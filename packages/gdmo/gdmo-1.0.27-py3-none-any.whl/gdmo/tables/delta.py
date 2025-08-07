import re
import datetime as dt

class Delta:

    """
        A class for creating and managing Delta tables in Azure Databricks.

        Attributes:
        - db_name (str): Required. The name of the database containing the table.
        - table_name (str): Required. The name of the table.
        - spark (pyspark.sql.SparkSession): Required. The SparkSession object to use for interacting with the table.
        - columns (list of dictionaries): Optional. A list of dictionaries, where each dictionary contains the column name, data type, and an optional comment.
        - options (dict): Optional. A dictionary containing the table options.
        - primary_key (str): Optional. The name of the primary key column.
        - partitioning (str): Optional. The name of the partitioning column.
        - identity (str): Optional. The name of the identity integer column that contains an auto-incremental number.

        Methods:
        - set_columns(columns): Sets the column list for the table.
        - set_comment(comment): Sets the comment for the table.
        - set_options(options): Sets the options for the table.
        - set_primary_key(primary_key): Sets the primary key for the table.
        - set_foregin_key(primary_key): Sets the primary key for the table.
        - set_partitioning(partitioning): Sets the partitioning for the table.
        - add_column(column_name, data_type, comment): Adds a single column to the table.
        - drop_existing(): Drops the existing table and removes it from the ADFS file system.
        - describe(): Returns a DataFrame object containing the description of the table.

    """
    def __init__(self, db_name, table_name, spark, catalog = 'default', container = 'default'):
        """
        Initializes a DeltaTable object with the specified database name, table name, and SparkSession object.

        Args:
        - db_name (str): Required. The name of the database containing the table.
        - table_name (str): Required. The name of the table.
        - spark (pyspark.sql.SparkSession): Required. The SparkSession object to use for interacting with the table.
        """
        # Check if the database exists
        databases = [db.name for db in spark.catalog.listDatabases()]
        if db_name not in databases and db_name != 'pytest':
            raise ValueError(f"Database {db_name} not found in the SparkSession.")

        # Check if the table name is valid
        if not re.match(r'^[a-zA-Z0-9_]+$', table_name):
            raise ValueError(f"Invalid table name: {table_name}. Table names can only contain alphanumeric characters and underscores.")

        self._catalog = catalog
        self._db_name = db_name
        self._table_name = table_name
        self._spark = spark
        self._columns = []
        self._table_location = ''   # Table location is empty by default. needs to be set.
        self._identity = None       # Default the table is created without auto-increment identity column. 
        self._options = {}
        self._primary_key = None
        self._partitioning = None
        self._foreignkeys = []
        self._table_path = f"{self._catalog}.{self._db_name}.{self._table_name}"
        self._comment = None
          
    def set_columns(self, columns):
        """
        Sets the column list for the table.

        Args:
        - columns (list of dictionaries): Required. A list of dictionaries, where each dictionary contains the column name, data type, and an optional comment.

        Returns:
        - self (DeltaTable): Returns the DeltaTable object.
        """
        # Check if columns is a list of dictionaries
        if not isinstance(columns, list) or not all(isinstance(col, dict) for col in columns):
            raise ValueError("The columns argument must be a list of dictionaries.")

        # Check if each dictionary in columns contains the required keys
        for col in columns:
            if not all(key in col for key in ["name", "data_type"]):
                raise ValueError("Each dictionary in the columns argument must contain the 'name' and 'data_type' keys.")

        # Add blank comments if not present in the dictionary
        for col in columns:
            if "comment" not in col:
                col["comment"] = ""

        # Check if 'DbxCreated', 'DbxUpdated', and 'IsDeleted' columns are present
        required_columns = ['DbxCreated', 'DbxUpdated', 'IsDeleted']
        existing_columns = [col['name'] for col in columns]
        missing_columns = [col for col in required_columns if col not in existing_columns]

        # Append the missing columns as the first three columns
        for col_name in reversed(missing_columns):
            columns.insert(0, {"name": col_name, "data_type": "timestamp" if col_name in ['DbxCreated', 'DbxUpdated'] else "int", "comment": ""})

        self._columns = columns
        return self

    def get_columns(self):
        return self._columns
        
    def set_comment(self, manual_comment, primary_keys = None, foreign_keys = None, load_config = None, upstream_dependencies = None) -> None:
        """
            Builds a detailed, prettified table comment string summarizing table structure, keys, relationships, partitioning, and data sources.

            Args:
                manual_comment (str): User-provided comment.
                load_config (dict): Load configuration metadata.
                upstream_dependencies (list): List of upstream source tables.

            Returns:
                self
        """
        lines = []

        # Table Name
        lines.append(f"Table Name: {self._table_path}")

        # Description
        if manual_comment:
            lines.append(f"\nDescription: {manual_comment}")
        else:
            lines.append(f"\nDescription: Table {self._table_path} created by Delta class.")

        # Primary Keys and Standard Key Columns
        if primary_keys:
            lines.append("\nPrimary Keys:")
            for c in primary_keys:
                # Use the first sentence of the comment as a summary
                comment = c.get("comment", "").split(".")[0]
                lines.append(f"- {c['name']}: {comment.strip()}")
        
        # Foreign keys
        if foreign_keys:
            lines.append("\nForeign Keys:")
            for fk in foreign_keys:
                lines.append(
                    f"- {fk['name']}: (from {fk['sourcecolumn']} to {fk['table']}.{fk['targetcolumn']})"
                )

        # Data Loaded From
        if upstream_dependencies:
            src_str = ", ".join(
                [f"{src['Table']} (Required: {src.get('Required', False)})" for src in upstream_dependencies]
            )
            lines.append(f"\nData Loaded From the following dependencies: {src_str}")
        elif load_config and "source" in load_config:
            lines.append(f"\nData Loaded From: {load_config['source']}")

        # Columns
        lines.append(f"\nColumns (Total: {len(self._columns)}) total occurance in other gold-level tables as of {dt.datetime.now()}:")
        for c in self._get_column_gold_count():
            lines.append(f'- {c["column_name"]}: {c["col_count"]} tables in {c["catalog_count"]} catalogs')


        self._comment = "\n".join(lines)
        return self

    def get_comment(self):
        return self._comment

    def set_options(self, options):
        """
        Sets the options for the table.

        Args:
        - options (dict): Required. A dictionary containing the table options.

        Returns:
        - None
        """
        self._options = options
        return self

    def get_options(self):
        return self._options
        
    def set_location(self, location):
        """
        Set the location of the table.

        Parameters:
        - location (str): The location where the table will be stored.

        Raises:
        - ValueError: If the location is not a non-empty string.
        """
        if not isinstance(location, str) or not location.strip():
            raise ValueError("The 'location' parameter must be a non-empty string.")

        self._table_location = location

        return self

    def get_location(self):
        return self._table_location
    
    def set_partitioning(self, partitioning):
        """
        Sets the partitioning for the table.

        Args:
        - partitioning (str): Required. The name of the partitioning column.

        Returns:
        - None
        """
        self._partitioning = partitioning
        return self

    def get_partitioning(self):
        return self._partitioning
    
    def set_primary_key(self, keyname, coll):
      """
        Sets the primary key for the table.

        Args:
        - keyname (str): Required. The name of the primary key constraint.
        - coll (str): Required. The column of the primary key.

        Returns:
        - self
      """

      # Check if the keyname already exists as a primary key constraint
      existing_key_query = f'''
          SELECT constraint_name
          FROM information_schema.table_constraints
          WHERE table_schema = '{self._db_name}'
          AND table_name = '{self._table_name}'
          AND constraint_type = 'PRIMARY KEY'
      '''
      
      existing_keys = self._spark.sql(existing_key_query).collect()

      if existing_keys:
        existing_key_names = [key["constraint_name"] for key in existing_keys]
        raise ValueError(f"Table {self._db_name}.{self._table_name} already has a primary key constraint(s) called {existing_key_names}.")

      if ',' in coll:
        # we have a string of multiple columns.
        for col in coll.split(','):
            try:
                self.alter_column(col.strip(), 'SET NOT NULL')
            except Exception as e:
                raise ValueError(f"Failed to set {col.strip()} to SET NOT NULL: {e}.")
      else:
        try:
            self.alter_column(coll.strip(), 'SET NOT NULL')
        except Exception as e:
            raise ValueError(f"Failed to set {coll.strip()} to SET NOT NULL: {e}.")
          

      try:
          # Add the primary key constraint to the table
          self._spark.sql(f'''
              ALTER TABLE {self._db_name}.{self._table_name}
              ADD CONSTRAINT {keyname} PRIMARY KEY ({coll})
          ''')
          self._spark.sql(f'''
              ALTER TABLE {self._db_name}.{self._table_name}
              SET TBLPROPERTIES('primary_key' = '{coll}')
          ''')
          
      except Exception as e:
          raise ValueError(f"Error adding primary key constraint: {e}")

      return self
        
    def set_foreign_keys(self, keys = None) -> str:
        """
        Adds a foreign key constraint to the created table. Expects input as a list of dicts like this: [{'name': 'name', 'columns': 'columns', 'table': 'table'}]
        
        Args:
        - keys (list): list of dictionaries containing all FKs to be created.
        
        Returns:
        - str: Success message listing all constraints that were successfully created.
        """
        self._foreignkeys = keys

        error_msg = 'Not all required datapoints are present. The input to this function needs to be shaped like this: [{\'name\': \'name\', \'sourcecolumn\': \'sourcecolumn\',\'targetcolumn\': \'targetcolumn\', \'table\': \'table\'}]'

        if not isinstance(keys, list):
                raise ValueError(error_msg)

        created_constraints = []

        for key in keys:
            if not isinstance(key, dict):
                raise ValueError('The key must be a dictionary containing the following keys: name, columns, table')
            if 'name' in key and 'sourcecolumn' in key and 'targetcolumn' in key and 'table' in key:
                if 'included_for_lineage_only' not in key:
                    # Check if the constraint already exists
                    existing_constraints = self._spark.sql(f"""
                        SELECT constraint_name
                        FROM information_schema.table_constraints
                        WHERE table_schema = '{self._db_name}'
                        AND table_name = '{self._table_name}'
                        AND constraint_type = 'FOREIGN KEY'
                        AND constraint_name = '{key['name']}'
                    """).collect()

                    if existing_constraints:
                        print(f"Foreign key constraint '{key['name']}' already exists on the table.")
                        continue

                    stmt = f"""
                            ALTER TABLE {self._catalog}.{self._db_name}.{self._table_name} 
                            ADD CONSTRAINT {key['name']}
                            FOREIGN KEY({key['sourcecolumn']}) REFERENCES {key['table']} ({key['targetcolumn']});
                    """
                    try:
                        self._spark.sql(stmt)
                        created_constraints.append(key['name'])
                    except Exception as e:
                        raise ValueError(f'Failed to set Foreign key: {stmt}. Error: {e}')
            else:
                raise ValueError(error_msg)
        
        if created_constraints:
            if len(created_constraints) == 1:
                return f"Foreign key constraint '{created_constraints[0]}' was successfully created."
            else:
                return f"Foreign key constraints successfully created: {', '.join(created_constraints)}"
        else:
            return "No new foreign key constraints were created."

    def set_identity(self, col):
        """
        Sets the specified column as an identity column with a primary key attached.

        Parameters:
        - col (str): The name of the column to be set as an identity column.

        Returns:
        - Delta: The updated Delta object with the specified column set as an identity column.

        Notes:
        - This function sets the specified column as an identity column with a primary key attached in the Delta table creation.
        """
        self._identity = col
        
        return self

    def get_identity(self):
        return self._identity

    def add_column(self, column):
        """
            Adds a column to the table.

            Args:
            - column (dict): Required. A dictionary containing the column name, data type, and comment.

            Returns:
            - self
        """
        # Check if the column is in the right format
        if not isinstance(column, dict) or not all(key in column for key in ["name", "data_type", "comment"]):
            raise ValueError("The column argument must be a dictionary with 'name', 'data_type', and 'comment' keys.")

        # Check if the column name is at least 3 characters long
        if len(column["name"].strip()) < 3:
            raise ValueError("The 'name' value in the column argument must be at least 3 characters long.")

        # Check if the comment is not identical to the column name
        if column["name"].strip().lower() == column["comment"].strip().lower():
            raise ValueError("The 'comment' value in the column argument must not be identical to the column name.")

        # Check if the comment is at least 10 characters long
        if len(column["comment"].strip()) < 10:
            raise ValueError("The 'comment' value in the column argument must be at least 10 characters long.")
        
        # Check if the column already exists in the table
        existing_columns = [col["name"] for col in self._columns]
        if column["name"] in existing_columns:
            raise ValueError(f"The column '{column['name']}' already exists in the table.")

        # Alter the table to add the column
        alter_table_query = f"ALTER TABLE {self._catalog}.{self._db_name}.{self._table_name} ADD COLUMN {column['name']} {column['data_type']} COMMENT '{column['comment']}'"
        self._spark.sql(alter_table_query)

        # Add the column to the list of columns
        self._columns.append(column)

        return self
    
    def alter_column(self, col, option):
      """
        Alters a column in the table by setting options like SET NOT NULL or DATATYPE.

        Args:
        - col (str): The name of the column to be altered.
        - option (str): The alteration option, such as SET NOT NULL or DATATYPE.

        Returns:
        - self
      """  

      if 'NOT NULL' in option or 'DATATYPE' in option:
          # Get the list of column names
          cols = self._spark.sql(f"SHOW COLUMNS IN {self._catalog}.{self._db_name}.{self._table_name}").collect()
          col_names = [c['col_name'] for c in cols]

          if col in col_names:
              try:
                  # Use ALTER TABLE to modify the column
                  self._spark.sql(f"""
                      ALTER TABLE {self._catalog}.{self._db_name}.{self._table_name}
                      ALTER COLUMN {col} {option}
                  """)
                  return self
              except Exception as e:
                  raise ValueError(f'Failed to alter column {col}: {e}')
          else:
              raise ValueError(f'Column {col} does not exist in the table.')
      else:
          raise ValueError('Invalid option provided. Allowed options: SET NOT NULL, DATATYPE')
                  
    def drop_existing(self):
        """
        Drops the existing table and removes it from the ADFS file system.

        Returns:
        - None
        """
        
        try:
            drop_sql_str = f"DROP TABLE IF EXISTS {self._db_name}.{self._table_name}"
            self._spark.sql(drop_sql_str)
                        
            dbutils = self._get_dbutils()

            dbutils.fs.rm(self._table_location, True)
            return self
        except Exception as e:
            print(f'Error during Table Drop: {e}')
            return False
            
    def create_table(self):
        """
        Saves the table to the specified database.

        Returns:
        - None
        """
        columns = []
        identity_column_found = False

        for col in self._columns:
            col_str = f"{col['name'].replace(' ','')} {col['data_type']} COMMENT '{col['comment']}'"
            
            if 'extra_clause' in col:
                col_str += f" {col['extra_clause']}"
            
            if self._identity is not None and col['name'] == self._identity:
                if col['data_type'].lower() in ['int', 'bigint']:
                    col_str += " GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY"
                    identity_column_found = True
                else:
                    raise ValueError(f"The identity column '{self._identity}' must be of type 'int' or 'bigint'. The selected column is of type '{col['data_type']}'.")
            
            columns.append(col_str)

        if self._identity is not None and not identity_column_found:
            raise ValueError(f"The specified identity column '{self._identity}' is not present in the column list set by set_columns().")

        columns_str = ", ".join(columns)
        
        options = ", ".join([f"{key} = '{value}'" for key, value in self._options.items()])
        partitioning = f"PARTITIONED BY ({self._partitioning})" if self._partitioning else ""
        table_comment = f'COMMENT "{self._comment}"' if self._comment else ""
        
        create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {self._catalog}.{self._db_name}.{self._table_name} (
                {columns_str}
            )
            USING DELTA
            location "{self._table_location}"
            {partitioning}
            {options}
            {table_comment}
        """
        try:
            self._spark.sql(create_table_query)
            print(f"Table {self._catalog}.{self._db_name}.{self._table_name} created successfully.")
            return self
          
        except Exception as e:
            if "Table already exists" in str(e):
                existing_table_desc = self._spark.sql(f"describe detail {self._db_name}.{self._table_name}").toPandas()
                existing_table_desc_str = "\n".join([f"{row['col_name']}\t{row['data_type']}\t{row['comment']}" for _, row in existing_table_desc.iterrows()])
                error_msg = f"Table {self._db_name}.{self._table_name} already exists. Please add the 'drop_existing()' function to the create statement if you want to overwrite the existing table.\n\nExisting table description:\n{existing_table_desc_str}"
            else:
                error_msg = f"Error during table save: {e}"
            raise Exception(error_msg)

    def describe(self):
        """
        Returns a DataFrame object containing the description of the table.

        Returns:
        - df (pyspark.sql.DataFrame): A DataFrame object containing the description of the table.
        """
        describe_sql_str = f"DESCRIBE DETAIL {self._catalog}.{self._db_name}.{self._table_name}"

        try:
            # Execute the describe SQL command
            desc = self._spark.sql(describe_sql_str)
        except Exception as e:
            return f'Error during table describe: {e}' 

        return desc

    def add_blank_record(self, filler='Unknown') -> None:
        """
        Adds a blank record to the table with the specified filler value.
        If the table contains an identity column, its value is set to -1.

        Args:
        - filler (str): Optional. The filler value to be used for the blank record. Defaults to 'Unknown'.

        Returns:
        - self
        """
    
        # Get the schema of the table
        table = self._spark.table(f"{self._catalog}.{self._db_name}.{self._table_name}")
        schema = table.schema
        blank_record = {}
        identity_col = self._identity


        # Iterate over each field in the schema to construct the blank record
        for field in schema.fields:
            dtype = field.dataType.typeName()
            if (identity_col and field.name == identity_col) or (field.name[3:] == 'Key'):
                blank_record[field.name] = -1  # Set identity column to -1
            elif dtype == 'string':
                blank_record[field.name] = filler  # Set string fields to filler value
            elif dtype in ('int', 'integer', 'bigint', 'long', 'short', 'byte'):
                blank_record[field.name] = 0  # Set numeric fields to 0
            elif dtype in ('float', 'double', 'decimal'):
                blank_record[field.name] = 0.0  # Set float fields to 0.0
            elif dtype == 'boolean':
                blank_record[field.name] = False  # Set boolean fields to False
            elif dtype in ('timestamp', 'date'):
                blank_record[field.name] = '1900-01-01'  # Set timestamp and date fields to None
            else:
                blank_record[field.name] = None  # Set other fields to None

        # Prepare columns and values for the SQL insert statement
        columns = []
        values = []
        for col, val in blank_record.items():
            columns.append(col)
            if val is None:
                values.append("NULL")
            elif isinstance(val, str):
                escaped_val = val.replace("'", "''")
                values.append(f"'{escaped_val}'")
            elif isinstance(val, bool):
                values.append("TRUE" if val else "FALSE")
            else:
                values.append(str(val))

        # Construct and execute the SQL insert statement
        columns_str = ", ".join(columns)
        values_str = ", ".join(values)
        insert_sql = f"INSERT INTO {self._catalog}.{self._db_name}.{self._table_name} ({columns_str}) VALUES ({values_str})"
        try:
            self._spark.sql(insert_sql)
            print(f"Blank record added to {self._catalog}.{self._db_name}.{self._table_name} with filler '{filler}'.")

        except Exception as e:
            print(f"Blank record addition failed. SQL: {insert_sql}: {e}")

        return self

    def _get_column_gold_count(self):
        """
        Returns the number of columns in the table that are in the gold schema.
        """
        try:
            col_str = ", ".join([f"'{c['name']}'" for c in self._columns])
            # Use a raw string for the LIKE pattern to avoid invalid escape sequence warnings
            sql = f'''
                    SELECT  t.column_name, 
                            COUNT(DISTINCT t.table_catalog) catalog_count,
                            COUNT(DISTINCT t.table_catalog || '.' || t.table_schema || '.' || t.table_name) AS col_count
                    FROM    system.information_schema.columns t
                    WHERE   t.column_name IN ({col_str})
                      AND   t.table_catalog LIKE '{self._catalog}%'
                      AND   t.table_schema = 'gold'
                      AND   (t.table_name != '{self._table_name}' and t.table_catalog != '{self._catalog}')
                    GROUP BY t.column_name
            '''
            return [row.asDict() for row in self._spark.sql(sql).collect()]
        except Exception as e:
            print(f"Error in _get_column_gold_count: {e}")
            return []

    def _get_dbutils(self):
        """
        Private function to get a dbutils instance available allowing the drop_existing function to drop a table from ADLS

        Returns:
        - dbutils object
        """
        dbutils = None
        
        if self._spark.conf.get("spark.databricks.service.client.enabled") == "true":
            
            from pyspark.dbutils import DBUtils
            dbutils = DBUtils(self._spark)
        
        else:
            
            import IPython
            dbutils = IPython.get_ipython().user_ns["dbutils"]
        
        return dbutils
