# Edge-Based Image Compression with Homogeneous Diffusion

## Directory Structure

```
homogeneous_diffusion/
├── images/
│   ├── image1.png
│   ├── image2.png
│   ├── image3.png
│   ├── image4.png
│   ├── image5.png
├── utils/
│   ├── contours.py
│   ├── decoder.py
│   ├── homogeneous_diffusion.py
│   ├── marr_hildreth.py
│   ├── storage.py
├── compressor.py
├── decompressor.py
├── paper.pdf
└── README.md
```

## Instructions

### Compress an Image

To compress an image, use the `compressor.py` script. Run the following command:

```bash
python3 compressor.py image_number q d
```

Replace `image_number` with the number of the image you want to compress (1-5), `q` with the quantization parameter, and `d` with the subsampling parameter.

The compressed image will be saved in the `compressed/` directory.

### Decompress an Image

To decompress an image, use the `decompressor.py` script. Run the following command:

```bash
python3 decompressor.py compressed_file_path
```

Replace `compressed_file_path` with the path to the compressed file.

The decompressed image will be saved in the `recontructed_images/` directory.
