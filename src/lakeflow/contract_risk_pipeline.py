# Databricks notebook source
"""Lakeflow pipeline: synthetic landing JSON -> governed contract risk tables.

The bundle supplies ``landing_root`` as a pipeline configuration value.
All tables are published in the configured Unity Catalog catalog and schema.
"""

from pyspark import pipelines as dp
from pyspark.sql import functions as F
from pyspark.sql.types import LongType, StringType, StructField, StructType


LANDING_ROOT = spark.conf.get("landing_root")

AWARD_SCHEMA = StructType(
    [
        StructField("contract_id", StringType()),
        StructField("as_of_date", StringType()),
        StructField("agency", StringType()),
        StructField("vendor", StringType()),
        StructField("start_date", StringType()),
        StructField("end_date", StringType()),
        StructField("obligated_amount", LongType()),
        StructField("contract_type", StringType()),
        StructField("naics", StringType()),
        StructField("psc", StringType()),
        StructField("source_type", StringType()),
        StructField("_rescued_data", StringType()),
    ]
)

EXPENDITURE_SCHEMA = StructType(
    [
        StructField("contract_id", StringType()),
        StructField("as_of_date", StringType()),
        StructField("spend_month", StringType()),
        StructField("amount", LongType()),
        StructField("source_type", StringType()),
        StructField("_rescued_data", StringType()),
    ]
)


@dp.table(name="bronze_awards", comment="Raw synthetic award snapshots from the UC landing volume")
def bronze_awards():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("recursiveFileLookup", "true")
        .schema(AWARD_SCHEMA)
        .load(f"{LANDING_ROOT}/awards/")
    )


@dp.table(name="bronze_expenditures", comment="Raw synthetic monthly expenditures from the UC landing volume")
def bronze_expenditures():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("recursiveFileLookup", "true")
        .schema(EXPENDITURE_SCHEMA)
        .load(f"{LANDING_ROOT}/expenditures/")
    )


@dp.table(
    name="silver_awards",
    comment="Validated synthetic contract award snapshots; one row per contract and as-of date",
    table_properties={"delta.enableRowTracking": "true"},
)
@dp.expect_or_drop("valid_award", "contract_id IS NOT NULL AND as_of_date IS NOT NULL AND end_date >= start_date AND obligated_amount > 0 AND _rescued_data IS NULL")
def silver_awards():
    return (
        spark.readStream.table("bronze_awards")
        .withColumn("as_of_date", F.to_date("as_of_date"))
        .withColumn("start_date", F.to_date("start_date"))
        .withColumn("end_date", F.to_date("end_date"))
    )


@dp.table(
    name="silver_expenditures",
    comment="Validated synthetic monthly contract expenditures, distinct from obligations",
    table_properties={"delta.enableRowTracking": "true"},
)
@dp.expect_or_drop("valid_expenditure", "contract_id IS NOT NULL AND as_of_date IS NOT NULL AND spend_month IS NOT NULL AND spend_month <= as_of_date AND amount >= 0 AND _rescued_data IS NULL")
def silver_expenditures():
    return (
        spark.readStream.table("bronze_expenditures")
        .withColumn("as_of_date", F.to_date("as_of_date"))
        .withColumn("spend_month", F.to_date("spend_month"))
    )


@dp.materialized_view(
    name="gold_contract_risk",
    comment="Explainable contract review priority from obligations, synthetic expenditures, and expiration dates; score is not a loss probability",
)
@dp.expect_or_fail("funding_balances", "remaining_obligation >= 0")
def gold_contract_risk():
    awards = spark.read.table("silver_awards")
    expenditures = spark.read.table("silver_expenditures")
    month_begin = F.trunc(F.col("as_of_date"), "MM")
    recent = (
        (F.col("spend_month") >= F.add_months(month_begin, -3))
        & (F.col("spend_month") < month_begin)
    )
    totals = expenditures.groupBy("contract_id", "as_of_date").agg(
        F.sum("amount").alias("total_expenditures"),
        F.sum(F.when(recent, F.col("amount")).otherwise(F.lit(0))).alias("last_three_month_expenditures"),
    )
    base = (
        awards.join(totals, ["contract_id", "as_of_date"], "left")
        .drop("_rescued_data")
        .fillna({"total_expenditures": 0, "last_three_month_expenditures": 0})
        .withColumn("remaining_obligation", F.col("obligated_amount") - F.col("total_expenditures"))
        .withColumn("monthly_burn", F.round(F.col("last_three_month_expenditures") / F.lit(3.0), 2))
        .withColumn("days_to_expiration", F.datediff("end_date", "as_of_date"))
    )
    base = base.withColumn(
        "projected_spend_to_end",
        F.round(F.col("monthly_burn") * F.greatest(F.col("days_to_expiration"), F.lit(0)) / F.lit(30.44), 2),
    )
    underutilization = (
        (F.col("days_to_expiration") <= 90)
        & (F.col("remaining_obligation") >= 1_000_000)
        & (F.col("projected_spend_to_end") < F.col("remaining_obligation") * 0.5)
    )
    exhaustion = (
        (F.col("days_to_expiration") > 30)
        & (F.col("remaining_obligation") > 0)
        & (F.col("projected_spend_to_end") > F.col("remaining_obligation") * 1.1)
    )
    return (
        base.withColumn(
            "risk_type",
            F.when(exhaustion, "funding_exhaustion")
            .when(underutilization, "underutilization")
            .when(F.col("days_to_expiration") <= 90, "watch")
            .otherwise("none"),
        )
        .withColumn(
            "risk_priority_score",
            F.when(F.col("risk_type") == "funding_exhaustion", 90)
            .when(F.col("risk_type") == "underutilization", 85)
            .when(F.col("risk_type") == "watch", 30)
            .otherwise(10),
        )
        .withColumn(
            "risk_level",
            F.when(F.col("risk_priority_score") >= 85, "HIGH")
            .when(F.col("risk_priority_score") >= 30, "MEDIUM")
            .otherwise("LOW"),
        )
        .withColumn(
            "projected_shortfall",
            F.round(F.greatest(F.col("projected_spend_to_end") - F.col("remaining_obligation"), F.lit(0)), 2),
        )
    )
