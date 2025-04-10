from airflow.decorators import dag
from airflow.operators.bash import BashOperator
from airflow.providers.google.cloud.transfers.local_to_gcs import (
    LocalFilesystemToGCSOperator,
)
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from airflow.utils.dates import days_ago


@dag(
    start_date=days_ago(1),
    schedule_interval=None,
    catchup=False,
    tags=["terraform", "bigquery"],
)
def terraform_then_upload_csv_to_bigquery():
    # Terraform init
    terraform_init = BashOperator(
        task_id="terraform_init",
        bash_command="cd include/terraform && terraform init",
    )

    # Terraform apply
    terraform_apply = BashOperator(
        task_id="terraform_apply",
        bash_command="cd include/terraform && terraform apply -auto-approve",
    )

    # Upload CSV to GCS
    upload_to_gcs = LocalFilesystemToGCSOperator(
        task_id="upload_csv",
        src="upload/marapthon_data.csv",
        dst="upload/marapthon_data.csv",
        bucket="final-project-bucket-resource",
        gcp_conn_id="google_cloud_default",
        mime_type="text/csv",
    )

    # Load CSV to BigQuery
    load_to_bigquery = BigQueryInsertJobOperator(
        task_id="load_to_bq",
        configuration={
            "load": {
                "sourceUris": [
                    "gs://final-project-bucket-resource/upload/marapthon_data.csv"
                ],
                "destinationTable": {
                    "projectId": "fiery-catwalk-440706-k8",
                    "datasetId": "youtube_data",
                    "tableId": "live_stream_stats",
                },
                "sourceFormat": "CSV",
                "skipLeadingRows": 1,
                "autodetect": True,
                "writeDisposition": "WRITE_TRUNCATE",
            }
        },
        gcp_conn_id="google_cloud_default",
    )

    # Task chaining
    terraform_init >> terraform_apply >> upload_to_gcs >> load_to_bigquery


terraform_then_upload_csv_to_bigquery()
