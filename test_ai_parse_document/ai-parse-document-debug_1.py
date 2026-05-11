# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "2"
# ///
# MAGIC %md
# MAGIC # AI parse document debug interface
# MAGIC
# MAGIC The DocumentRenderer Class is extracted from a databricks tutorial.
# MAGIC [official Databricks documentation](https://docs.databricks.com/aws/en/sql/language-manual/functions/ai_parse_document)
# MAGIC
# MAGIC ## Overview
# MAGIC This notebook provides a **visual interface** for analyzing the output of Databricks' `ai_parse_document` function. It renders parsed documents with interactive bounding box overlays, allowing you to inspect what content was extracted from each region of your documents.
# MAGIC
# MAGIC ## Features
# MAGIC - **Visual bounding boxes**: Color-coded overlays showing the exact regions where text/elements were detected
# MAGIC - **Interactive tooltips**: Hover over any bounding box to see the parsed content from that region
# MAGIC - **Element type visualization**: Different colors for different element types (text, headers, tables, figures, etc.)
# MAGIC
# MAGIC ## Required parameters
# MAGIC
# MAGIC This interface requires two Unity Catalog (UC) volume paths to be configured:
# MAGIC
# MAGIC ### 1. `source_files` 
# MAGIC - **Description**: Path to the list of documents in the UC volume you want to parse and visualize
# MAGIC - **Example**: `/Volumes/catalog/schema/volume/source_files`
# MAGIC
# MAGIC ### 2. `image_output_path`
# MAGIC - **Description**: Path to a writeable UC volume where `ai_parse_document` will store the extracted page images
# MAGIC - **Example**: `/Volumes/catalog/schema/volume/parsed_images/`
# MAGIC - **Requirements**: Write access required for storing intermediate image outputs
# MAGIC

# COMMAND ----------

# MAGIC %run ../_config/config_unity_catalog

# COMMAND ----------

# MAGIC %run ./document_renderer

# COMMAND ----------

import json, re
import time
from datetime import datetime
from html.parser import HTMLParser
from pyspark.sql import functions as F
from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType,
    BooleanType, DoubleType, FloatType
)
volume="raw_data"
# ── Paths ───────────────────────────────────────────────────────────────────
PATH_VOLUME  = f"/Volumes/{catalog}/{schema}/{volume}"
PATH_IMAGES  = f"/Volumes/{catalog}/{schema}/{volume}/parsed_images"
PATH_RESULTS = f"/Volumes/{catalog}/{schema}/{volume}/parse_results"
PATH_OUTPUT= f"/Volumes/{catalog}/{schema}/{volume}/output"
dbutils.fs.mkdirs(PATH_OUTPUT)

# COMMAND ----------

# DBTITLE 1,Configuration parameters

#   Parse page selection string and return list of page indices to display.
#    
source_files = {
    "Invoice_jpg"           : "multiformat/Invoice.jpg",
    "AccidentStatement_pdf" : "multiformat/AccidentStatement.pdf",
    "old_articles_pdf"      : "multiformat/old_articles.pdf",
}

print(f"Volume : {PATH_VOLUME}")
print(f"Files  : {list(source_files.values())}")
sources = [f"{PATH_VOLUME}/{source_name}" for source_name in source_files.values()]

# COMMAND ----------

# DBTITLE 1,Run document parse code (may take some time)
def parse_doc(source, output) : 
  # SQL statement with ai_parse_document()
  sql = f'''
  with parsed_documents AS (
    SELECT
      path,
      ai_parse_document(content
       ,
      map(
      'version', '2.0',
       'imageOutputPath', '{output}',
       'descriptionElementTypes', 'figure' 
      )
    ) as parsed
  FROM
    read_files('{source}', format => 'binaryFile')
  )
  select * from parsed_documents
  '''

  parsed_results = [row.parsed for row in spark.sql(sql).collect()]
  return parsed_results

# COMMAND ----------

# DBTITLE 1,Debug Visualization Results
for s in sources :
  parsed_results = parse_doc(s, PATH_OUTPUT)
  render_ai_parse_output_interactive(parsed_results)
