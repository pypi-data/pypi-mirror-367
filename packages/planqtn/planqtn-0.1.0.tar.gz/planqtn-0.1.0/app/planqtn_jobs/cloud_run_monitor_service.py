import base64
import json
import os
from fastapi import FastAPI, Request
import logging
import uvicorn

from planqtn_jobs.task import (
    SupabaseCredentials,
    SupabaseTaskStore,
    TaskDetails,
    TaskState,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Cloud Run Job Monitor Service")


def extract_details_from_decoded_data(decoded_data: bytes) -> str:
    obj = json.loads(decoded_data)
    args = obj["protoPayload"]["response"]["spec"]["template"]["spec"]["containers"][0][
        "args"
    ]
    index = args.index("--task-uuid")
    task_uuid = args[index + 1]
    index = args.index("--user-id")
    user_id = args[index + 1]
    conds = obj["protoPayload"]["response"]["status"]["conditions"]
    result = None
    for cond in conds:
        if cond["type"] == "Completed":
            result = cond["message"]
            break
    return task_uuid, user_id, result


def extract_details(body: dict) -> str:
    """Extract the job ID from the decoded data."""
    base64_data = body["message"]["data"]
    decoded_data = base64.b64decode(base64_data)
    return extract_details_from_decoded_data(decoded_data)


@app.post("/job-failed")
async def handle_job_failed(request: Request):
    """Handle job failed events from Cloud Run."""
    body = await request.json()
    logger.info(f"Received job failed event: {body}")

    task_uuid, user_id, result = extract_details(body)
    logger.info(f"Task UUID: {task_uuid}")

    task_store = SupabaseTaskStore(
        task_db_credentials=SupabaseCredentials(
            url=os.environ["SUPABASE_URL"],
            service_role_key=os.environ["SUPABASE_KEY"],
        ),
        task_updates_db_credentials=SupabaseCredentials(
            url=os.environ["SUPABASE_URL"],
            service_role_key=os.environ["SUPABASE_KEY"],
        ),
    )

    task_details = TaskDetails(
        user_id=user_id,
        uuid=task_uuid,
    )

    logger.info(f"Task {task_details.uuid} failed with {result}, storing result")
    task_store.store_task_result(
        task=task_details,
        result=result,
        state=TaskState.FAILED,
    )
    print(f"Sending task update for {task_details.uuid} to state {TaskState.FAILED}")
    res = task_store.send_task_update(task_details, {"state": TaskState.FAILED.value})
    print(f"Task update result: {res}")

    return {"status": "received", "event": "job-failed"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
