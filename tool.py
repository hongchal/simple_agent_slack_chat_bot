from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
import pymysql
import pandas as pd
from dotenv import load_dotenv
import os
from datetime import datetime
from langchain_openai import ChatOpenAI
from sql.order_sql import order_sql_query
from sql.pre_shippped import pre_shipped_sql_query
from sql.cm_sql import cm_sql_query
from typing import Dict

load_dotenv()

search_tool = DuckDuckGoSearchRun()
llm = ChatOpenAI(model="gpt-4o")

@tool
def get_today_date() -> str:
    """Get today's date"""
    return datetime.now().strftime("%Y-%m-%d")

@tool
def nl_to_order_sql(nl_query: str) -> str:
    """Convert a natural language query to an SQL query for the order DB."""

    prompt = f"""
    You are an expert SQL developer.
    Convert the following natural language request into a valid SQL query for our order database.
    
    order_sql_query = f'{order_sql_query}'
    Natural language: {nl_query}
    """
    
    sql_query = llm.invoke(prompt)

    return sql_query

@tool
def nl_to_pre_shipped_sql(nl_query: str) -> str:
    """Convert a natural language query to an SQL query for the pre-shipped DB."""
    prompt = f"""
    You are an expert SQL developer.
    Convert the following natural language request into a valid SQL query for our pre-shipped database.
    
    pre_shipped_sql_query = f'{pre_shipped_sql_query}'
    Natural language: {nl_query}
    """

    sql_query = llm.invoke(prompt)

    return sql_query

@tool
def nl_to_cm_sql(nl_query: str) -> str:
    """Convert a natural language query to an SQL query for the cm(contribution margin) DB."""
    prompt = f"""
    You are an expert SQL developer.
    Convert the following natural language request into a valid SQL query for our cm(ontribution margin) database.

    cm_sql_query = f'{cm_sql_query}'
    Natural language: {nl_query}
    """

    sql_query = llm.invoke(prompt)
    return sql_query

@tool
def get_data_from_db(query: str) -> Dict[str, str]:
    """Get data from the database and save as CSV file."""

    remote = pymysql.connect(
        host=os.getenv("DATABASE_HOST"),
        port=int(os.getenv("DATABASE_PORT")),
        user=os.getenv("DATABASE_USER"),
        password=os.getenv("DATABASE_PASSWORD"),
        database=os.getenv("DATABASE_NAME"),
        charset='utf8'
    )

    cur = remote.cursor()
    cur.execute(query)

    rows = cur.fetchall()
    columns = [col[0] for col in cur.description]
    target_df = pd.DataFrame(rows, columns=columns)

    result_dir = './results'
    os.makedirs(result_dir, exist_ok=True)
    filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    path = os.path.abspath(os.path.join(result_dir, filename))
    target_df.to_csv(path, index=False, encoding="cp949")

    return {"file_path": path}

