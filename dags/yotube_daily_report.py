from airflow.decorators import dag
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta
from io import StringIO
from google.cloud import storage
import pandas as pd
import os
from dotenv import load_dotenv
from include.scripts.youtube_fetcher import fetch_youtube_data


@dag(
    dag_id="youtube_data_pipeline_in_memory",
    start_date=days_ago(1),
    schedule_interval="@daily",
    catchup=False,
    tags=["youtube", "in_memory", "gcs"],
)
def youtube_data_pipeline_in_memory():

    def fetch_and_upload_to_gcs():
        load_dotenv()
        api_key = os.getenv("YOUTUBE_API_KEY")
        channel_id = "UCCuzDCoI3EUOo_nhCj4noSw"

        end_date = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
        start_date = (datetime.utcnow() - timedelta(days=1)).replace(
            microsecond=0
        ).isoformat() + "Z"

        df = fetch_youtube_data(api_key, channel_id, start_date, end_date)

        # Create CSV in memory
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)

        # Upload to GCS
        client = storage.Client()
        bucket = client.get_bucket("final-project-bucket-resource")
        timestamp = datetime.utcnow().strftime("%Y-%m-%d")
        blob_path = f"upload/youtube_data_{timestamp}.csv"

        blob = bucket.blob(blob_path)
        blob.upload_from_string(csv_buffer.getvalue(), content_type="text/csv")

        # Push GCS path to XCom
        return blob_path

    fetch_and_upload_task = PythonOperator(
        task_id="fetch_and_upload_to_gcs",
        python_callable=fetch_and_upload_to_gcs,
    )

    def get_gcs_uri(ti):
        blob_path = ti.xcom_pull(task_ids="fetch_and_upload_to_gcs")
        return f"gs://final-project-bucket-resource/{blob_path}"

    load_to_bq = BigQueryInsertJobOperator(
        task_id="load_to_bigquery",
        configuration=lambda context: {
            "load": {
                "sourceUris": [get_gcs_uri(context["ti"])],
                "destinationTable": {
                    "projectId": "fiery-catwalk-440706-k8",
                    "datasetId": "youtube_data_stream",
                    "tableId": "live_stream_stats",
                },
                "sourceFormat": "CSV",
                "skipLeadingRows": 1,
                "autodetect": True,
                "writeDisposition": "WRITE_TRUNCATE",
            }
        },
        gcp_conn_id="google_cloud_default",
        location="us-central1",
    )

    fetch_and_upload_task >> load_to_bq


youtube_data_pipeline_in_memory()
