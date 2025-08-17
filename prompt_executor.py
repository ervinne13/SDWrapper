import os
import time
import requests
import prompt_patcher
from nsfw_classifier import check_nsfw, NSFWGeneratedOutput

# --- Config ---
OUTPUT_DIR = os.path.join(os.getcwd(), "generated")
COMFYUI_SERVER = "http://127.0.0.1:8188"
# --------------


def execute_workflow_unsafe(workflow):
    pid = send_workflow(workflow)
    result = poll_status(pid)
    prefix = prompt_patcher.get_patched_uuid(workflow)
    files = []
    if os.path.exists(OUTPUT_DIR):
        all_files = os.listdir(OUTPUT_DIR)
        if prefix:
            files = [f for f in all_files if f.startswith(prefix)]
        else:
            files = all_files
    file = files[0] if files else None
    return pid, result, file

def execute_workflow(workflow):
    attempts = 0
    max_attempts = 2
    nsfw_error = None
    pid = None
    result = None
    file = None
    while attempts < max_attempts:
        pid, result, file = execute_workflow_unsafe(workflow)
        if not file:
            break
        image_path = os.path.join(OUTPUT_DIR, file)
        try:
            check_nsfw(image_path)
            # If no exception, image is safe
            break
        except NSFWGeneratedOutput as e:
            print(f"[NSFW] Attempt {attempts+1}: {e}")
            nsfw_error = str(e)
            attempts += 1
            if attempts >= max_attempts:
                file = None
    if not file and nsfw_error:
        return {"prompt_id": pid, "result": result, "file": None, "error": nsfw_error}
    return {"prompt_id": pid, "result": result, "file": file}

def send_workflow(workflow):
    response = requests.post(f"{COMFYUI_SERVER}/prompt", json={"prompt": workflow})
    response.raise_for_status()
    return response.json()["prompt_id"]

def poll_status(prompt_id, interval=2):
    print(f"[poll_status] Watching status for prompt {prompt_id}...")
    while True:
        r = requests.get(f"{COMFYUI_SERVER}/history/{prompt_id}")
        if r.status_code == 200:
            data = r.json()
            if prompt_id in data:
                status = data[prompt_id]
                if "outputs" in status and status["outputs"]:
                    print("[poll_status] ✅ Finished!")
                    return status
        q = requests.get(f"{COMFYUI_SERVER}/queue").json()
        running = q.get("queue_running", [])
        pending = q.get("queue_pending", [])
        print(f"[poll_status] ⏳ Still running... {len(running)} running / {len(pending)} pending")
        if not running and not pending:
            print("[poll_status] ⚠️ Queue is empty, but no outputs found yet...")
            return None
        time.sleep(interval)
