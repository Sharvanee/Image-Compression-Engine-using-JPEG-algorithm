import cv2
import numpy as np
import struct
import os
import sys
from tqdm import tqdm
import matplotlib.pyplot as plt
import subprocess

def reconstruct_with_inpaint(edge_image, pixel_data_restored):
    """
    Reconstruct the image using OpenCV's inpainting based on known edge and pixel data.

    :param edge_image: Binary edge map (1 for edge, 0 for non-edge).
    :param pixel_data_restored: Array of dequantized pixel values (n, 5) with (x, y, R, G, B).
    :return: Inpainted image.
    """
    height, width = edge_image.shape

    inpainted_image = np.zeros((height, width, 3), dtype=np.uint8)

    mask = np.zeros((height, width), dtype=np.uint8)  # inpainting mask
    for x, y, R, G, B in pixel_data_restored:
        inpainted_image[x, y] = [B, G, R]
        mask[x, y] = 255
    mask[edge_image == 1] = 255
    mask = 255 - mask

    inpainted_image = inpainted_image.astype(np.uint8)
    mask = mask.astype(np.uint8)

    inpaint_result = cv2.inpaint(inpainted_image, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)

    return inpaint_result


def deserialize_pixel_data(serialized_data):
    """
    Deserialize binary data into a list of (x, y, R, G, B) tuples.
    """
    pixel_data = []
    tuple_size = struct.calcsize("HHBBB")
    for i in range(0, len(serialized_data), tuple_size):
        x, y, R, G, B = struct.unpack("HHBBB", serialized_data[i:i + tuple_size])
        pixel_data.append((x, y, R, G, B))
    return pixel_data


def decompress_with_paq(input_file, temp_file):
    """
    Decompress data using PAQ8o6.
    :param input_file: Path to the compressed file.
    :param temp_file: Path to save the decompressed binary data.
    """
    subprocess.run(["paq8o6_64", "-d", input_file], check=True)
    decompressed_file = "recovered/temp.bin"
    os.rename(decompressed_file, temp_file)


def display_pixel_data(pixel_data_restored, height, width):
    """
    Create an image from the pixel data and display it.

    :param pixel_data_restored: Array of (x, y, R, G, B) tuples.
    :param height: Height of the image.
    :param width: Width of the image.
    :return: Image created from pixel data.
    """
    pixel_image = np.zeros((height, width, 3), dtype=np.uint8)

    for x, y, R, G, B in pixel_data_restored:
        if 0 <= x < height and 0 <= y < width:
            pixel_image[x, y] = [B, G, R]

    return pixel_image


def main():
    if len(sys.argv) != 4:
        print("Usage: python3 decoder.py <contour_paq_file> <edge_pbm_file> <image_number>")
        sys.exit(1)

    contour_paq_file = sys.argv[1]
    edge_pbm_file = sys.argv[2]
    image_number = sys.argv[3]

    # loading the compressed pixel data
    decompress_with_paq(contour_paq_file, "decompressed.bin")
    with open("decompressed.bin", "rb") as f:
        decompressed_data = f.read()
    pixel_data_restored = np.array(deserialize_pixel_data(decompressed_data))
    os.remove("decompressed.bin")

    # loading edge map
    edge_image = cv2.imread(edge_pbm_file, cv2.IMREAD_GRAYSCALE)
    edge_image = (edge_image > 0).astype(np.uint8)

    # reconstruction
    reconstructed_image = reconstruct_with_inpaint(edge_image, pixel_data_restored)

    output_dir = "reconstructed_images"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"reconstructed_image{image_number}.png")
    cv2.imwrite(output_path, reconstructed_image)

    plt.figure(figsize=(5, 5))
    plt.title("Reconstructed Image")
    plt.imshow(cv2.cvtColor(reconstructed_image, cv2.COLOR_BGR2RGB))
    plt.axis("off")
    plt.show()

if __name__ == "__main__":
    main()
