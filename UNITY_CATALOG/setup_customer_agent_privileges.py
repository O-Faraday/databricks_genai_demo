# Databricks notebook source
# MAGIC %md
# MAGIC # Customer Agent - Service Principal Setup
# MAGIC
# MAGIC This notebook sets up privileges on catalog `demo` and schema `demo`:
# MAGIC    - READ access to tables ending with "feature"
# MAGIC    - EXECUTE access to functions (for model inference)
# MAGIC

# COMMAND ----------

# MAGIC %pip install databricks-sdk==0.55.0 unitycatalog-ai[databricks]
# MAGIC # Restart to load the packages into the Python environment
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1- Create the Group and Service Principal
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC Already created through the web console

# COMMAND ----------

group_name = "cust_group"
sp_display_name = "sp_cust_agent"

# COMMAND ----------

# MAGIC %md
# MAGIC Load the catalog 'demo' and schema 'demo' of the project UC.

# COMMAND ----------

# MAGIC %run ../_config/config_unity_catalog

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2- Grant Catalog and Schema Privileges

# COMMAND ----------

# Grant USE CATALOG privilege on demo catalog
spark.sql(f"GRANT USE CATALOG ON CATALOG {catalog} TO `{group_name}`")
print(f"Granted USE CATALOG on {catalog} to {group_name}")

# Privileges granted to the  schema level, to be able to create models from the mlflow log.
privileges = [
    "USE SCHEMA",
    "CREATE TABLE",
    "CREATE MODEL",
    "CREATE MODEL VERSION"
]

for privilege in privileges:
    spark.sql(f"GRANT {privilege} ON SCHEMA {catalog}.{schema} TO `{group_name}`")
    print(f"Granted {privilege} on '{catalog}.{schema}' to {group_name}")


# COMMAND ----------

# MAGIC %md
# MAGIC ## 3- Grant SELECT on Tables Ending with "feature"

# COMMAND ----------

# Get all tables in demo.demo schema
tables_df = spark.sql(f"SHOW TABLES IN `{catalog}`.`{schema}`")
display(tables_df)

# COMMAND ----------

# Get list of tables ending with 'feature' and grant SELECT privilege
tables_df = spark.sql(f"SHOW TABLES IN `{catalog}`.`{schema}`")
feature_tables = tables_df.filter(tables_df.tableName.endswith('feature')).collect()

print(f"Found {len(feature_tables)} tables ending with 'feature':")
print()

for row in feature_tables:
    table_name = row.tableName
    print(f"Processing table: {table_name}")
    
    # Grant SELECT privilege on each feature table
    spark.sql(f"GRANT SELECT ON TABLE `{catalog}`.`{schema}`.`{table_name}` TO `{group_name}`")
    print(f"Granted SELECT privilege on {table_name}")

print()


# COMMAND ----------

# MAGIC %md
# MAGIC ## 4- Grant EXECUTE on All Functions in demo.demo

# COMMAND ----------

# List all functions in the schema
from unitycatalog.ai.core.databricks import DatabricksFunctionClient

client = DatabricksFunctionClient()
f_names = [f.name for f in client.list_functions(catalog=catalog, schema=schema)]

# Grant EXECUTE on each function
for function_name in f_names:
    spark.sql(
        f"GRANT EXECUTE ON FUNCTION `{function_name}` TO `{group_name}`"
    )
    print(
        f"Granted EXECUTE on  functions in {function_name}  to {group_name}"
    )

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5- Grant Access to Vector Search Resources

# COMMAND ----------

# MAGIC %md
# MAGIC ### Grant privileges on the Vector Search Index

# COMMAND ----------

# Grant SELECT privilege on the vector search index
spark.sql(f"GRANT SELECT ON TABLE {catalog}.{schema}.pdf_document_raw_vs_index TO `{group_name}`")
print(f"Granted SELECT on vector search index 'pdf_document_raw_vs_index' to {group_name}")
