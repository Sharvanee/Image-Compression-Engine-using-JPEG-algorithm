import struct
import sys
import subprocess
import os

def decompress_with_jbig(input_file, output_file):
    subprocess.run(["jbgtopbm", input_file, output_file], check=True)


def recover_encoded_data(encoded_file, output_jbig_file, output_paq_file):
    """
    Recover JBIG data, PAQ data, and metadata from the encoded file.

    :param encoded_file: Path to the combined encoded file.
    :param output_jbig_file: Path to save the extracted JBIG file.
    :param output_paq_file: Path to save the extracted PAQ file.
    """
    with open(encoded_file, "rb") as f:
        # metadata
        # d = struct.unpack("B", f.read(1))[0]  # subsampling parameter
        # q = struct.unpack("B", f.read(1))[0]  # quantization parameter
        jbig_size = struct.unpack("I", f.read(4))[0] # size of JBIG data
        
        # JBIG data
        jbig_data = f.read(jbig_size)

        # PAQ data
        paq_data = f.read()

    # write JBIG data to output file
    with open(output_jbig_file, "wb") as jbig_out:
        jbig_out.write(jbig_data)
    decompress_with_jbig(output_jbig_file, output_jbig_file.replace(".jbg", ".pbm"))
    os.remove(output_jbig_file)

    # write PAQ data to output file
    with open(output_paq_file, "wb") as paq_out:
        paq_out.write(paq_data)


def main():
    if len(sys.argv) != 4:
        print("Usage: python decoder.py <encoded_file> <output_jbig_file> <output_paq_file>")
        sys.exit(1)

    encoded_path = sys.argv[1]
    output_jbig_path = sys.argv[2]
    output_paq_path = sys.argv[3]   

    recover_encoded_data(encoded_path, output_jbig_path, output_paq_path)


if __name__ == "__main__":
    main()
