"""Converter main interface"""

import logging
import os

import nibabel as nib
import numpy as np
import PIL
from PIL import ImageOps

log = logging.getLogger(__name__)


def set_min_max_threshold_value(image_data, threshold_percentile):
    """This function set the image data that is either above or below the threshold value
    to the corresponding threshold value.

    Args:
        image_data (numpy.ndarray): A 2D numpy array representation of an image
        threshold_percentile (float): The percentile cutoff for maximum values

    Returns:
        numpy.ndarray: Updated 2D numpy array representation of an image
    """
    try:
        log.info("Getting the threshold value for the NIfTi file.")

        # determine value at threshold_percentile
        max_threshold_value = np.percentile(image_data, threshold_percentile)
        min_threshold_value = np.percentile(image_data, 100 - threshold_percentile)

        # replace values on the image with threshold_value
        image_data[image_data < min_threshold_value] = min_threshold_value
        image_data[image_data > max_threshold_value] = max_threshold_value

    except ValueError:
        log.error("Percentiles must be in the range [0, 100]")

    except Exception as e:
        log.error(
            f"Unable to determine the threshold percentile. Details: {e}",
            exc_info=True,
        )

    return image_data


def scale_image_data(image_data):
    log.info("Scaling the image data...")
    # scale to 255 for PIL import
    return (
        (image_data - image_data.min()) * 255 / (image_data.max() - image_data.min())
    ).astype(np.uint8)


def process_mips(image_data, threshold_percentile, invert_image):
    """This is a function processes MIPs 2D numpy arrays.

    Args:
        image_data (numpy.ndarray): A 2D numpy array representation of an image
        threshold_percentile (float): The percentile cutoff for maximum values
        invert_image (bool): Invert the colors of image file. Default True.

    Returns:
        PIL.Image: A PIL object that can be saves as an image file

    """
    updated_image_data = set_min_max_threshold_value(image_data, threshold_percentile)

    updated_image_data = scale_image_data(updated_image_data)
    # convert to PIL object for image operations
    img = PIL.Image.fromarray(updated_image_data)

    if invert_image:
        log.info("Inverting the image....")
        # invert image (black to white)
        img = ImageOps.invert(img)

    # resize image and rotate 90 degrees counter-clockwise
    log.info("Resizing the image....")
    img = img.rotate(90)

    return img


def create_mips_file_name(filename, file_type):
    output_string = filename.split(".nii")[0]
    output_string = output_string + "_" + file_type

    return output_string


def get_image_slices_data(image_data):
    # compute MIPS for each cardinal direction
    sagittal = np.amax(image_data, 0)
    coronal = np.amax(image_data, 1)
    axial = np.amax(image_data, 2)

    return sagittal, coronal, axial


def check_nifti_dimension(nifti_image_shape):
    if (
        all(isinstance(v, int) for v in nifti_image_shape)
        and len(nifti_image_shape) == 3
    ):
        return True
    else:
        return False


def run(output_folder, filepath, filename, threshold_percentile, invert_image):
    log.info(f"Loading nifti file - {filepath}")
    try:
        # load the nifti image
        nifti_file = nib.load(filepath)
    except nib.filebasedimages.ImageFileError as e:
        log.error(f"Error occured. Detail: {e}", exc_info=True)
        os.sys.exit(1)
    else:
        if check_nifti_dimension(nifti_file.shape):
            # get np 3D np array from nifti_file
            image_data = nifti_file.get_fdata()

            sagittal, coronal, axial = get_image_slices_data(image_data)

            # threshold MIPS
            sagittal = process_mips(sagittal, threshold_percentile, invert_image)
            coronal = process_mips(coronal, threshold_percentile, invert_image)
            axial = process_mips(axial, threshold_percentile, invert_image)

            try:
                log.info("Exporting images as PNG format...")
                # save images in PNG format
                sagittal.save(
                    os.path.join(
                        output_folder,
                        create_mips_file_name(filename, "MIPs_sag.png"),
                    ),
                    "PNG",
                )
                coronal.save(
                    os.path.join(
                        output_folder,
                        create_mips_file_name(filename, "MIPs_cor.png"),
                    ),
                    "PNG",
                )
                axial.save(
                    os.path.join(
                        output_folder,
                        create_mips_file_name(filename, "MIPs_ax.png"),
                    ),
                    "PNG",
                )
            except Exception as e:
                log.error(f"Unable to save the image. Detail: {e}", exc_info=True)
                os.sys.exit(1)

            else:
                log.info("Succesfully converted image into MIPS...")
                return 0  # success status code

        else:
            log.error("Required 3D nifit image to be converted to a MIPS format.")
            log.info("Exiting....")
            return 1  # error status code
