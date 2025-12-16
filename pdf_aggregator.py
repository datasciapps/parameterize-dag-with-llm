import argparse
from pathlib import Path
import matplotlib.pyplot as plt

# You will need to install 'pdf2image' and 'Pillow' for this script to run.
# You will also need 'poppler' installed on your system for pdf2image to work.
try:
    from pdf2image import convert_from_path
except ImportError:
    print("🚨 Missing required libraries: 'pdf2image' and 'Pillow'.")
    print("Please install them: pip install pdf2image Pillow")
    print("Also, ensure 'poppler' is installed on your system.")
    exit(1)


def aggregate_and_display_pdfs(archive_dir: str):
    """
    Finds specific PDF files in a directory, asserts the count, and
    aggregates their first pages into a 5x5 grid visualization.

    Args:
        archive_dir (str): The path to the directory containing the PDFs.
    """

    # 1. Setup paths and parameters
    archive_path = Path(archive_dir)
    pattern = "*full_dag_eff*.pdf"

    # 2. Find the target PDF files
    print(f"🔍 Searching for files matching '{pattern}' in '{archive_path}'...")

    # Use glob to find all matching files recursively (if needed, but simpler to just use glob here)
    target_files = sorted(list(archive_path.glob(pattern)))

    print(f"✅ Found {len(target_files)} files.")

    # 3. Assertion of file count
    expected_count = 25
    try:
        assert len(target_files) == expected_count, (
            f"Assertion Failed: Expected {expected_count} files, "
            f"but found {len(target_files)}."
        )
        print(f"🎉 Assertion successful: Found exactly {expected_count} files.")
    except AssertionError as e:
        print(f"❌ Error: {e}")
        # Decide whether to stop or continue with the files found
        if len(target_files) < expected_count:
            print(
                "Visualization cannot be created as 25 files are required for the 5x5 grid."
            )
            return
        # If more than 25 are found, we can take the first 25, but the user requested 25 exactly.
        # For this script, we'll stop if the assertion fails, as requested.
        # If you wanted to continue, you would add logic here.
        return

    # 4. Prepare for Visualization (Grid Aggregation)

    # Create a 5x5 subplot grid
    N_ROWS = 5
    N_COLS = 5
    fig, axes = plt.subplots(
        N_ROWS, N_COLS, figsize=(15, 15)
    )  # 15x15 inches figure size
    fig.suptitle(
        f"Aggregation of {expected_count} *full_dag_eff*.pdf Files", fontsize=16, y=1.02
    )

    # Flatten the axes array for easy iteration
    axes = axes.flatten()

    # Process the first 25 files (which we know are there due to the assertion)
    print("🖼️ Converting first page of PDFs to images and plotting...")

    for i, pdf_file in enumerate(target_files):
        ax = axes[i]

        try:
            # Convert the first page of the PDF to a list of PIL Images
            # Requires 'poppler' to be installed on the system
            images = convert_from_path(pdf_file, first_page=1, last_page=1, dpi=100)

            if images:
                # Display the image on the current subplot
                img = images[0]
                ax.imshow(img)
                ax.set_title(pdf_file.name, fontsize=8)
            else:
                # In case conversion failed but didn't raise an exception
                print(f"⚠️ Could not convert first page of {pdf_file.name}.")
                ax.text(0.5, 0.5, "Conversion Failed", ha="center", va="center")

        except Exception as e:
            # Handle potential conversion errors (e.g., corrupted PDF)
            print(f"⚠️ Error processing {pdf_file.name}: {e}")
            ax.text(0.5, 0.5, f"Error: {e}", ha="center", va="center", fontsize=8)

        # Clean up subplot aesthetics
        ax.axis("off")  # Hide axes for better visual

    # 5. Save the Visualization

    # Adjust layout to prevent titles/images from overlapping
    plt.tight_layout(rect=[0, 0, 1, 1.0])

    output_filename = "aggregated_pdf_grid.png"
    output_path = archive_path / output_filename

    print(f"💾 Saving visualization to: {output_path}")

    try:
        fig.savefig(output_path, dpi=300, bbox_inches="tight")
        print("✨ Successfully saved the grid visualization!")
    except Exception as e:
        print(f"❌ Failed to save figure: {e}")

    # Optional: Display the plot (comment out if running on a headless server)
    # plt.show()


def main():
    """Parses command line arguments and runs the aggregation process."""
    parser = argparse.ArgumentParser(
        description="Aggregate and visualize the first page of 25 specific PDF files."
    )

    # Make the archive directory configurable as an argument
    parser.add_argument(
        "archive_dir",
        type=str,
        help="The path to the archive directory (e.g., 'output/archive_a').",
    )

    args = parser.parse_args()

    # Ensure the provided directory exists before proceeding
    if not Path(args.archive_dir).is_dir():
        print(f"❌ Error: Directory '{args.archive_dir}' not found.")
        print("Please create the directory and place your PDF files inside.")
        return

    aggregate_and_display_pdfs(args.archive_dir)


if __name__ == "__main__":
    main()
