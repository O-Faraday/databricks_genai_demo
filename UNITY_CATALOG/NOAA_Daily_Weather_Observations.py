# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "2"
# ///
# MAGIC %md
# MAGIC # 🌤️ Daily Weather Observations — NOAA (GHCNd)
# MAGIC **Provider:** Rearc ·  **Runtime:** DBR 16.4 LTS (Spark 3.5.2, Python 3.11)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1- Setup

# COMMAND ----------

import requests
from io import StringIO
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pyspark.sql import functions as F
from pyspark.sql.types import FloatType

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2- Load from Delta Sharing

# COMMAND ----------

df_raw = spark.table("rearc_daily_weather_observations_noaa.esg_noaa_ghcn.noaa_ghcn_daily")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3- Prepare data

# COMMAND ----------

df_clean = (
    df_raw
    .select("station", "date", "precipitation", "precipitation_attrs", "latitude", "longitude", "name")
    .withColumn("year",  F.year("date"))
    .withColumn("month", F.month("date"))
    .withColumn("day",   F.dayofmonth("date"))
    .withColumn("value", F.col("precipitation")/10.)
    .withColumn("unity", F.lit("mm"))
    .withColumn("rainy_day", F.when(F.col("value") > 5., 1).otherwise(0))
    .withColumnRenamed("station",      "station_id")
    .filter(F.col("year") == 2023)
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4- Filter station
# MAGIC You can get the list of weather stations :https://noaa-ghcn-pds.s3.amazonaws.com/ghcnd-stations.txt
# MAGIC We will use as reference the following stations.

# COMMAND ----------

CITY_STATIONS = {
    "San-Francisco": "USW00023234",
    "New-Orleans": "USW00012916",
    "Washington":  "USW00013743",
}
#Cities list
CITIES = list(CITY_STATIONS.keys())

df_station = (
    df_clean
    .filter(F.col("station_id").isin(list(CITY_STATIONS.values())))
    .withColumn(
        "city",
        F.create_map(*[item for pair in
            [(F.lit(sid), F.lit(city)) for city, sid in CITY_STATIONS.items()]
            for item in pair
        ])[F.col("station_id")]
    )
    .groupBy("city", "station_id", "year", "month")
    .agg(F.sum("rainy_day").alias("rainy_days"))
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5-  Rainy Days > 5 mm per Month — 2024
# MAGIC
# MAGIC Count of days per month where daily precipitation exceeded **5 mm**,
# MAGIC

# COMMAND ----------

import seaborn as sns
 
MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
 
pdf = df_station.toPandas()
pdf["month_label"] = pd.Categorical(
    pdf["month"].apply(lambda m: MONTHS[m - 1]),
    categories=MONTHS, ordered=True
)
 
fig, ax = plt.subplots(figsize=(14, 6))
sns.barplot(data=pdf, x="month_label", y="rainy_days", hue="city", ax=ax)
ax.set(xlabel="Month", ylabel="Days with precipitation > 5 mm",
       title=f"🌧️ Rainy Days (> 5 mm) per Month — 2023\n{CITIES}")
ax.legend(title="City")
sns.despine()
display(fig)
plt.close(fig)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6- Try genie with the following question
# MAGIC for the year 2023, represent in a bar chart the number of days per month where precipitation exceeded 50 (i.e. 5 mm, since values are stored in tenths of mm) for the following stations: USW00023234 (San-Francisco), USW00012916 (New-Orleans), and USW00013743 (Washington). Group results by station and month, and display city names instead of station IDs.
