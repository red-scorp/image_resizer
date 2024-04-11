# image_resizer

This python script is meant to be user to resize large image datasets to use them in machine learning models. It uses the PIL library to resize the images and the multiprocessing library to speed up the process.

## Usage

The main usage of the script is to resize bunch of images from input directory tree to output directory tree. The script will keep the same directory structure in the output directory as in the input directory.

For example, this command will resize all images to fit into `1024`x`1024` px from the input directory and save them in the output directory with the same directory structure:

```bash
python3 image_resizer.py -i /path/to/input_dir -o /path/to/output_dir -s 1024
```

The script will create the output directory if it does not exist.

## Options

Full usage information can be found by running the script with the `-h` flag:

```bash
python3 image_resizer.py -h
```

This will print the following help message:

```
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
                        Output format for resized images (same, png, jpg, gif, tiff and webp). Default is same.
  -n NUM_PROCESSES, --num-processes NUM_PROCESSES
                        Number of processes to use for resizing. Default is number of available CPU cores.
  -m, --add-mirror      Add a mirrored version of each image.
  -M, --mirror-only     Produce only a mirrored version of each image.
  -v, --verbose         Verbose output.
```

Following options are available to customize the resizing process:

| Option | Description |
| --- | --- |
| `-h`, `--help` | **Show this help message and exit.** The script will print the help message and exit. |
| `-i`, `--input` | **Input directory containing images.** The script finds all JPEG and PNG images for processing. |
| `-o`, `--output` | **Output directory to store resized images.** The script will keep the same directory structure in the output directory as in the input directory. |
| `-s`, `--size` | **Size to resize the images. Default is `512`.** The default value is chosen to be use with stable diffusion 1.5. For stable diffusion XL use size of `1024`. |
| `-r`, `--resize-mode` | **Resize mode for images (`thumbnail`, `cover` or `crop`). Default is thumbnail.** The resize modes are covering different use cases. <ul><li> `thumbnail` wants to resize original image to fit in `size`x`size` square, this means the smaller side of the output image will be smaller then `size`. </li><li> `cover` wants to cover `size`x`size` square, the bigger side of the image will be bigger then the `size`. </li><li> `crop` will act as `cover` and crop the output image to `size`x`size` square. </li></ul> |
| `-f`, `--format` | **Output format for resized images (`same`, `png`, `jpg`, `gif`, `tiff` and `webp`). Default is same.** The script can additionally produce output in specific image format. <ul><li> `same` will save output files in original image format. </li><li> `png` will convert images to PNG format. </li><li> `jpg` will generate JPEG output files. </li><li> `gif` will generate GIF output files. </li><li> `tiff` will generate TIFF output files. </li><li> `webp` will generate WEBP output files. </li></ul> |
| `-n`, `--num-processes` | **Number of processes to use for resizing. Default is number of available CPU cores.** The script will use multiprocessing to speed up the resizing process. |
| `-m`, `--add-mirror` | **Add a mirrored version of each image.** The script will add a mirrored version of each image to the output directory. The mirrored file will be saved with following name format `<original_image>_mirror.<ext>`. The idea of adding mirrored versions of the images to your training dataset is to remove biases from your input images. |
| `-M`, `--mirror-only` | **Produce only a mirrored version of each image.** The script will produce only a mirrored version of each image to the output directory. This option can be used to add mirrored images to existing output directory tree. |
| `-v`, `--verbose` | **Verbose output.** The script will print more information about the processing. Adding more `-v` options will increase information you will see during directory resizing. |

## How You Can Contribute

We welcome your contributions to the ag-panel project! Whether it's code, resources, or financial support, your help is invaluable. Feel free to reach out directly via email at andriy.golovnya@gmail.com or through my [GitHub profile](https://github.com/red-scorp).

If you'd like to make a financial contribution to support the project's development, you can donate via [PayPal](http://paypal.me/redscorp) or [Ko-Fi](http://ko-fi.com/redscorp). Your generosity is greatly appreciated.

Thank you in advance for your support, and let's make the ag-panel project even better together!
