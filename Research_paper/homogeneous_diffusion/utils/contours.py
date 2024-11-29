import subprocess
import struct
import os
import numpy as np
import cv2
import sys
import matplotlib.pyplot as plt

def create_colored_contour_image(edge_image, pixel_data_restored):
    """
    Create a colored contour image by overlaying sampled pixel colors on the edges.
    
    :param edge_image: Binary edge image (2D).
    :param pixel_data_restored: Array with (x, y, R, G, B) values for sampled pixels.
    :return: Colored contour image (3D).
    """
    colored_contour_image = np.zeros((edge_image.shape[0], edge_image.shape[1], 3), dtype=np.uint8)
    
    # colored_contour_image[edge_image == 1] = [255, 255, 255]  # White for edge pixels
    # colored_contour_image = 255 - colored_contour_image  # Invert colors for better visualization

    for x, y, R, G, B in pixel_data_restored:
        if 0 <= x < colored_contour_image.shape[0] and 0 <= y < colored_contour_image.shape[1]:
            colored_contour_image[x, y] = [R, G, B]  # Assign color from pixel_data_restored

    return colored_contour_image

def get_adjacent_indices(image, edges):
    """
    Extract pixel values adjacent to detected edges.
    :param image: 3D array of the original image
    :param edges: Binary edge map (1 for edge, 0 for non-edge)
    :return: List of pixel values adjacent to edges
    """

    gap = 3    # specifies the window around edges to consider as adjacent pixels
    directions = [(dx, dy) for dx in range(-gap, gap + 1) for dy in range(-gap, gap + 1) if dx != 0 or dy != 0]
    indices = []

    for x, y in zip(*np.where(edges == 1)):  # Edge positions
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < image.shape[0] and 0 <= ny < image.shape[1] and edges[nx, ny] == 0:
                indices.append([nx, ny])

    # returns unique indices
    return list(set(map(tuple, indices)))


def quantize_pixel_values(pixel_values, q):
    """
    Quantize pixel values to reduce the number of unique values.
    :param pixel_values: List of pixel values
    :param q: Quantization parameter
    :return: Quantized pixel values
    """
    quantized_values = []
    for value in pixel_values:
        R, G, B = value
        R_quantized = np.round(R / (256 / (2 ** q))) * (256 / (2 ** q))
        G_quantized = np.round(G / (256 / (2 ** q))) * (256 / (2 ** q))
        B_quantized = np.round(B / (256 / (2 ** q))) * (256 / (2 ** q))
        quantized_values.append((R_quantized, G_quantized, B_quantized))
    return quantized_values


def subsample_indices(indices, d):
    """
    Subsample pixel values at a specified interval.
    :param pixel_values: List of pixel values
    :param d: Subsampling distance
    :return: Subsampled pixel values
    """
    return indices[::d]


def encode_contour_pixel_values(image, edges, q, d):
    """
    Encode pixel values adjacent to edges using quantization and subsampling.
    :param image: 2D array of the original image
    :param edges: Binary edge map (1 for edge, 0 for non-edge)
    :param q: Quantization parameter
    :param d: Subsampling distance
    :return: Encoded pixel data
    """
    adjacent_values = get_adjacent_indices(image, edges)

    subsampled_indices = subsample_indices(adjacent_values, d)

    subsampled_values = []
    for idx in subsampled_indices:
        x, y = idx
        R, G, B = image[x, y]
        subsampled_values.append((x, y, R, G, B))

    return np.array(subsampled_values)


def serialize_pixel_data(pixel_data):
    """
    Serialize a list of (x, y, R, G, B) tuples into binary format.
    """
    serialized = bytearray()
    for x, y, R, G, B in pixel_data:
        serialized.extend(struct.pack("HHBBB", x, y, R, G, B))  # H for uint16, B for uint8
    return bytes(serialized)


def compress_with_paq(data, temp_file, output_file):
    """
    Compress binary data using PAQ8o6.
    """
    with open(temp_file, "wb") as temp:
        temp.write(data)
    
    subprocess.run(["paq8o6_64", temp_file], check=True)
    os.rename(f"{temp_file}.paq8o6", os.path.join("tmp", output_file))
    os.remove(temp_file)


if __name__ == "__main__":

    if len(sys.argv) != 5:
        print("Usage: python contours.py <path_to_image.png> <path_to_edges.pbm> <q> <d>")
        sys.exit(1)

    image_path = sys.argv[1]
    edges_path = sys.argv[2]
    q = int(sys.argv[3])
    d = int(sys.argv[4])

    # read in the image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Unable to read image from {image_path}")
        sys.exit(1)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # read in the edge map in binary form
    edges = cv2.imread(edges_path, cv2.IMREAD_GRAYSCALE)
    if edges is None:
        print(f"Error: Unable to read edges from {edges_path}")
        sys.exit(1)
    edges = (edges > 0).astype(int)

    quantized_values = encode_contour_pixel_values(image, edges, q, d)

    # convert quantized_values to a list of 5-element tuples and compress
    quantized_data_list = [tuple(row) for row in quantized_values]
    serialized_data = serialize_pixel_data(quantized_data_list)
    compress_with_paq(serialized_data, "temp.bin", "compressed.paq8o6")

    colored_contour_image = create_colored_contour_image(edges, quantized_values)
    plt.figure(figsize=(10, 10))
    plt.imshow(colored_contour_image)
    plt.title('Colored Contour Image')
    plt.axis('off')
    plt.show()

    #################################
    # to visualize the edges being extracted and ensure they are satisfactory
    # def overlay_edges_on_image(image, edges):
    #     """
    #     Overlay edges on the original image in red color.
        
    #     :param image: Original image (3D).
    #     :param edges: Binary edge image (2D).
    #     :return: Image with edges overlaid in red.
    #     """
    #     overlay_image = image.copy()
    #     overlay_image[edges == 1] = [255, 0, 0]  # Red color for edges
    #     return overlay_image

    
    # overlay_image = overlay_edges_on_image(image, edges)

    # fig, ax = plt.subplots(figsize=(10, 10))
    # ax.imshow(overlay_image)
    # ax.set_title('Original Image with Edges Overlaid')
    # ax.axis('off')
    # plt.show()
    #################################
