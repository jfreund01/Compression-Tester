import huffman
import lz_77
import os
import glob
from time import time
from functools import wraps
from utils import detailed_report

def timing(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = time()
        f(*args, **kw)
        te = time()
        execution_time = te - ts
        return execution_time
    return wrap


class DeflateCompressor:

    def __init__(self, search_buffer_size, lookup_buffer_size, block_number):
        self.huffman = huffman.HuffmanCompressor()
        self.lz_77 = lz_77.LZ77Compressor(search_buffer_size, lookup_buffer_size, block_number)
    


    @timing
    def compress(self, folder_path, input_file):
        lz_77_comp = self.lz_77.compress(folder_path, input_file)
        huffman = self.huffman.compress_bin(folder_path, f"{input_file}.enc")
        comp_time = lz_77_comp + huffman
        return comp_time
    
    @timing
    def decompress(self, folder_path, input_file):
        huffman_decomp = self.huffman.decompress(folder_path, f"{input_file}.enc")
        lz_77_decomp = self.lz_77.decompress(folder_path, f"{input_file}")
        # decomp_time = lz_77_decomp + huffman_decomp
        # return decomp_time

    def test(self, folder_path, input_file):
        comp_time = self.compress(folder_path, input_file)
        decomp_time = 0
        decomp_time = self.decompress(folder_path, input_file)
        detailed_report("Deflate", f"{folder_path}{input_file}", comp_time, decomp_time, output_file=f"{folder_path}{input_file}.enc.enc")    
        # for hgx in glob.glob(f"{folder_path}{input_file}.*"):
        #     os.remove(hgx)