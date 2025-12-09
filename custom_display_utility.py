def display(object_to_display, csv_file_postfix: str,  exp_id: str) -> None:
    """A custom display for cli environments."""
    if "DataFrame" in str(type(object_to_display)):
        print("[Display (DataFrame)]")
        print(object_to_display.to_markdown(index=False))
        csv_file_path = "./output/" + exp_id + "df_" + csv_file_postfix + ".csv"
        object_to_display.to_csv(csv_file_path, index=False)
        print(f"[Display] CSV file saved to: {csv_file_path}")
        return
    else:
        print(type(object_to_display))
        raise NotImplementedError("Custom display function is not implemented yet.")