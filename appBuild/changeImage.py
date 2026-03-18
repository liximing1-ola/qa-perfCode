import sys
from PIL import Image
import os


def convert_images_to_grayscale():
    # Improve argument validation with helpful message
    if len(sys.argv) != 3:
        print("Usage: python changeImage.py <input_directory> <output_directory>")
        exit(1)

    image_path = sys.argv[1]
    out_path = sys.argv[2]

    # Create output directory with error handling for existing directories
    os.makedirs(out_path, exist_ok=True)  # Replaces os.mkdir with makedirs for robustness

    # Get list of files and filter image types (case-insensitive)
    file_list = os.listdir(image_path)
    image_extensions = {'.png', '.jpg', '.jpeg'}  # Include common image extensions
    image_files = [f for f in file_list if os.path.splitext(f)[1].lower() in image_extensions]
    total_images = len(image_files)

    if total_images == 0:
        print("No image files found in input directory")
        return

    success_count = 0  # Track successful conversions instead of total files

    for file in image_files:
        try:
            # Open and process image with error handling
            image_i = Image.open(os.path.join(image_path, file))
            image_gray = image_i.convert('L')
            image_gray.save(os.path.join(out_path, file), quality=95)
            success_count += 1
            print(f"{file} -- success")  # Use f-string for modern formatting
        except Exception as e:
            print(f"{file} -- failed: {str(e)}")  # Catch and report errors

    # More accurate success check (compares processed images vs successful conversions)
    print(f"Total images found: {total_images}")
    print(f"Successfully converted: {success_count}")
    if success_count == total_images:
        print('gray all success')
    else:
        print(f"Warning: {total_images - success_count} images failed to process")


if __name__ == '__main__':
    convert_images_to_grayscale()

