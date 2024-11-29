import struct
import os
import sys
import subprocess

def compress_with_jbig(input_file, output_file):
    subprocess.run(["pbmtojbg", input_file, output_file], check=True)

def store_encoded_data(pbm_file, paq_file, output_file, q, d):
    """
    Combine JBIG data, PAQ data, and metadata into the final encoded file.
    
    :param jbig_file: Path to the JBIG-encoded contour file.
    :param paq_file: Path to the PAQ-compressed pixel values file.
    :param output_file: Path to the final output encoded file.
    :param q: Quantization parameter.
    :param d: Sampling distance.
    :param channels: Number of color channels (1 for grayscale, 3 for RGB).
    """

    jbig_file = os.path.splitext(pbm_file)[0] + ".jbg"
    compress_with_jbig(pbm_file, jbig_file)

    # read JBIG and PAQ data
    with open(jbig_file, "rb") as f:
        jbig_data = f.read()
    
    with open(paq_file, "rb") as f:
        paq_data = f.read()

    with open(output_file, "wb") as f:
        # metadata
        # f.write(struct.pack("B", d))             # subsampling parameter (1 byte)    
        # f.write(struct.pack("B", q))             # quantization parameter (1 byte)        
        f.write(struct.pack("I", len(jbig_data)))  # Size of JBIG data (4 bytes)
        
        # JBIG data
        f.write(jbig_data)                
        f.write(paq_data)

    print(f"Encoded data stored in {output_file}")


def main():
    
    if len(sys.argv) != 6:
        print("Usage: python storage.py <jbig_file> <paq_file> <output_file> <q> <d>")
        sys.exit(1)

    jbig_path = sys.argv[1]
    paq_path = sys.argv[2]
    out_path = sys.argv[3]
    q = int(sys.argv[4])
    d = int(sys.argv[5])
    
    store_encoded_data(jbig_path, paq_path, out_path, q, d)

if __name__ == "__main__":
    main()