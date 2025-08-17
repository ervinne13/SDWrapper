import json
from datetime import datetime

def get_patched_json(data):
    with open("workflow.json", "r", encoding="utf-8") as f:
        workflow = json.load(f)
    patched = patch_workflow(workflow, data)
    return patched

def patch_workflow(workflow, data):
    prefix_value = "generation-" + datetime.now().strftime("%Y%m%d%H%M%S")
    for node in workflow.values():
        if node.get("class_type") == "String" and node.get("_meta", {}).get("title") == "Prefix":
            node["inputs"]["value"] = prefix_value
        if node.get("class_type") == "Metadata Hub":
            # TODO: Implement later based on data, for now we hardcode the prompt
            node["inputs"]["prompt"] = "Cowboy shot of a lady holding a paper that says 'hello world' on it."
            node["inputs"]["steps"] = data["steps"] if "steps" in data else 24
    return workflow

def get_patched_uuid(workflow):
    """
    Returns the Prefix value from the patched workflow.
    """
    for node in workflow.values():
        if node.get("class_type") == "String" and node.get("_meta", {}).get("title") == "Prefix":
            return node["inputs"].get("value")
    return None

