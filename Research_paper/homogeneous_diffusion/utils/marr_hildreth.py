#!/usr/bin/env python

import argparse
import numpy as np
import skimage.io as io
import matplotlib.pyplot as plt
from skimage import color
from skimage.util import img_as_ubyte
from scipy.ndimage import gaussian_laplace


def marr_hildreth_edge_detection(img, sigma, threshold=0.01):
    """
    Perform Marr-Hildreth edge detection with adjustable sensitivity.
    
    Parameters:
        img (ndarray): Grayscale input image.
        sigma (float): Sigma value for the Gaussian filter.
        threshold (float): Threshold for LoG values to reduce sensitivity.

    Returns:
        log_image (ndarray): Laplacian of Gaussian image.
        zero_crossing (ndarray): Binary edge-detected image.
    """
    # LoG step with thresholding
    log_image = gaussian_laplace(img, sigma=sigma)
    log_image[np.abs(log_image) < threshold] = 0

    # computing zero crossings in 3x3 neighborhood
    zero_crossing = np.zeros_like(log_image, dtype=np.uint8)
    rows, cols = log_image.shape

    for i in range(1, rows - 1):
        for j in range(1, cols - 1):
            patch = log_image[i - 1:i + 2, j - 1:j + 2]
            if np.min(patch) < 0 < np.max(patch):
                zero_crossing[i, j] = 255

    return log_image, zero_crossing


def main():
    parser = argparse.ArgumentParser(description="Marr-Hildreth Edge Detector")
    parser.add_argument("--input", required=True, help="Path to the input image (PNG format).")
    parser.add_argument("--output", required=True, help="Path to the output edge-detected image.")
    parser.add_argument("--sigma", type=float, default=3.0, help="Sigma value for Gaussian filter.")
    parser.add_argument("--threshold", type=float, default=0.0005, help="Threshold for edge sensitivity.")
    args = parser.parse_args()

    # loading the input image
    img = io.imread(args.input)

    # discarding alpha channel if applicable
    if img.shape[-1] == 4:
        img = img[..., :3]
    if img.ndim == 3:
        img = color.rgb2gray(img)

    log_image, edges = marr_hildreth_edge_detection(img, args.sigma, args.threshold)

    # Save the edge-detected image
    io.imsave(args.output, img_as_ubyte(edges))

    # Plot the results
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    axes[0].imshow(img, cmap="gray")
    axes[0].set_title("Original Image")
    axes[1].imshow(edges, cmap="gray")
    axes[1].set_title("Edges (Zero Crossings)")
    for ax in axes:
        ax.axis("off")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
