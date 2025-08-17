import json
import os

WORKFLOW_JSON = "workflow.json"
OUTPUT_DIR = os.path.join(os.getcwd(), "generated")

def patch_workflow():
    """
    This makes it easy for us to isolate things. We work on SD separately and generate the workflow,
    then simply patch it here once it's production ready.

    Note that prompt_patcher does live patching (for prompts) while this just sets up the defaults.
    This thing will actually modify the base workflow.json vs prompt_patcher that only modifies
    in memory
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(WORKFLOW_JSON, "r", encoding="utf-8") as f:
        workflow = json.load(f)

    patched = False
    for node_id, node in workflow.items():
        if (
            node.get("class_type") == "String"
            and node.get("_meta", {}).get("title") == "OutputDir"
        ):
            old_val = node["inputs"]["value"]
            node["inputs"]["value"] = OUTPUT_DIR
            print(f"📂 Patched OutputDir: {old_val} → {OUTPUT_DIR}")
            patched = True
                
    with open(WORKFLOW_JSON, "w", encoding="utf-8") as f:
        json.dump(workflow, f, indent=2)

    print(f"✅ Saved patched workflow to {WORKFLOW_JSON}")

if __name__ == "__main__":
    patch_workflow()
