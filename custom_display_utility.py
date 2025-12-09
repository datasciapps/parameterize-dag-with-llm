import os


def _unique_path(path: str) -> str:
    """Return a filesystem path that does not yet exist by appending _1, _2, ... before the extension.

    The `path` may include an extension (e.g. .csv or .png). The returned value includes the extension.
    """
    base, ext = os.path.splitext(path)
    candidate = path
    i = 1
    while os.path.exists(candidate):
        candidate = f"{base}_{i}{ext}"
        i += 1
    return candidate


def display(object_to_display, output_file_postfix: str,  exp_id: str) -> None:
    """A custom display for cli environments."""
    if "DataFrame" in str(type(object_to_display)):
        print("[Display (DataFrame)]")
        print(object_to_display.to_markdown(index=False))
        os.makedirs("./output", exist_ok=True)
        csv_file_path = os.path.join(".", "output", f"{exp_id}df_{output_file_postfix}.csv")
        csv_file_path = _unique_path(csv_file_path)
        object_to_display.to_csv(csv_file_path, index=False)
        print(f"[Display] CSV file saved to: {csv_file_path}")
        return
    elif "graphviz" in str(type(object_to_display)):
        print("[Display (Graphviz)]")
        os.makedirs("./output", exist_ok=True)
        # Change the file extension to 'pdf'
        graph_output_path = os.path.join(".", "output", f"{exp_id}graph_{output_file_postfix}.pdf")
        graph_output_path = _unique_path(graph_output_path)
        filename_no_ext, _ = os.path.splitext(graph_output_path)
        
        # Change format to "pdf"
        object_to_display.render(filename=filename_no_ext, format="pdf", cleanup=True)
        
        # Update print statement to reflect the PDF output path
        print(f"[Display] Graph PDF saved to: {graph_output_path}")
        return
    else:
        print(type(object_to_display))
        raise NotImplementedError("Custom display function is not implemented yet.")