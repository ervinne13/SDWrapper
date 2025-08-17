import json
import time
import requests
import os

# --- Config ---
JSON_PATH = "workflow.json"
OUTPUT_DIR = os.path.join(os.getcwd(), "generated")
COMFYUI_SERVER = "http://127.0.0.1:8188"
# --------------

def send_workflow(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        workflow = json.load(f)

    response = requests.post(f"{COMFYUI_SERVER}/prompt", json={"prompt": workflow})
    response.raise_for_status()
    return response.json()["prompt_id"]

def poll_status(prompt_id, interval=2):
    print(f"🔎 Watching status for prompt {prompt_id}...")
    while True:
        # check history for this prompt
        r = requests.get(f"{COMFYUI_SERVER}/history/{prompt_id}")
        if r.status_code == 200:
            data = r.json()
            if prompt_id in data:
                status = data[prompt_id]
                if "outputs" in status and status["outputs"]:
                    print("✅ Finished!")
                    return status

        # check queue state too
        q = requests.get(f"{COMFYUI_SERVER}/queue").json()
        running = q.get("queue_running", [])
        pending = q.get("queue_pending", [])

        if not running and not pending:
            print("⚠️ Queue is empty, but no outputs found yet...")
            return None

        print(f"⏳ Still running... {len(running)} running / {len(pending)} pending")
        time.sleep(interval)

if __name__ == "__main__":
    pid = send_workflow(JSON_PATH)
    result = poll_status(pid)

    # List files in generated folder
    if os.path.exists(OUTPUT_DIR):
        files = os.listdir(OUTPUT_DIR)
        print(f"📑 Files in {OUTPUT_DIR}:")
        for f in files:
            print(" -", f)
    else:
        print("⚠️ No generated folder found.")
