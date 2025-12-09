import json
import os

import numpy as np

def _unique_path(path: str) -> str:
    """Return a filesystem path that does not yet exist by appending _1, _2, ... before the extension.

    The `path` may include an extension (e.g. .csv or .png). The returned value includes the extension.
    The first unique path will use '_1'.
    """
    base, ext = os.path.splitext(path)
    
    # Start with i = 1
    i = 1
    
    # Construct the candidate path with the _1 postfix
    candidate = f"{base}_{i}{ext}"

    # Loop until a path that does not exist is found
    # This loop will check _1, _2, _3, ...
    while os.path.exists(candidate):
        i += 1
        candidate = f"{base}_{i}{ext}"
        
    return candidate


def display(object_to_display, output_file_postfix: str,  exp_id: str) -> None:
    """A custom display for cli environments."""
    if "DataFrame" in str(type(object_to_display)):
        print("[Display (DataFrame)]")
        print(object_to_display.to_markdown(index=False))
        os.makedirs("./output", exist_ok=True)
        # Construct the base path *without* the initial _1 for _unique_path to handle
        base_csv_file_path = os.path.join(".", "output", f"{exp_id}df_{output_file_postfix}.csv")
        
        # _unique_path will now return a path ending in _1.csv, _2.csv, etc.
        csv_file_path = _unique_path(base_csv_file_path)
        
        object_to_display.to_csv(csv_file_path, index=False)
        print(f"[Display] CSV file saved to: {csv_file_path}")
        return
    elif "graphviz" in str(type(object_to_display)):
        print("[Display (Graphviz)]")
        os.makedirs("./output", exist_ok=True)
        
        # Construct the base path *without* the initial _1 for _unique_path to handle
        # Note: We still pass .pdf extension so _unique_path works correctly.
        base_graph_output_path = os.path.join(".", "output", f"{exp_id}graph_{output_file_postfix}.pdf")
        
        # _unique_path will now return a path ending in _1.pdf, _2.pdf, etc.
        graph_output_path = _unique_path(base_graph_output_path)
        
        # The graphviz render function takes the filename *without* extension
        filename_no_ext, _ = os.path.splitext(graph_output_path)
        
        # Change format to "pdf"
        object_to_display.render(filename=filename_no_ext, format="pdf", cleanup=True)
        
        # Update print statement to reflect the PDF output path (which includes the .pdf extension)
        print(f"[Display] Graph PDF saved to: {graph_output_path}")
        return
    else:
        print(type(object_to_display))
        raise NotImplementedError("Custom display function is not implemented yet.")

def export_graph_snapshot_to_json(json_output_data: dict, exp_id: str, console_output_json: bool = False) -> None:
    print("[Exporting Graph Snapshot to JSON]")
    os.makedirs("./output", exist_ok=True)
    # Construct the base path *without* the initial _1 for _unique_path to handle
    base_json_file_path = os.path.join(".", "output", f"{exp_id}graph_snapshot.json")
        
    # _unique_path will now return a path ending in _1.csv, _2.csv, etc.
    json_file_path = _unique_path(base_json_file_path)

    with open(json_file_path, "w") as f:
        json.dump(json_output_data, f, indent=2, cls=CustomJsonEncoder)
    print(f"[Exporting Graph Snapshot to JSON] Visualization data saved to : {json_file_path}")

    if console_output_json:
        print("\n--- Visualization Data (JSON) ---")
        print(json.dumps(json_output_data, indent=2, cls=CustomJsonEncoder))


# Custom JSON encoder to handle non-serializable types like numpy floats and sets
class CustomJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.float64):
            return float(obj)
        if isinstance(obj, set):
            return list(obj)
        # Convert tuple keys in dictionaries to strings
        if isinstance(obj, dict):
            return {str(k): v for k, v in obj.items()}
        return json.JSONEncoder.default(self, obj)