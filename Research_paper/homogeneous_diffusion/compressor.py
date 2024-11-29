import subprocess
import sys
import os

def run_command(command):
    """
    Run a shell command and handle errors.
    :param command: The command to run as a list of strings.
    """
    try:
        print(f"Running: {' '.join(command)}")
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: Command '{' '.join(command)}' failed with exit code {e.returncode}")
        sys.exit(e.returncode)


def main():
    if len(sys.argv) != 4:
        print("Usage: python3 compressor.py <image_number> <q> <d>")
        sys.exit(1)

    # assumes the input image is stored as inputs/image{image_number}.png
    image_number = sys.argv[1]
    base_name = f"image{image_number}"
    q = sys.argv[2]
    d = sys.argv[3]

    for folder in ["edges", "tmp", "compressed"]:
        if not os.path.exists(folder):
            os.makedirs(folder)
    
    # file paths
    input_image = f"images/{base_name}.png"
    edge_output = f"edges/edges{image_number}.pbm"
    temp_compressed_file = f"tmp/compressed.paq8o6"
    compressed_file = f"compressed/out{image_number}.bin"

    # check if input image exists
    if not os.path.exists(input_image):
        print(f"Error: Input image {input_image} does not exist.")
        sys.exit(1)

    # Marr-Hildreth edge detection
    run_command(["python3", "utils/marr_hildreth.py", "--input", input_image, "--output", edge_output])
    print("Marr-Hildreth edge detection completed.")

    # Extract contours
    run_command(["python3", "utils/contours.py", input_image, edge_output, q, d])
    print("Contours extraction completed.")

    # Compress using storage.py
    run_command(["python3", "utils/storage.py", edge_output, temp_compressed_file, compressed_file, q, d])
    print("Compression completed.")

    print(f"Compressed image stored in {compressed_file}.")

if __name__ == "__main__":
    main()