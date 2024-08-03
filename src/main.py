import huffman_encoder
import lz_77
import os
import sys

main_script_dir = os.path.dirname(os.path.abspath(__file__))
TEXT_PATH = os.path.join(main_script_dir, "../text_encoded_files/")

input_file = f"{TEXT_PATH}{sys.argv[1]}"

if __name__ == "__main__":
    
    # lz_77.lz77_encode(input_file)
    compressor = lz_77.LZ77Compressor(8192, 20)
    compressor.test(input_file)
    # huffman_encoder.huffman_encode(input_file)
    # with open('../text_encoded_files/bigfile.txt', 'rb') as f_in, gzip.open('compressed_file.gz', 'wb') as f_out:
    #     f_out.writelines(f_in)
    # decompression_time = decode(compressed_file, output_file)
    # detailed_report("Huffman Encoding", input_file, compressed_file, compression_time, 
                    #decompression_time)
    
