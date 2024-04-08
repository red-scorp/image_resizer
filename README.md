# image_resizer

This python script is meant to be user to resize large image datasets to use them in machine learning models. It uses the PIL library to resize the images and the multiprocessing library to speed up the process.

## Usage

The main usage of the script is to resize bunch of images from input directory tree to output directory tree. The script will keep the same directory structure in the output directory as in the input directory.

For example, this command will resize all images to fit into 512x512 px from the input directory and save them in the output directory with the same directory structure:

```bash
python3 image_resizer.py -i /path/to/input_dir --o /path/to/output_dir -s 512
```

The script will create the output directory if it does not exist.

## Options

Full usage information can be found by running the script with the `-h` flag:

```bash
python3 image_resizer.py -h
```

This will print the following help message:

```bash
usage: image_resizer.py [-h] -i INPUT -o OUTPUT [-s SIZE] [-r RESIZE_MODE] [-f FORMAT] [-n NUM_PROCESSES] [-m] [-M] [-v]

Resize images in a directory tree.

options:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Input directory containing images.
  -o OUTPUT, --output OUTPUT
                        Output directory to store resized images.
  -s SIZE, --size SIZE  Size to resize the images. Default is 512.
  -r RESIZE_MODE, --resize-mode RESIZE_MODE
                        Resize mode for images (thumbnail, cover or crop). Default is thumbnail.
  -f FORMAT, --format FORMAT
                        Output format for resized images (same, png or jpg). Default is same.
  -n NUM_PROCESSES, --num-processes NUM_PROCESSES
                        Number of processes to use for resizing. Default is number of available CPU cores.
  -m, --add-mirror      Add a mirrored version of each image.
  -M, --mirror-only     Produce only a mirrored version of each image.
  -v, --verbose         Verbose output.
```

