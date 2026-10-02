"""
db.py
Loads cleaned sales data into a local SQLite database and provides
SQL query functions used by the dashboard and the AI layer.

Using SQLite keeps the project zero-config (no server to install) while
still demonstrating real SQL skills - all aggregation here is done with
SQL, not pandas, on purpose.
"""

import os
import sqlite3
import pandas as pd

DB_PATH = "data/sales.db"
TABLE_NAME = "sales"


def ensure_db_exists():
    """Ensure data/sales.db exists on disk. If not, generate data, clean it, and load SQLite."""
    if not os.path.exists(DB_PATH) or os.path.getsize(DB_PATH) == 0:
        print(f"Database {DB_PATH} not found. Running data pipeline initialization...")
        os.makedirs("data", exist_ok=True)
        
        # 1. Generate raw data if missing
        if not os.path.exists("data/raw_sales.csv"):
            import generate_data
            generate_data.main() if hasattr(generate_data, "main") else None
            
        # 2. Clean data if missing
        if not os.path.exists("data/clean_sales.csv"):
            import clean_data
            clean_data.main() if hasattr(clean_data, "main") else None
            
        # 3. Load to SQLite
        load_to_sqlite()


def load_to_sqlite(csv_path: str = "data/clean_sales.csv", db_path: str = DB_PATH):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    df = pd.read_csv(csv_path, parse_dates=["order_date"])
    conn = sqlite3.connect(db_path)
    df.to_sql(TABLE_NAME, conn, if_exists="replace", index=False)
    conn.close()
    print(f"Loaded {len(df)} rows into {db_path} (table: {TABLE_NAME})")


def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    ensure_db_exists()
    return sqlite3.connect(db_path)


def run_query(sql: str, params: tuple = ()) -> pd.DataFrame:
    conn = get_connection()
    try:
        return pd.read_sql_query(sql, conn, params=params)
    finally:
        conn.close()


# ---------------------------------------------------------------------
# Reusable KPI queries. Each returns a small pandas DataFrame.
# ---------------------------------------------------------------------

def total_kpis() -> pd.DataFrame:
    sql = """
    SELECT
        ROUND(SUM(revenue), 2) AS total_revenue,
        ROUND(SUM(profit), 2) AS total_profit,
        COUNT(DISTINCT order_id) AS total_orders,
        ROUND(AVG(revenue), 2) AS avg_order_value,
        ROUND(SUM(profit) * 1.0 / SUM(revenue), 4) AS overall_margin
    FROM sales;
    """
    return run_query(sql)


def revenue_by_month() -> pd.DataFrame:
    sql = """
    SELECT year_month, ROUND(SUM(revenue), 2) AS revenue, ROUND(SUM(profit), 2) AS profit
    FROM sales
    GROUP BY year_month
    ORDER BY year_month;
    """
    return run_query(sql)


def revenue_by_product() -> pd.DataFrame:
    sql = """
    SELECT product, category,
           ROUND(SUM(revenue), 2) AS revenue,
           ROUND(SUM(profit), 2) AS profit,
           SUM(quantity) AS units_sold
    FROM sales
    GROUP BY product, category
    ORDER BY revenue DESC;
    """
    return run_query(sql)


def revenue_by_region() -> pd.DataFrame:
    sql = """
    SELECT region, ROUND(SUM(revenue), 2) AS revenue, ROUND(SUM(profit), 2) AS profit
    FROM sales
    GROUP BY region
    ORDER BY revenue DESC;
    """
    return run_query(sql)


def product_month_over_month() -> pd.DataFrame:
    """Used to detect which products are growing or declining."""
    sql = """
    SELECT product, year_month, ROUND(SUM(revenue), 2) AS revenue
    FROM sales
    GROUP BY product, year_month
    ORDER BY product, year_month;
    """
    df = run_query(sql)
    return df


def latest_two_months_comparison() -> pd.DataFrame:
    sql = """
    WITH months AS (
        SELECT DISTINCT year_month FROM sales ORDER BY year_month DESC LIMIT 2
    )
    SELECT s.year_month, ROUND(SUM(s.revenue), 2) AS revenue
    FROM sales s
    JOIN months m ON s.year_month = m.year_month
    GROUP BY s.year_month
    ORDER BY s.year_month;
    """
    return run_query(sql)


if __name__ == "__main__":
    load_to_sqlite()
    print(total_kpis())
    print(revenue_by_month().tail())
