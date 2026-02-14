import sys
import os
from sqlalchemy import create_engine, text, inspect
import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Connection strings
# Source: stockstewardai
SOURCE_URL = "postgresql://neondb_owner:npg_Y5IfRBbmS2FW@ep-delicate-poetry-ahi4kvos-pooler.c-3.us-east-1.aws.neon.tech/stockstewardai?sslmode=require"
# Destination: emr
DEST_URL = "postgresql://neondb_owner:npg_Y5IfRBbmS2FW@ep-delicate-poetry-ahi4kvos-pooler.c-3.us-east-1.aws.neon.tech/emr?sslmode=require"

def migrate_emr():
    try:
        source_engine = create_engine(SOURCE_URL)
        dest_engine = create_engine(DEST_URL)
        
        # 1. Ensure 'emr' schema exists in destination
        with dest_engine.connect().execution_options(isolation_level="AUTOCOMMIT") as dest_conn:
            dest_conn.execute(text("CREATE SCHEMA IF NOT EXISTS emr"))
            logger.info("Checked/Created 'emr' schema in destination database.")

        # 2. Get list of tables in source 'emr' schema
        inspector = inspect(source_engine)
        tables = inspector.get_table_names(schema='emr')
        logger.info(f"Found {len(tables)} tables to migrate: {tables}")

        for table_name in tables:
            try:
                logger.info(f"Migrating table: {table_name}")
                
                # 3. Read data from source
                df = pd.read_sql_table(table_name, source_engine, schema='emr')
                row_count_source = len(df)
                logger.info(f"  - Read {row_count_source} rows from source (emr.{table_name}).")

                # 4. Write data to destination
                # Use if_exists='replace' to ensure schema matches DataFrame
                df.to_sql(table_name, dest_engine, schema='emr', if_exists='replace', index=False)
                logger.info(f"  - Wrote data to {table_name} in destination (emr database).")

                # 5. Verify row counts
                with dest_engine.connect() as dest_conn:
                    res = dest_conn.execute(text(f"SELECT count(*) FROM emr.{table_name}"))
                    row_count_dest = res.scalar()
                    if row_count_source == row_count_dest:
                        logger.info(f"  - SUCCESS: Row counts match ({row_count_dest}).")
                    else:
                        logger.error(f"  - FAILURE: Row counts mismatch! Source: {row_count_source}, Dest: {row_count_dest}")
            except Exception as e:
                logger.error(f"  - ERROR migrating {table_name}: {e}")
                # Log column types to see if there's anything unusual
                # df.dtypes is available here
                logger.info(f"  - Column types: {df.dtypes.to_dict()}")

        logger.info("Migration complete.")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    migrate_emr()
