import huffman
import lz_77
import deflate
import os
import sys

main_script_dir = os.path.dirname(os.path.abspath(__file__))
TEXT_PATH = os.path.expanduser("~/Compression-Tester/text_encoded_files/")

input_file = sys.argv[1]
if __name__ == "__main__":
    # huffman_compressor = huffman.HuffmanCompressor()
    # huffman_compressor.compress_bin(TEXT_PATH, input_file)
    # huffman_compressor = huffman.HuffmanCompressor()
    # huffman_compressor.test(TEXT_PATH, input_file)
    # lz_77_compressor = lz_77.LZ77Compressor(65536, 20, 1)
    # lz_77_compressor.compress(TEXT_PATH, input_file)
    # lz_77_compressor.test(TEXT_PATH, input_file)
    deflate_compressor = deflate.DeflateCompressor(8192, 20, 3)
    deflate_compressor.test(TEXT_PATH, input_file)
    