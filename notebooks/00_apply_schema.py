# Databricks notebook source
# MAGIC %md
# MAGIC # 00 - Schema Enforcer
# MAGIC **Digital Realty - Lakehouse Schema Evolution Demo**
# MAGIC
# MAGIC Reads the Schema Registry and ensures the Lakehouse matches.
# MAGIC - Creates missing tables
# MAGIC - Adds missing columns (ALTER TABLE)
# MAGIC - Detects schema drift (extra columns added via UI)
# MAGIC
# MAGIC **Run this BEFORE data ingestion notebooks.**

# COMMAND ----------

# Import schema definitions from the registry
import runpy
import pathlib

# Execute the registry script and load SCHEMAS and SCHEMA_VERSION
_registry_path = pathlib.Path(__file__).parent / "00_schema_registry.py"
registry = runpy.run_path(str(_registry_path))
SCHEMAS = registry.get("SCHEMAS")
SCHEMA_VERSION = registry.get("SCHEMA_VERSION")

# COMMAND ----------

from pyspark.sql.types import *

# COMMAND ----------

# MAGIC %md
# MAGIC ## Schema Enforcement Engine

# COMMAND ----------

class SchemaEnforcer:
    """Compares expected schemas against actual Lakehouse tables and applies changes."""

    def __init__(self, schemas, version):
        self.schemas = schemas
        self.version = version
        self.actions = []

    def enforce_all(self):
        """Enforce all schemas from the registry."""
        print(f"Schema Enforcer v{self.version}")
        print("=" * 60)
        print(f"Checking {len(self.schemas)} table definitions...\n")

        for table_name, schema_def in self.schemas.items():
            self._enforce_table(table_name, schema_def)

        self._print_summary()

    def _enforce_table(self, table_name, schema_def):
        """Enforce schema for a single table."""
        if not spark.catalog.tableExists(table_name):
            self._create_table(table_name, schema_def)
            return

        existing_fields = {f.name: f.dataType.simpleString()
                          for f in spark.table(table_name).schema.fields}
        expected_columns = schema_def["columns"]

        missing_columns = []
        for col_name, col_type, nullable in expected_columns:
            if col_name not in existing_fields:
                missing_columns.append((col_name, col_type))

        if missing_columns:
            self._add_columns(table_name, missing_columns)
        else:
            print(f"  OK  {table_name} -- schema matches registry")
            self.actions.append(("OK", table_name, "Schema matches"))

        # Detect drift: columns in Lakehouse but NOT in registry
        expected_names = {c[0] for c in expected_columns}
        extra_columns = set(existing_fields.keys()) - expected_names
        if extra_columns:
            print(f"  DRIFT  {table_name} -- extra columns not in registry: {extra_columns}")
            self.actions.append(("DRIFT", table_name, f"Extra columns: {extra_columns}"))

    def _create_table(self, table_name, schema_def):
        """Create a table that does not exist yet."""
        columns_sql = ", ".join(
            f"{c[0]} {c[1]}" + ("" if c[2] else " NOT NULL")
            for c in schema_def["columns"]
        )
        ddl = f"CREATE TABLE {table_name} ({columns_sql}) USING DELTA"

        if schema_def.get("partition_by"):
            partitions = ", ".join(schema_def["partition_by"])
            ddl += f" PARTITIONED BY ({partitions})"

        spark.sql(ddl)
        print(f"  CREATED  {table_name} -- {len(schema_def['columns'])} columns")
        self.actions.append(("CREATED", table_name, f"{len(schema_def['columns'])} columns"))

    def _add_columns(self, table_name, columns):
        """Add missing columns to an existing table."""
        for col_name, col_type in columns:
            spark.sql(f"ALTER TABLE {table_name} ADD COLUMNS ({col_name} {col_type})")
            print(f"  ADDED  {table_name}.{col_name} ({col_type})")
            self.actions.append(("ADDED", table_name, f"{col_name} {col_type}"))

    def _print_summary(self):
        """Print enforcement summary."""
        created = sum(1 for a in self.actions if a[0] == "CREATED")
        added = sum(1 for a in self.actions if a[0] == "ADDED")
        ok = sum(1 for a in self.actions if a[0] == "OK")
        drift = sum(1 for a in self.actions if a[0] == "DRIFT")

        print("\n" + "=" * 60)
        print(f"Schema Enforcement Complete (v{self.version})")
        print(f"  Tables created:  {created}")
        print(f"  Columns added:   {added}")
        print(f"  Tables OK:       {ok}")
        print(f"  Drift detected:  {drift}")
        print("=" * 60)

        if drift > 0:
            print("\nWARNING: Schema drift detected. Review the extra columns above.")
            print("These columns exist in the Lakehouse but are NOT in the schema registry.")
            print("Either add them to 00_schema_registry.py or remove them from the Lakehouse.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Run Schema Enforcement

# COMMAND ----------

enforcer = SchemaEnforcer(SCHEMAS, SCHEMA_VERSION)
enforcer.enforce_all()
