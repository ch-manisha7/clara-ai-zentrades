import json
import os
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TASK_LOG_PATH = os.path.join(PROJECT_ROOT, "outputs", "task_log.json")


def _load():
    if os.path.exists(TASK_LOG_PATH):
        with open(TASK_LOG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def _save(tasks):
    os.makedirs(os.path.dirname(TASK_LOG_PATH), exist_ok=True)
    with open(TASK_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=4, ensure_ascii=False)


def create_task(account_id, company_name, task_type, status="open", notes=""):
    tasks = _load()
    task = {
        "task_id": "CLARA-" + str(len(tasks) + 1).zfill(4),
        "account_id": account_id,
        "company_name": company_name,
        "task_type": task_type,
        "status": status,
        "notes": notes,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    for i, t in enumerate(tasks):
        if t["account_id"] == account_id and t["task_type"] == task_type:
            task["task_id"] = t["task_id"]
            task["created_at"] = t["created_at"]
            tasks[i] = task
            _save(tasks)
            return task
    tasks.append(task)
    _save(tasks)
    return task


def update_task_status(account_id, task_type, new_status):
    tasks = _load()
    for t in tasks:
        if t["account_id"] == account_id and t["task_type"] == task_type:
            t["status"] = new_status
            t["updated_at"] = datetime.now().isoformat()
    _save(tasks)
