from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
import pymysql
import pandas as pd
from dotenv import load_dotenv
import os
from datetime import datetime
from langchain_openai import ChatOpenAI
from sql.order_sql import order_sql_query
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
def get_order_data(query: str) -> Dict[str, str]:
    """Get order data from the database and save as CSV file."""
    print('_'*100)
    print(query)
    print('_'*100)

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


    
