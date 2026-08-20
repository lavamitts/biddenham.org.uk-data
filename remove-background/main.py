from pathlib import Path
from PIL import Image
from rembg import remove
import os


def main(input_path: str, output_path: str):
    """
    Removes the background from an image and saves it at maximum quality.
    """
    try:
        # Validate that the input file exists
        input_file = Path(input_path)
        if not input_file.is_file():
            print(f"Error: The file '{input_path}' does not exist.")
            return

        print(f"Processing '{input_file.name}'... Please wait.")

        # Open the input image
        with Image.open(input_file) as img:
            # Pass the image data to rembg
            # The remove function automatically handles alpha channels for transparency
            output_data = remove(img)

            # Save the image at maximum quality
            # For PNGs, optimize=True and compress_level=9 ensure loss-free maximum compression
            output_data.save(output_path, format="PNG", optimize=True, compress_level=9)

        print(f"Success! Saved high-quality background-free image to: {output_path}")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    script_dir = Path(__file__).resolve().parent

    # Get and make resource folders
    resources_folder = os.path.join(script_dir, "resources")
    in_folder = os.path.join(resources_folder, "in")
    out_folder = os.path.join(resources_folder, "out")

    # Get filenames
    input_image_filename = "ostrich.jpg"
    output_image_filename = f"transparent-{input_image_filename}"

    # Get full paths
    input_image_path = os.path.join(in_folder, input_image_filename)
    output_image_path = os.path.join(out_folder, output_image_filename)

    # Go ahead and remove the background
    main(input_image_path, output_image_path)
