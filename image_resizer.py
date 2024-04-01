import os
import sys
import argparse
from PIL import Image
import multiprocessing

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
        return True
    except Exception as e:
        print(f"Error resizing {input_path}: {e}")
        return False

def worker(input_queue, output_queue, size, format, verbose):
    while True:
        item = input_queue.get()
        if item is None:
            break
        input_path, output_path = item
        success = resize_image(input_path, output_path, size, format, verbose)
        output_queue.put(success)

def process_images(input_dir, output_dir, size, format, verbose, num_processes):
    input_queue = multiprocessing.Queue()
    output_queue = multiprocessing.Queue()

    processes = []
    for _ in range(num_processes):
        p = multiprocessing.Process(target=worker, args=(input_queue, output_queue, size, format, verbose))
        p.start()
        processes.append(p)

    for root, _, files in os.walk(input_dir):
        for filename in files:
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                input_path = os.path.join(root, filename)
                relative_path = os.path.relpath(input_path, input_dir)
                output_path = os.path.join(output_dir, relative_path)
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                input_queue.put((input_path, output_path))

    for _ in range(num_processes):
        input_queue.put(None)

    successes = 0
    total_files = sum(len(files) for _, _, files in os.walk(input_dir))
    while successes < total_files:
        success = output_queue.get()
        if success:
            successes += 1
        if verbose:
            print(f"Processed: {successes}/{total_files} files ({successes / total_files * 100:.2f}%)", end='\r')

    for p in processes:
        p.join()

def main():
    parser = argparse.ArgumentParser(description="Resize images in a directory tree.")
    parser.add_argument("-i", "--input", required=True, help="Input directory containing images.")
    parser.add_argument("-o", "--output", required=True, help="Output directory to store resized images.")
    parser.add_argument("-s", "--size", type=int, default=512, help="Size to resize the images.")
    parser.add_argument("-f", "--format", default="png", help="Output format for resized images (png or jpg). Default is png.")
    parser.add_argument("-n", "--num-processes", type=int, default=multiprocessing.cpu_count(), help="Number of processes to use for resizing. Default is number of available CPU cores.")
    parser.add_argument("-v", "--verbose", action="count", default=0, help="Verbose output.")
    args = parser.parse_args()

    process_images(args.input, args.output, args.size, args.format, args.verbose, args.num_processes)

if __name__ == "__main__":
    main()
