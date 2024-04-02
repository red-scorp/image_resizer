#!/usr/bin/env python3

# image_resizer.py - Resize images in a directory tree.
# This script is intended to resize images in a directory tree to a specified size and store the resized images in a separate directory.
# Copyright (c) 2024, Andriy Golovnya

"""
Resize images in a directory tree.

This script is intended to resize images in a directory tree to a specified size and store the resized images in a separate directory.
"""

import os
import sys
from argparse import ArgumentParser, Namespace
from PIL import Image
from multiprocessing import Process, Queue, cpu_count
from typing import Any

VERBOSITY_NONE : int = 0 # No verbose output.
VERBOSITY_LOW : int = 1 # Low verbose output.
VERBOSITY_HIGH : int = 2 # High verbose output.

DEFAULT_SIZE : int = 512 # Default size to resize the images.
DEFAULT_VERBOSITY : int = VERBOSITY_NONE # Default verbosity level for output.
DEFAULT_FORMAT : str = "same" # Default output format for resized images.
DEFAULT_RESIZE_MODE : str = "thumbnail" # Default resize mode for images.

def resize_image(input_path : str, output_path : str, size : int, resize_mode : str, format : str, verbose : int) -> bool:
    """
    Resize an image to the specified size and save it to the output path.

    :param input_path: Path to the input image.
    :param output_path: Path to save the resized image.
    :param size: Size to resize the image.
    :param resize_mode: Resize mode for the image.
    :param format: Output format for the resized image.
    :param verbose: Verbosity level for output.
    :return: ``True`` if the image was resized successfully, ``False`` otherwise.
    """

    try:
        # Open the image
        image = Image.open(input_path)

        # Check if the image has exif metadata and contains orientation information
        if hasattr(image, "_getexif") and image._getexif():
            exif = dict(image._getexif().items())
            orientation = exif.get(0x0112, 1)  # Default orientation is 1 (normal)

            # Rotate the image according to its orientation
            if orientation == 3:
                image = image.transpose(Image.ROTATE_180)
            elif orientation == 6:
                image = image.transpose(Image.ROTATE_270)
            elif orientation == 8:
                image = image.transpose(Image.ROTATE_90)

        # Prepare the image parameters for resizing
        original_width : int = image.width
        original_height : int = image.height
        result_width : int = 0
        result_height : int = 0

        # Calculate the new size based on the resize mode
        if resize_mode.lower() == "thumbnail":
            # We want to put the image into a square box of size x size with the original aspect ratio
            if image.width > image.height:
                result_width = size
                result_height = int((result_width * original_height) / original_width)
            else:
                result_height = size
                result_width = int((result_height * original_width) / original_height)

        elif resize_mode.lower() == "cover":
            # We want the resized image to cover the whole box of size x size with the original aspect ratio
            if image.width > image.height:
                result_height = size
                result_width = int((result_height * original_width) / original_height)
            else:
                result_width = size
                result_height = int((result_width * original_height) / original_width)

        elif resize_mode.lower() == "crop":
            # We want to crop the image to a square box of size x size
            # Calculate the crop box
            box : tuple[int, int, int, int] = (0, 0, 0, 0)
            if image.width > image.height:
                box = (int((original_width - original_height) / 2), 0, int((original_width + original_height) / 2), original_height)
            else:
                box = (0, int((original_height - original_width) / 2), original_width, int((original_height + original_width) / 2))
            # Crop the image to make it square
            image = image.crop(box)
            result_height = size
            result_width = size

        else:
            print(f"Unsupported resize mode: {resize_mode}")
            return False

        # Resize the image
        image = image.resize((result_width, result_height), resample = Image.BICUBIC)

        # Save the image with the correct format
        if format.lower() == "png":
            output_path = os.path.splitext(output_path)[0] + ".png"
            image.save(output_path, format = "PNG")
        elif format.lower() == "jpg":
            output_path = os.path.splitext(output_path)[0] + ".jpg"
            image.save(output_path, format = "JPEG")
        elif format.lower() == "same":
            image.save(output_path)
        else:
            print(f"Unsupported output format: {format}")
            return False

        # Print verbose output to show the resized image path and size
        if verbose >= VERBOSITY_HIGH:
            print(f"Resized: {input_path} ({original_width}x{original_height}) to {output_path} ({result_width}x{result_height})")

        return True
    except Exception as e:
        print(f"Error resizing {input_path}: {e}")
        return False

