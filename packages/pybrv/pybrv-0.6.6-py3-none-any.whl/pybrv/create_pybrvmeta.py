from pyspark.sql import SparkSession

class DatabricksPybrvmeta:
    def __init__(self, spark: SparkSession):
        self.spark = spark.getActiveSession()

    def setup_pybrv_meta(self, database: str):
        """
        Create database, 'pybrv_meta' schema, and required tables for business rule validation metadata.
        """
        
        # Create database and schema
        self.spark.sql(f"CREATE SCHEMA IF NOT EXISTS {database}.pybrv_meta")

        # Drop if exists
        self.spark.sql(f"DROP TABLE IF EXISTS {database}.pybrv_meta.pybrv_business_rule_check_result")
        self.spark.sql(f"DROP TABLE IF EXISTS {database}.pybrv_meta.pybrv_data_parity_result")
        self.spark.sql(f"DROP TABLE IF EXISTS {database}.pybrv_meta.pybrv_metadata")
        self.spark.sql(f"DROP TABLE IF EXISTS {database}.pybrv_meta.pybrv_unique_rule_mapping")
        self.spark.sql(f"DROP TABLE IF EXISTS {database}.pybrv_meta.pydpc_attribute_mismatch_details")
        self.spark.sql(f"DROP TABLE IF EXISTS {database}.pybrv_meta.pydpc_attribute_result")
        self.spark.sql(f"DROP TABLE IF EXISTS {database}.pybrv_meta.pydpc_attribute_stats")
        self.spark.sql(f"DROP TABLE IF EXISTS {database}.pybrv_meta.pydpc_attribute_summary")
        self.spark.sql(f"DROP TABLE IF EXISTS {database}.pybrv_meta.pydpc_record_results")
        self.spark.sql(f"DROP TABLE IF EXISTS {database}.pybrv_meta.pydpc_rule_summary")
        self.spark.sql(f"DROP TABLE IF EXISTS {database}.pybrv_meta.sgp_test_result")

        # Create tables
        self.spark.sql(f"""
        CREATE TABLE {database}.pybrv_meta.pybrv_business_rule_check_result (
            unique_rule_identifier BIGINT,
            execution_id BIGINT,
            team_name STRING,
            rule_name STRING,
            data_domain STRING,
            table_checked STRING,
            severity STRING,
            rule_category STRING,
            bookmark_column_name STRING,
            bookmark_start_date DATE,
            bookmark_end_date DATE,
            status STRING,
            pass_record_count INT,
            fail_record_count INT,
            pass_percentage INT,
            threshold INT,
            failed_keys STRING,
            failed_query STRING,
            test_case_comments STRING,
            remarks STRING,
            last_modified_ts TIMESTAMP 
        )
        USING DELTA
        """)

        self.spark.sql(f"""
        CREATE TABLE {database}.pybrv_meta.pybrv_data_parity_result (
            unique_rule_identifier BIGINT,
            execution_id BIGINT,
            rule_name STRING,
            data_domain STRING,
            table_checked STRING,
            bookmark_column_name STRING,
            bookmark_column_value DATE,
            join_key_values STRING,
            metric_dim_values STRING,
            attribute_name STRING,
            attribute_value INT,
            comments STRING,
            last_modified_ts TIMESTAMP 
        )
        USING DELTA
        """)

        self.spark.sql(f"""
        CREATE TABLE {database}.pybrv_meta.pybrv_metadata (
            unique_rule_identifier BIGINT NOT NULL,
            bookmark_start_date DATE,
            bookmark_end_date DATE,
            last_modified_ts TIMESTAMP
        )
        USING DELTA
        """)

        self.spark.sql(f"""
        CREATE TABLE {database}.pybrv_meta.pybrv_unique_rule_mapping (
            unique_rule_identifier BIGINT NOT NULL,
            team_name STRING,
            data_domain STRING,
            rule_category STRING,
            rule_id INT,
            rule_name STRING,
            last_modified_ts TIMESTAMP 
        )
        USING DELTA
        """)

        self.spark.sql(f"""
        CREATE TABLE {database}.pybrv_meta.pydpc_attribute_mismatch_details (
            unique_rule_identifier BIGINT,
            execution_id BIGINT,
            rule_name STRING,
            data_domain STRING,
            table_name STRING,
            bookmark_column_name STRING,
            bookmark_column_value STRING,
            join_key_values MAP<STRING, STRING>,
            metric_dim_values MAP<STRING, STRING>,
            mismatch_type STRING,
            column_mismatch_flags MAP<STRING, STRING>,
            source_values MAP<STRING, STRING>,
            target_values MAP<STRING, STRING>,
            mismatched_columns STRING,
            comments STRING,
            last_modified_ts TIMESTAMP
        )
        USING DELTA
        """)

        self.spark.sql(f"""
        CREATE TABLE {database}.pybrv_meta.pydpc_attribute_result (
            execution_id BIGINT,
            unique_rule_identifier BIGINT,
            data_domain STRING,
            team_name STRING,
            inventory STRING,
            tool_name STRING,
            test_case_type STRING,
            test_name STRING,
            execution_datetime TIMESTAMP,
            gpid STRING,
            test_execution_link STRING,
            status INT,
            remarks STRING,
            bookmark_column_name STRING,
            bookmark_start_date DATE,
            bookmark_end_date DATE,
            metadata STRING,
            last_modified_ts TIMESTAMP,
            pos STRING 
        )
        USING DELTA
        """)


        self.spark.sql(f"""
        CREATE TABLE {database}.pybrv_meta.pydpc_attribute_stats (
            execution_id BIGINT,
            unique_rule_identifier BIGINT,
            data_domain STRING,
            rule_name STRING,
            table_checked STRING,
            execution_date DATE,
            key_date_column STRING,
            key_date_value DATE,
            field_name STRING,
            comments STRING,
            source_records BIGINT,
            target_records BIGINT,
            target_rows_matched BIGINT,
            source_attribute_count BIGINT,
            target_attribute_count BIGINT 
        )
        USING DELTA
        """)


        self.spark.sql(f"""
        CREATE TABLE {database}.pybrv_meta.pydpc_attribute_summary (
            data_domain STRING,
            rule_name STRING,
            table_name STRING,
            field_name STRING,
            source_total_records STRING,
            target_total_records STRING,
            target_attribute_found STRING,
            attributes_matched_perc STRING,
            threshold STRING,
            execution_id BIGINT,
            unique_rule_identifier BIGINT
        )
        USING DELTA
        """)

        self.spark.sql(f"""
        CREATE TABLE {database}.pybrv_meta.pydpc_record_results (
            unique_rule_identifier BIGINT,
            execution_id BIGINT,
            rule_name STRING,
            data_domain STRING,
            table_name STRING,
            bookmark_column_name STRING,
            bookmark_column_value DATE,
            join_key_values STRING,
            metric_dim_values STRING,
            attribute_name STRING,
            attribute_value BIGINT,
            comments STRING,
            last_modified_ts TIMESTAMP
        )
        USING DELTA
        """)


        self.spark.sql(f"""
        CREATE TABLE {database}.pybrv_meta.pydpc_rule_summary (
            start_date STRING,
            end_date STRING,
            data_domain STRING,
            rule_name STRING,
            table_name STRING,
            status STRING,
            source_records STRING,
            target_found STRING,
            percent_records_found STRING,
            target_rows_matched STRING,
            percent_rows_matched STRING,
            attributes_checked STRING,
            attributes_matched STRING,
            comments STRING,
            execution_id BIGINT,
            unique_rule_identifier BIGINT 
        )
        USING DELTA
        """)

        self.spark.sql(f"""
        CREATE TABLE {database}.pybrv_meta.sgp_test_result (
            id INT,
            data_domain STRING,
            team_name STRING,
            inventory STRING,
            tool_name STRING,
            test_case_type STRING,
            test_name STRING,
            execution_datetime TIMESTAMP,
            gpid STRING,
            test_execution_link STRING,
            status INT,
            remarks STRING,
            bookmark_column_name STRING,
            bookmark_start_date DATE,
            bookmark_end_date DATE,
            metadata STRING,
            last_modified_ts TIMESTAMP,
            pos STRING 
        )
        USING DELTA
        """)


   
        print(f"✅ All tables in `{database}.pybrv_meta` created successfully.")
