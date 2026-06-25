from databricks.sdk.service.sql import StatementState
from databricks.sdk import WorkspaceClient
import time

def sql_call(databricks_sdk_client: WorkspaceClient, statement: str, warehouse_id: str ) -> list[dict]:
    """Execute a SQL statement on a Databricks SQL warehouse and return the results."""
    response = databricks_sdk_client.statement_execution.execute_statement(
        warehouse_id=warehouse_id,
        statement=statement,
        wait_timeout="30s",
    )
    while response.status.state not in (
        StatementState.SUCCEEDED, StatementState.FAILED,
        StatementState.CANCELED, StatementState.CLOSED,
    ):
        time.sleep(1)
        response = databricks_sdk_client.statement_execution.get_statement(response.statement_id)

    if response.status.state != StatementState.SUCCEEDED:
        raise RuntimeError(f"SQL failed [{response.status.state}]: {response.status.error}")

    if response.result is None or response.result.data_array is None:
        return []

    cols = [c.name for c in response.manifest.schema.columns]
    return [dict(zip(cols, row)) for row in response.result.data_array]

print("sql_call() helper ready")