from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timedelta
import requests
import json

API_URL = "https://BrsApi.ir/Api/Market/Cryptocurrency.php?key=your_api_key"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 OPR/106.0.0.0",
    "Accept": "application/json, text/plain, */*"
}


def fetch_and_store_prices():
    response = requests.get(API_URL, headers=HEADERS)

    if response.status_code != 200:
        raise Exception(f"API ERROR: {response.status_code} - {response.text}")

    data = response.json()

    pg_hook = PostgresHook(postgres_conn_id="crypto_prices")
    conn = pg_hook.get_conn()
    cursor = conn.cursor()

    insert_query = """
        INSERT INTO crypto_prices 
        (date, time, time_unix, name_en, name_fa, price, price_toman, change_percent, market_cap, link_icon, category)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    for item in data:

        price_raw = item.get("price", "0")
        price_toman_raw = item.get("price_toman", "0")

        # --- تبدیل امن ---
        try:
            price = float(price_raw)
        except:
            price = None

        try:
            price_toman = int(float(price_toman_raw))
        except:
            price_toman = None

        cursor.execute(insert_query, (
            item.get("date"),
            item.get("time"),
            item.get("time_unix"),
            item.get("name_en"),
            item.get("name"),
            price,
            price_toman,
            item.get("change_percent"),
            item.get("market_cap"),
            item.get("link_icon"),
            item.get("category"),
        ))

    conn.commit()
    cursor.close()
    conn.close()


default_args = {
    "owner": "mamali",
    "retries": 2,
    "retry_delay": timedelta(seconds=20)
}

with DAG(
    dag_id="crypto_fetch_price",
    default_args=default_args,
    start_date=datetime(2025, 11, 20),
    schedule_interval="*/1 * * * *",
    catchup=False,
    tags=["crypto", "price"],
) as dag:

    task_fetch_and_store = PythonOperator(
        task_id="fetch_crypto_prices",
        python_callable=fetch_and_store_prices
    )
