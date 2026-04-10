-- Fabric notebook source

-- METADATA ********************

-- META {
-- META   "kernel_info": {
-- META     "name": "synapse_pyspark"
-- META   },
-- META   "dependencies": {
-- META     "lakehouse": {
-- META       "default_lakehouse": "11fedcf0-74de-4d96-88c2-9a171434c078",
-- META       "default_lakehouse_name": "DataCenterLakehouse",
-- META       "default_lakehouse_workspace_id": "ffb373f3-c810-453a-b598-badb52dfd152",
-- META       "known_lakehouses": [
-- META         {
-- META           "id": "11fedcf0-74de-4d96-88c2-9a171434c078"
-- META         }
-- META       ]
-- META     }
-- META   }
-- META }

-- CELL ********************

-- Welcome to your new notebook
-- Type here in the cell editor to add code!
CREATE TABLE year_2017.green_tripdata_2017_clone_20260408
AS SELECT * FROM year_2017.green_tripdata_2017;

CREATE TABLE year_2018.green_tripdata_2018_backup_2018 AS
SELECT * FROM year_2018.green_tripdata_2018;

SELECT COUNT(*) FROM lakehouse.<table>_backup_YYYYMMDD;

-- METADATA ********************

-- META {
-- META   "language": "sparksql",
-- META   "language_group": "synapse_pyspark"
-- META }

-- CELL ********************

ALTER TABLE dbo.green_tripdata_2017 ADD COLUMNS (perm_check_tmp STRING);
DESCRIBE TABLE dbo.green_tripdata_2017;
ALTER TABLE dbo.green_tripdata_2017 DROP COLUMN perm_check_tmp;

-- METADATA ********************

-- META {
-- META   "language": "sparksql",
-- META   "language_group": "synapse_pyspark"
-- META }

-- CELL ********************

SHOW DATABASES;
SHOW TABLES IN year_2017;

-- METADATA ********************

-- META {
-- META   "language": "sparksql",
-- META   "language_group": "synapse_pyspark"
-- META }

-- CELL ********************

ALTER TABLE year_2017.green_tripdata_2017 ADD COLUMNS (new_col STRING);
DESCRIBE TABLE year_2017.green_tripdata_2017;

-- METADATA ********************

-- META {
-- META   "language": "sparksql",
-- META   "language_group": "synapse_pyspark"
-- META }

-- CELL ********************

ALTER TABLE year_2017.green_tripdata_2017 ADD COLUMNS (new_col1 STRING);
DESCRIBE TABLE year_2017.green_tripdata_2017;

-- METADATA ********************

-- META {
-- META   "language": "sparksql",
-- META   "language_group": "synapse_pyspark"
-- META }

-- CELL ********************

DESCRIBE TABLE year_2017.green_tripdata_2017;

-- METADATA ********************

-- META {
-- META   "language": "sparksql",
-- META   "language_group": "synapse_pyspark"
-- META }
