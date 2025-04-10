from airflow.decorators import dag
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago


@dag(schedule_interval=None, start_date=days_ago(1), catchup=False, tags=["terraform"])
def terraform_runner():

    terraform_init = BashOperator(
        task_id="terraform_init",
        bash_command="cd include/terraform && terraform init",
    )

    terraform_plan = BashOperator(
        task_id="terraform_plan",
        bash_command="cd include/terraform && terraform plan -out=tfplan",
    )

    terraform_apply = BashOperator(
        task_id="terraform_apply",
        bash_command="cd include/terraform && terraform apply -auto-approve tfplan",
    )

    terraform_init >> terraform_plan >> terraform_apply


terraform_runner()
