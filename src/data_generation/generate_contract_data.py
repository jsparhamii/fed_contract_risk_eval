# Databricks notebook source
from datetime import date
from pyspark.sql import functions as F

dbutils.widgets.text("catalog", "")
dbutils.widgets.text("schema", "")
dbutils.widgets.text("volume", "")
dbutils.widgets.text("as_of_date", "2026-09-23")

catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
volume = dbutils.widgets.get("volume")
as_of = date.fromisoformat(dbutils.widgets.get("as_of_date"))
if any(not value or "/" in value for value in (catalog, schema, volume)):
    raise ValueError("Bundle-managed catalog, schema, and volume parameters are required")

volume_root = f"/Volumes/{catalog}/{schema}/{volume}"
as_of_column = F.lit(as_of.isoformat()).cast("date")
ids = spark.range(1, 49)
base = (
    ids.withColumn(
        "scenario",
        F.when(F.col("id") <= 12, "underutilization")
         .when(F.col("id") <= 24, "funding_exhaustion")
         .when(F.col("id") <= 36, "watch")
         .otherwise("none"),
    )
    .withColumn(
        "monthly_base",
        F.when(F.col("id") <= 12, 45_000 + F.col("id") * 1_000)
         .when(F.col("id") <= 24, 350_000 + (F.col("id") - 12) * 10_000)
         .when(F.col("id") <= 36, 150_000 + (F.col("id") - 24) * 3_000)
         .otherwise(120_000 + (F.col("id") - 36) * 5_000),
    )
    .withColumn(
        "remaining_amount",
        F.when(F.col("id") <= 12, 2_000_000 + (F.col("id") - 1) * 100_000)
         .when(F.col("id") <= 24, 180_000 + (F.col("id") - 13) * 20_000)
         .when(F.col("id") <= 36, 500_000 + (F.col("id") - 25) * 20_000)
         .otherwise(2_000_000 + (F.col("id") - 37) * 100_000),
    )
    .withColumn(
        "days_left",
        F.when(F.col("id") <= 12, 20 + (F.col("id") - 1) * 4)
         .when(F.col("id") <= 24, 90 + (F.col("id") - 13) * 5)
         .when(F.col("id") <= 36, 35 + (F.col("id") - 25) * 3)
         .otherwise(180 + (F.col("id") - 37) * 10),
    )
    .withColumn("contract_id", F.format_string("SYN-%04d", F.col("id")))
    .withColumn("as_of_date", as_of_column)
)

awards = base.select(
    "contract_id",
    "as_of_date",
    F.when(F.col("id") % 3 == 1, "Agency A")
     .when(F.col("id") % 3 == 2, "Agency B")
     .otherwise("Agency C").alias("agency"),
    F.when(F.col("id") % 4 == 1, "Northstar Systems")
     .when(F.col("id") % 4 == 2, "Pine Harbor Research")
     .when(F.col("id") % 4 == 3, "Civic Meridian")
     .otherwise("Blue Mesa Analytics").alias("vendor"),
    F.add_months(F.trunc("as_of_date", "MM"), -6).alias("start_date"),
    F.date_add("as_of_date", F.col("days_left").cast("int")).alias("end_date"),
    (F.col("remaining_amount") + F.col("monthly_base") * 6).cast("long").alias("obligated_amount"),
    F.when(F.col("id") % 2 == 1, "Firm Fixed Price")
     .otherwise("Time and Materials").alias("contract_type"),
    F.lit("541512").alias("naics"),
    F.lit("D399").alias("psc"),
    F.lit("synthetic_award").alias("source_type"),
)

expenditures = (
    base.crossJoin(spark.range(0, 6).withColumnRenamed("id", "month_index"))
    .select(
        "contract_id",
        "as_of_date",
        F.add_months(F.trunc("as_of_date", "MM"), F.col("month_index").cast("int") - 6).alias("spend_month"),
        (F.col("monthly_base") + ((F.col("month_index") % 3) - 1) * 5_000).cast("long").alias("amount"),
        F.lit("synthetic_expenditure").alias("source_type"),
    )
)

# Spark creates the dated folders. Re-running the same snapshot skips the existing files.
awards.coalesce(1).write.mode("ignore").json(f"{volume_root}/awards/{as_of.isoformat()}")
expenditures.coalesce(1).write.mode("ignore").json(f"{volume_root}/expenditures/{as_of.isoformat()}")

print(f"snapshot={as_of.isoformat()} awards={awards.count()} expenditures={expenditures.count()}")
for row in base.groupBy("scenario").count().orderBy("scenario").collect():
    print(f"{row.scenario}: {row['count']}")
