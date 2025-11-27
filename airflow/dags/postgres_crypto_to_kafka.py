from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime
from kafka import KafkaProducer
import json
import os


def postgres_crypto_to_kafka():

    # --- 1) Read rows from Postgres ---
    pg = PostgresHook(postgres_conn_id="crypto_prices")   # <-- اصلاح مهم
    records = pg.get_records("""
        SELECT id, date, time, time_unix, name_en, name_fa, price, 
               price_toman, change_percent, market_cap, link_icon, category
        FROM crypto_prices
    """)

    if not records:
        print("No records found in crypto_prices")
        return

    # --- 2) Kafka Producer config ---
    bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
    topic_name = os.getenv("KAFKA_TOPIC", "crypto_prices")

    producer = KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        retries=5
    )

    # --- 3) Send each row to Kafka ---
    for row in records:
        crypto_msg = {
            "id": row[0],
            "date": row[1],
            "time": row[2],
            "time_unix": row[3],
            "name_en": row[4],
            "name_fa": row[5],
            "price": float(row[6]) if row[6] is not None else None,
            "price_toman": row[7],
            "change_percent": row[8],
            "market_cap": row[9],
            "link_icon": row[10],
            "category": row[11]
        }

        producer.send(topic_name, crypto_msg)

    producer.flush()
    print(f" ✔ Sent {len(records)} records to Kafka topic → {topic_name}")


with DAG(
    dag_id="postgres_crypto_to_kafka",
    start_date=datetime(2025, 11, 20),
    schedule_interval="*/1 * * * *",
    catchup=False,
    tags=["postgres", "kafka", "crypto"]
) as dag:

    export_task = PythonOperator(
        task_id="export_crypto_prices",
        python_callable=postgres_crypto_to_kafka
    )