def worker(input_queue : Queue, output_queue : Queue, size : int, resize_mode : str, format : str, verbose : int) -> None:
    """
    Worker function to resize images from the input queue and store the results in the output queue.
    
    :param input_queue: Queue to read input image paths from.
    :param output_queue: Queue to write success status to.
    :param size: Size to resize the images.
    :param resize_mode: Resize mode for images.
    :param format: Output format for the resized images.
    :param verbose: Verbosity level for output.
    :return: None
    """

    while True:
        # Get an item from the input queue
        item = input_queue.get()
        if item is None: # Termination signal is found
            break

        # Resize the image and put the success status in the output queue
        input_path, output_path = item
        success : bool = resize_image(input_path, output_path, size, resize_mode, format, verbose)
        output_queue.put(success)

def process_images(input_dir : str, output_dir : str, size : int, resize_mode : str, format : str, verbose : int, num_processes : int) -> None:
    """
    Process images in the input directory and store the resized images in the output directory.
    
    :param input_dir: Input directory containing images.
    :param output_dir: Output directory to store resized images.
    :param size: Size to resize the images.
    :param resize_mode: Resize mode for images.
    :param format: Output format for the resized images.
    :param verbose: Verbosity level for output.
    :param num_processes: Number of processes to use for resizing.
    :return: None
    """

    # Create input and output queues for the worker processes
    input_queue : Queue = Queue()
    output_queue : Queue = Queue()

    # Start worker processes to resize images
    processes : list[Process] = []
    for _ in range(num_processes):
        p : Process = Process(target = worker, args = (input_queue, output_queue, size, resize_mode, format, verbose))
        p.start()
        processes.append(p)

    # Walk through the input directory and add images to the input queue
    for root, _, files in os.walk(input_dir):
        for filename in files:
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                input_path = os.path.join(root, filename)
                relative_path = os.path.relpath(input_path, input_dir)
                output_path = os.path.join(output_dir, relative_path)
                os.makedirs(os.path.dirname(output_path), exist_ok = True)
                input_queue.put((input_path, output_path))

    # Add termination signals to the input queue
    for _ in range(num_processes):
        input_queue.put(None)

    # Wait for all worker processes to finish and collect the results
    successes : int = 0
    all_files : int = 0
    total_files : int = sum(len(files) for _, _, files in os.walk(input_dir))
    while all_files < total_files:
        success = output_queue.get()
        all_files += 1
        if success:
            successes += 1
        if verbose >= VERBOSITY_LOW:
            print(f"Processed: {successes}/{total_files} files ({successes / total_files * 100:.2f}%)", end = '\r')

    # Join all worker processes
    for p in processes:
        p.join()

    # Print verbose output to show the number of processed images
    if verbose >= VERBOSITY_LOW:
        print(f"Processed: {successes}/{total_files} files ({successes / total_files * 100:.2f}%)")

def main() -> None:
    """
    Main function to parse command line arguments and process images.
    
    :return: None
    """

    # Parse command line arguments
    parser = ArgumentParser(description = "Resize images in a directory tree.")
    parser.add_argument("-i", "--input", required = True, help = "Input directory containing images.")
    parser.add_argument("-o", "--output", required = True, help = "Output directory to store resized images.")
    parser.add_argument("-s", "--size", type = int, default = DEFAULT_SIZE, help = f"Size to resize the images. Default is {DEFAULT_SIZE}.")
    parser.add_argument("-r", "--resize-mode", default = DEFAULT_RESIZE_MODE, help = f"Resize mode for images (thumbnail, cover or crop). Default is {DEFAULT_RESIZE_MODE}.")
    parser.add_argument("-f", "--format", default = DEFAULT_FORMAT, help = f"Output format for resized images (same, png or jpg). Default is {DEFAULT_FORMAT}.")
    parser.add_argument("-n", "--num-processes", type = int, default = cpu_count(), help = "Number of processes to use for resizing. Default is number of available CPU cores.")
    parser.add_argument("-v", "--verbose", action = "count", default = DEFAULT_VERBOSITY, help = "Verbose output.")
    args : Namespace = parser.parse_args()

    # Check some input arguments for validity
    if args.format.lower() not in ["same", "png", "jpg"]:
        print(f"Unsupported output format {args.format}")
        sys.exit(1)

    if args.resize_mode.lower() not in ["thumbnail", "cover", "crop"]:
        print(f"Unsupported resize mode {args.resize_mode}")
        sys.exit(1)

    if args.size <= 0:
        print(f"Invalid size {args.size}")
        sys.exit(1)

    # Start processing images
    process_images(args.input, args.output, args.size, args.resize_mode, args.format, args.verbose, args.num_processes)

if __name__ == "__main__":
    main()
