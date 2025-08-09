import os
import io
import logging
from typing import Tuple, Optional
import pandas as pd
import sqlalchemy
from langchain_openai import ChatOpenAI
from langchain_community.utilities.sql_database import SQLDatabase
from langchain.chains import create_sql_query_chain

def text_to_sql_and_export(
    natural_language_query: str,
    openai_api_key: str,
    db_engine: sqlalchemy.engine.Engine
) -> Optional[Tuple[io.BytesIO, io.BytesIO]]:
    """
    Converts a natural language query to SQL, executes it, and returns the result
    as an in-memory Excel file and the SQL script as an in-memory text file.

    Args:
        natural_language_query: The user's question in plain English.
        openai_api_key: Your OpenAI API key.
        db_engine: An initialized SQLAlchemy engine connected to the target database.

    Returns:
        A tuple containing two in-memory file objects (BytesIO):
        1. excel_buffer: The query results in an Excel format.
        2. sql_buffer: The generated SQL script in a text format (for logging).
        Returns (None, None) if an error occurs.
    """
    try:
        # --- 1. Set up Environment and LLM ---
        os.environ["OPENAI_API_KEY"] = openai_api_key
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        db = SQLDatabase(
            engine=db_engine,
            # Specify tables for the LLM to consider for better accuracy
            include_tables=['products', 'orders'],
            sample_rows_in_table_info=2
        )

        # --- 2. Generate SQL Query ---
        logging.info("Generating SQL query from natural language...")
        query_chain = create_sql_query_chain(llm, db)
        sql_query = query_chain.invoke({"question": natural_language_query})

        # Clean up query in case the LLM wraps it in markdown
        if "```sql" in sql_query:
            sql_query = sql_query.replace("```sql\n", "").replace("\n```", "").strip()
        
        logging.info(f"Generated SQL Query:\n{sql_query}")

        # --- 3. Execute Query and Fetch Data ---
        logging.info("Executing SQL query...")
        with db_engine.connect() as connection:
            result_df = pd.read_sql_query(sqlalchemy.text(sql_query), connection)
        logging.info(f"Query executed successfully, fetched {len(result_df)} rows.")

        # --- 4. Create In-Memory Excel File from DataFrame ---
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            result_df.to_excel(writer, sheet_name='Query_Result', index=False)
        excel_buffer.seek(0)  # Rewind buffer to the beginning

        # --- 5. Create In-Memory Text File for SQL Log ---
        sql_buffer = io.BytesIO()
        # Write the SQL query string, encoded to bytes, into the buffer
        sql_buffer.write(sql_query.encode('utf-8'))
        sql_buffer.seek(0)  # Rewind buffer

        return excel_buffer, sql_buffer

    except Exception as e:
        # Log the full error with traceback for easier debugging
        logging.error(f"An error occurred in the text-to-SQL process: {e}", exc_info=True)
        return None, None
