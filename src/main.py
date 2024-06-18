from huffman_encoder import *
import os
import sys

main_script_dir = os.path.dirname(os.path.abspath(__file__))
TEXT_PATH = os.path.join(main_script_dir, "../text_encoded_files/")

input_file = f"{TEXT_PATH}{sys.argv[1]}"
compressed_file = f"{TEXT_PATH}encoded_file.bin"
output_file = f"{TEXT_PATH}output.txt"

if __name__ == "__main__":
    encode(input_file, compressed_file)
    decode(compressed_file, output_file)
    detailed_report(input_file, compressed_file)
