import os
import sys
import argparse
from PIL import Image

def resize_image(input_path, output_path, size, format, verbose):
    try:
        image = Image.open(input_path)
        if image.width <= size and image.height <= size:
            if verbose >= 2:
                print(f"Skipping: {input_path} (already smaller than {size}x{size})")
            return

        if image.width > size or image.height > size:
            image.thumbnail((size, size))

        if format.lower() == "png":
            output_path = os.path.splitext(output_path)[0] + ".png"
            image.save(output_path, format="PNG")
        elif format.lower() == "jpg":
            output_path = os.path.splitext(output_path)[0] + ".jpg"
            image.save(output_path, format="JPEG")
        else:
            print(f"Unsupported output format: {format}")
            return

        if verbose >= 2:
            print(f"Resized: {input_path}")
    except Exception as e:
        print(f"Error resizing {input_path}: {e}")

def process_images(input_dir, output_dir, size, format, verbose):
    total_files = sum(len(files) for _, _, files in os.walk(input_dir))
    processed_files = 0

    for root, dirs, files in os.walk(input_dir):
        for filename in files:
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                input_path = os.path.join(root, filename)
                relative_path = os.path.relpath(input_path, input_dir)
                output_path = os.path.join(output_dir, relative_path)
                os.makedirs(os.path.dirname(output_path), exist_ok=True)

                resize_image(input_path, output_path, size, format, verbose)

                processed_files += 1
                if verbose:
                    print(f"Processed: {processed_files}/{total_files} files ({processed_files / total_files * 100:.2f}%)", end='\r')

def main():
    parser = argparse.ArgumentParser(description="Resize images in a directory tree.")
    parser.add_argument("-i", "--input", required=True, help="Input directory containing images.")
    parser.add_argument("-o", "--output", required=True, help="Output directory to store resized images.")
    parser.add_argument("-s", "--size", type=int, default=512, help="Size to resize the images.")
    parser.add_argument("-f", "--format", default="png", help="Output format for resized images (png or jpg). Default is png.")
    parser.add_argument("-v", "--verbose", action="count", default=0, help="Verbose output.")
    args = parser.parse_args()

    process_images(args.input, args.output, args.size, args.format, args.verbose)

if __name__ == "__main__":
    main()
