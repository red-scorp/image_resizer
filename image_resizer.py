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
import hashlib

VERBOSITY_NONE : int = 0 # No verbose output.
VERBOSITY_LOW : int = 1 # Low verbose output.
VERBOSITY_HIGH : int = 2 # High verbose output.

DEFAULT_SIZE : int = 512 # Default size to resize the images.
DEFAULT_VERBOSITY : int = VERBOSITY_NONE # Default verbosity level for output.
DEFAULT_FORMAT : str = "same" # Default output format for resized images.
DEFAULT_RESIZE_MODE : str = "thumbnail" # Default resize mode for images.
DEFAULT_RENAME : str = "none" # Default rename pattern for resized images.

def store_image(image : Image.Image, output_path: str, format : str, rename : str, file_counter : int) -> tuple[bool, str]:
    """
    Store an image to the output path with the specified format.

    This function stores an image to the output path with the specified format.

    :param image: Image to store.
    :param output_path: Path to save the image.
    :param format: Output format for the image.
    :param rename: Rename pattern for the image.
    :param file_counter: Counter for the generated files.
    :return: Tuple of boolean success value and the output path of the stored image.
    """

    if format.lower() == "png":
        output_path = os.path.splitext(output_path)[0] + ".png"
        image.save(output_path, format = "PNG")
    elif format.lower() == "jpg":
        output_path = os.path.splitext(output_path)[0] + ".jpg"
        image.save(output_path, format = "JPEG")
    elif format.lower() == "gif":
        output_path = os.path.splitext(output_path)[0] + ".gif"
        image.save(output_path, format = "GIF")
    elif format.lower() == "tiff":
        output_path = os.path.splitext(output_path)[0] + ".tiff"
        image.save(output_path, format = "TIFF")
    elif format.lower() == "bmp":
        output_path = os.path.splitext(output_path)[0] + ".bmp"
        image.save(output_path, format = "BMP")
    elif format.lower() == "webp":
        output_path = os.path.splitext(output_path)[0] + ".webp"
        image.save(output_path, format = "WEBP")
    elif format.lower() == "same":
        image.save(output_path)
    else:
        return False, f"Unsupported output format: {format}"

    if rename.lower() == "none":
        return True, output_path

    new_output_path : str

    if rename.lower() == "counter":
        new_output_path = os.path.dirname(output_path) + "/" + str(file_counter) + os.path.splitext(output_path)[1]
        os.remove(new_output_path) if os.path.exists(new_output_path) else None
        os.rename(output_path, new_output_path)
        return True, new_output_path

    if rename.lower() == "0-counter":
        new_output_path = os.path.dirname(output_path) + "/" + f"{file_counter:08d}" + os.path.splitext(output_path)[1]
        os.remove(new_output_path) if os.path.exists(new_output_path) else None
        os.rename(output_path, new_output_path)
        return True, new_output_path

    if rename.lower() == "md5":
        file_content = open(output_path, "rb").read()
        new_output_path = os.path.dirname(output_path) + "/" + hashlib.md5(file_content).hexdigest() + os.path.splitext(output_path)[1]
        os.remove(new_output_path) if os.path.exists(new_output_path) else None
        os.rename(output_path, new_output_path)
        return True, new_output_path

    return True, output_path

