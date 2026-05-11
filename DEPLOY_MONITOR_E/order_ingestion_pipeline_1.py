# =============================================================================
# Lakeflow Spark Declarative Pipeline — Order Ingestion with Auto Loader
# Target: demo.demo.order_features  (existing Delta table, CDF enabled)
# =============================================================================
# Pipeline flow:
#
#   /Volumes/demo/demo/raw_orders/  (CSV files)
#     └─► BRONZE  : bronze_orders_raw         @dp.table  (streaming, Auto Loader)
#           └─► SILVER  : silver_orders_enriched   @dp.table  (streaming)
#                 ├─► SINK    : demo.demo.order_features   dp.create_sink
#                 │             + @dp.append_flow
#                 └─► MV      : mv_order_status_summary    @dp.materialized_view
#
# Prerequisites:
#   1. Run generate_source_orders_0.py to create the Volume raw_orders and land the CSV.
#   2. demo.demo.orders_feature exists with CDF enabled.
#   3. Pipeline default catalog = demo, default schema = demo.
# =============================================================================

from pyspark import pipelines as dp
from pyspark.sql.functions import col, when, current_date, count, round as fround
from pyspark.sql.functions import sum as fsum
from pyspark.sql.types import (
    StructType, StructField,
    IntegerType, StringType, DoubleType
)
catalog="demo"
schema="demo"
# Volume path where the setup notebook lands CSV files
VOLUME_PATH = f"/Volumes/{catalog}/{schema}/raw_orders/"

# Explicit schema — always prefer explicit over inferred in production
# to avoid type mismatches when new files arrive.
_SOURCE_SCHEMA = StructType([
    StructField("order_id",         IntegerType(), False),
    StructField("customer_id",      IntegerType(), False),
    StructField("order_date",       StringType(),  True),   # nullable — may be missing
    StructField("status",           StringType(),  False),
    StructField("total_amount",     DoubleType(),  False),
    StructField("shipping_address", StringType(),  True),
])


# =============================================================================
# BRONZE — Auto Loader ingestion from the Unity Catalog Volume
#
# cloudFiles (Auto Loader) tracks which files have already been processed
# using an internal checkpoint managed by the pipeline.
# Each new CSV file dropped in VOLUME_PATH is picked up automatically
# on the next pipeline run — no manual tracking needed.
# =============================================================================

@dp.table(
    comment="Bronze: incremental CSV ingestion from /Volumes/demo/demo/raw_orders/ "
            "via Auto Loader. Raw data, no transformation. "
            "Each file is processed exactly once.",
    table_properties={"quality": "bronze"}
)
def bronze_orders_raw():
    return (
        spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "csv")
        .option("header", "true")
        # Schema location is managed automatically by the SDP pipeline —
        # no need to set cloudFiles.schemaLocation manually.
        .schema(_SOURCE_SCHEMA)
        .load(VOLUME_PATH)
    )


# =============================================================================
# SILVER — Enrichment: backfill null order_date with today's date
#
# Reads bronze as a stream so new records flow through end-to-end
# without requiring a full recompute of the table.
# =============================================================================

@dp.table(
    comment="Silver: order_date backfilled with current_date() where null. "
            "All other columns pass through unchanged.",
    table_properties={"quality": "silver"}
)
def silver_orders_enriched():
    """
    Fills in the missing order_date for any row where it was not provided
    in the source file. current_date() resolves at pipeline run time.
    """
    return (
        spark.readStream.table("bronze_orders_raw")
        .withColumn(
            "order_date",
            when(col("order_date").isNull(), current_date().cast(StringType()))
            .otherwise(col("order_date"))
        ).withColumn(
            "orders_feature_id",
            col("order_id")
        )
    )


# =============================================================================
# SINK — Register demo.demo.orders_feature as an external Delta sink
#
# The pipeline does NOT own this table. Full refreshes do not clear it.
# All appends are tracked via CDF on the target table.
# =============================================================================

dp.create_sink(
    "order_features_sink",
    "delta",
    {"tableName": f"demo.demo.orders_feature"}
)


# =============================================================================
# APPEND FLOW — Stream silver records into demo.demo.orders_feature
#
# Because bronze and silver are now proper streaming tables (Auto Loader),
# once=True is no longer needed: the pipeline naturally processes only
# new records on each run (incremental, exactly-once semantics).
# =============================================================================
 
@dp.append_flow(
    target="order_features_sink",
    name="append_new_orders",
    comment="Stream enriched silver records into demo.demo.orders_feature. "
            "New files in the Volume are picked up automatically on each pipeline run."
)
def append_new_orders():
    """
    Reads silver_orders_enriched as a stream and appends to the sink.
    Each order — including any row with status 'returned' or a backfilled
    order_date — is written once to demo.demo.orders_feature.
    """
    return spark.readStream.table("silver_orders_enriched")

# =============================================================================
# MATERIALIZED VIEW — Order summary by status
#
# Reads from silver with batch semantics. Recomputed incrementally
# when silver_orders_enriched receives new data.
# =============================================================================

@dp.materialized_view(
    comment="Aggregated view: order count and total revenue per status. "
            "Surfaces invalid statuses (e.g. 'returned') alongside valid ones.",
    table_properties={"quality": "gold"}
)
def mv_order_status_summary():
    return (
        spark.read.table("silver_orders_enriched")
        .groupBy("status")
        .agg(
            count("order_id").alias("order_count"),
            fround(fsum("total_amount"), 2).alias("total_revenue")
        )
        .orderBy(col("order_count").desc())
    )
