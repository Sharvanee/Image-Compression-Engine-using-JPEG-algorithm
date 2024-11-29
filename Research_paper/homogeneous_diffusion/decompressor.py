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
    if len(sys.argv) != 2:
        print("Usage: python3 decompressor.py <compressed file>")
        sys.exit(1)

    compressed_file = sys.argv[1]
    image_number = int(compressed_file.split("out")[1].split(".bin")[0])

    for folder in ["reconstructed_images", "recovered"]:
        if not os.path.exists(folder):
            os.makedirs(folder)
        
    recovered_contours = f"recovered/contours{image_number}.paq8o6"
    recovered_edges = f"recovered/edges{image_number}.jbg"
    recovered_edges_pbm = f"recovered/edges{image_number}.pbm"

    # Decompress with decoder.py
    run_command(["python3", "utils/decoder.py", compressed_file, recovered_edges, recovered_contours])
    print("Decompression completed.")

    # Reconstruct using homogeneous_diffusion.py
    run_command(["python3", "utils/homogeneous_diffusion.py", recovered_contours, recovered_edges_pbm, str(image_number)])

    print(f"Reconstructed image number {image_number}.")

if __name__ == "__main__":
    main()