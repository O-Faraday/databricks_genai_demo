# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "2"
# ///
# MAGIC %md
# MAGIC
# MAGIC ## SETUP — Generate source CSV and land it in the Unity Catalog Volume
# MAGIC Run this notebook ONCE before starting the pipeline.
# MAGIC
# MAGIC What it does:
# MAGIC - Writes 5 new orders (including one "awaiting" + missing order_date) as a CSV file to /Volumes/demo/demo/raw_data/
# MAGIC
# MAGIC Re-run it any time you want to simulate a new set of orders arriving in the Volume.

# COMMAND ----------

# MAGIC %md
# MAGIC Load the catalog & schema and create the volume if not exist

# COMMAND ----------

# MAGIC %run ../_config/config_unity_catalog

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Create the volume if it doesn't exist yet
# MAGIC CREATE VOLUME IF NOT EXISTS raw_orders
# MAGIC COMMENT 'Landing zone for raw order CSV files consumed by the ingestion pipeline';

# COMMAND ----------

# MAGIC %md
# MAGIC Create the csv of new orders

# COMMAND ----------

from pyspark.sql.types import (
    StructType, StructField,
    IntegerType, StringType, DoubleType
)

VOLUME_PATH = f"/Volumes/{catalog}/{schema}/raw_orders"

# 5 source orders:
#   • order_id 2004 → status  = "awaiting"  (intentionally invalid)
#   • order_date will be modified in silver
source_orders = [
    (2001, 1, None,  "processing",   150.00, "10 Rue de Rivoli, Paris"),
    (2002, 2, None,  "processing",      89.99, "5 Av. Montaigne, Paris"),
    (2003, 3, None,   "processing",    220.50, "8 Rue du Faubourg, Lyon"),
    (2004, 4, None,  "awaiting",      45.00, "22 Cours Mirabeau, Aix"),
    (2005, 5, None,  "processing",  310.75, "3 Place Bellecour, Lyon"),
]

schema = StructType([
    StructField("order_id",         IntegerType(), False),
    StructField("customer_id",      IntegerType(), False),
    StructField("order_date",       StringType(),  True),
    StructField("status",           StringType(),  False),
    StructField("total_amount",     DoubleType(),  False),
    StructField("shipping_address", StringType(),  True),
])

df = spark.createDataFrame(source_orders, schema)

# Write as a single CSV file with header
# mode="append" → each run drops a new file; Auto Loader will pick it up
(df.coalesce(1)
   .write
   .mode("append")
   .option("header", "true")
   .csv(VOLUME_PATH))

print(f"Source CSV written to {VOLUME_PATH}")
display(df)