def resize_image(input_path : str, output_path : str, size : int, resize_mode : str, normal_image : bool, mirror_image : bool, format : str, rename : str, file_counter : int) -> tuple[bool, int, str]:
    """
    Resize an image to the specified size and save it to the output path.

    This function resizes an image to the specified size and saves it to the output path.
    Optionally, it can also save a mirrored version of the image.

    This function supports several resize modes: thumbnail, cover and crop.
    - thumbnail: Put the image into a square box of size x size with the original aspect ratio.
    - cover: Resize the image to cover the whole box of size x size with the original aspect ratio.
    - crop: Crop the image to a square box of size x size.

    :param input_path: Path to the input image.
    :param output_path: Path to save the resized image.
    :param size: Size to resize the image.
    :param resize_mode: Resize mode for the image.
    :param normal_image: Flag to save normal image.
    :param mirror_image: Flag to save mirrored image.
    :param format: Output format for the resized image.
    :param rename: Rename pattern for the resized image.
    :param file_counter: Counter for the generated files.
    :return: Tuple of boolean success value, number of generated files and a message string.
    """

    all_output_list : list[str] = []

    try:
        # Open the image
        image : Image.Image = Image.open(input_path)

        # Check if the image has exif metadata and contains orientation information
        if hasattr(image, "_getexif") and image._getexif():
            exif : dict[int, Any] = dict(image._getexif().items())
            orientation : int = exif.get(0x0112, 1)  # Default orientation is 1 (normal)

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
            return (False, len(all_output_list), f"Unsupported resize mode: {resize_mode}")

        # Resize the image
        image = image.resize((result_width, result_height), resample = Image.BICUBIC)

        if normal_image:
            # Save the image with the correct format
            success, output = store_image(image, output_path, format, rename, file_counter)
            if success:
                all_output_list.append(output)
            else:
                return (False, len(all_output_list), output)

        if mirror_image:
            # Mirror the image and save it with the correct format
            mirrored_image : Image.Image = image.transpose(Image.FLIP_LEFT_RIGHT)
            mirrored_output_path = os.path.splitext(output_path)[0] + "_mirror" + os.path.splitext(output_path)[1]
            success, output = store_image(mirrored_image, mirrored_output_path, format, rename, file_counter + 1)
            if success:
                all_output_list.append(output)
            else:
                return (False, len(all_output_list), output)

        all_output_path : str = ",".join(all_output_list)

        return (True, len(all_output_list), f"Resized: {input_path} ({original_width}x{original_height}) to {all_output_path} ({result_width}x{result_height})")
    except Exception as e:
        return (False, len(all_output_list), f"Error resizing {input_path}: {e}")

def worker(input_queue : Queue, output_queue : Queue, size : int, resize_mode : str, normal_image : bool, mirror_image : bool, format : str, rename : str) -> None:
    """
    Worker function to resize images from the input queue and store the results in the output queue.
    
    :param input_queue: Queue to read input image paths from.
    :param output_queue: Queue to write success status to.
    :param size: Size to resize the images.
    :param resize_mode: Resize mode for images.
    :param normal_image: Flag to save normal image.
    :param mirror_image: Flag to save mirrored image.
    :param format: Output format for the resized images.
    :param rename: Rename pattern for the resized images.
    :return: None
    """

    while True:
        # Get an item from the input queue
        item : tuple[str, str, int] = input_queue.get()
        if item is None: # Termination signal is found
            break

        # Resize the image and put the result status in the output queue
        input_path : str
        output_path : str
        file_counter : int
        input_path, output_path, file_counter = item
        result : tuple[bool, int, str] = resize_image(input_path, output_path, size, resize_mode, normal_image, mirror_image, format, rename, file_counter)
        output_queue.put(result)

def process_images(input_dir : str, output_dir : str, size : int, resize_mode : str, normal_image : bool, mirror_image : bool, format : str, rename : str, verbose : int, num_processes : int) -> None:
    """
    Process images in the input directory and store the resized images in the output directory.
    
    :param input_dir: Input directory containing images.
    :param output_dir: Output directory to store resized images.
    :param size: Size to resize the images.
    :param resize_mode: Resize mode for images.
    :param normal_image: Flag to save normal image.
    :param mirror_image: Flag to save mirrored image.
    :param format: Output format for the resized images.
    :param rename: Rename pattern for the resized images.
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
        p : Process = Process(target = worker, args = (input_queue, output_queue, size, resize_mode, normal_image, mirror_image, format, rename))
        p.start()
        processes.append(p)

    total_files : int = 0
    file_counter : int = 0

    # Walk through the input directory and add images to the input queue
    root : str
    files : list[str]
    for root, _, files in os.walk(input_dir):
        filename : str
        for filename in files:
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', "gif", "tiff", "tif", "bmp", "webp")):
                input_path : str = os.path.join(root, filename)
                relative_path : str = os.path.relpath(input_path, input_dir)
                output_path : str = os.path.join(output_dir, relative_path)
                os.makedirs(os.path.dirname(output_path), exist_ok = True)
                input_queue.put((input_path, output_path, file_counter))
                total_files += 1
                file_counter += 2 if mirror_image and normal_image else 1

    # Add termination signals to the input queue
    for _ in range(num_processes):
        input_queue.put(None)

    successes : int = 0
    processed_files : int = 0
    generated_files : int = 0
    errors : int = 0

    # Wait for all worker processes to finish and collect the results
    while processed_files < total_files:
        # Read the result from the output queue
        result : tuple[bool, int, str] = output_queue.get()
        if result is None:
            break

        success : bool
        generated : int
        message : str
        success, generated, message = result

        # Update counters based on the result
        processed_files += 1
        if success:
            successes += 1
        else:
            errors += 1
        generated_files += generated

        # Print verbose output to show the result of the image processing
        if verbose >= VERBOSITY_HIGH:
            print(message)

        # Print verbose output to show general progress
        if verbose >= VERBOSITY_LOW:
            print(f"Processed: {processed_files}/{total_files} files ({processed_files / total_files * 100:.2f}%)", end = '\r')

    # Join all worker processes
    for p in processes:
        p.join()

    # Print verbose output to show general progress at the end
    if verbose >= VERBOSITY_LOW:
        print(f"Processed: {processed_files}/{total_files} files ({processed_files / total_files * 100:.2f}%)")

    # Print verbose output to show the number of successes and errors
    if verbose >= VERBOSITY_HIGH:
        print(f"Processed files: {processed_files}, Successes: {successes}, Errors: {errors}, Generated files: {generated_files}")

def main() -> None:
    """
    Main function to parse command line arguments and process images.
    
    :return: None
    """

    # Parse command line arguments
    parser : ArgumentParser = ArgumentParser(description = "Resize images in a directory tree.")
    parser.add_argument("-i", "--input", required = True, help = "Input directory containing images.")
    parser.add_argument("-o", "--output", required = True, help = "Output directory to store resized images.")
    parser.add_argument("-s", "--size", type = int, default = DEFAULT_SIZE, help = f"Size to resize the images. Default is {DEFAULT_SIZE}.")
    parser.add_argument("-r", "--resize-mode", default = DEFAULT_RESIZE_MODE, help = f"Resize mode for images (thumbnail, cover or crop). Default is {DEFAULT_RESIZE_MODE}.")
    parser.add_argument("-f", "--format", default = DEFAULT_FORMAT, help = f"Output format for resized images (same, png, jpg, gif, tiff, bmp and webp). Default is {DEFAULT_FORMAT}.")
    parser.add_argument("-n", "--num-processes", type = int, default = cpu_count(), help = "Number of processes to use for resizing. Default is number of available CPU cores.")
    parser.add_argument("-m", "--add-mirror", action = "store_true", help = "Add a mirrored version of each image.")
    parser.add_argument("-M", "--mirror-only", action = "store_true", help = "Produce only a mirrored version of each image.")
    parser.add_argument("-R", "--rename", default = "none", help = "Rename the resized images using a pattern (none, counter, 0-counter, md5).")
    parser.add_argument("-v", "--verbose", action = "count", default = DEFAULT_VERBOSITY, help = "Verbose output.")
    args : Namespace = parser.parse_args()

    # Check some input arguments for validity
    if args.format.lower() not in ["same", "png", "jpg", "gif", "tiff", "bmp", "webp"]:
        print(f"Unsupported output format {args.format}")
        sys.exit(1)

    if args.resize_mode.lower() not in ["thumbnail", "cover", "crop"]:
        print(f"Unsupported resize mode {args.resize_mode}")
        sys.exit(1)

    if args.rename.lower() not in ["none", "counter", "0-counter", "md5"]:
        print(f"Unsupported rename pattern {args.rename}")
        sys.exit(1)

    if args.size <= 0:
        print(f"Invalid size {args.size}")
        sys.exit(1)

    if args.num_processes <= 0:
        print(f"Invalid number of processes {args.num_processes}")
        sys.exit(1)

    if args.add_mirror and args.mirror_only:
        print("Options -m/--add-mirror and -M/--mirror-only are mutually exclusive")
        sys.exit(1)

    normal_image : bool = True
    mirror_image : bool = False

    if args.add_mirror:
        normal_image = True
        mirror_image = True

    if args.mirror_only:
        mirror_image = True
        normal_image = False

    # Start processing images
    process_images(args.input, args.output, args.size, args.resize_mode, normal_image, mirror_image, args.format, args.rename, args.verbose, args.num_processes)

if __name__ == "__main__":
    main()
