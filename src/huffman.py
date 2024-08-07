import heapq as hq
import pickle
import os
import time
import struct
from collections import Counter
from functools import wraps
from utils import detailed_report


import cProfile
import pstats

def timing_and_profiling(f):
    @wraps(f)
    def wrap(*args, **kw):
        profiler = cProfile.Profile()
        profiler.enable()
        ts = time.time()
        result = f(*args, **kw)
        te = time.time()
        profiler.disable()
        execution_time = te - ts
        stats = pstats.Stats(profiler)
        stats.strip_dirs()
        stats.sort_stats("cumulative")
        stats.print_stats()
        return execution_time
    return wrap


class huffman_node:
    def __init__(self, char, freq, left=None, right=None):
        self.left = left
        self.right = right
        self.char = char
        self.freq = freq

    def __lt__(self, other):
        return self.freq < other.freq

    def __le__(self, other):
        return self.freq <= other.freq

    def __gt__(self, other):
        return self.freq > other.freq

    def __ge__(self, other):
        return self.freq >= other.freq

    def __eq__(self, other):
        return self.freq == other.freq

    def __ne__(self, other):
        return self.freq != other.freq
        
def print_huffman_tree(node, indent="", is_left=True):
    if node is not None:
        print(indent, end="")
        if is_left:
            print("L----", end="")
            indent += "|    "
        else:
            print("R----", end="")
            indent += "     "

        print(f"{repr(node.char)} ({repr(node.freq)})")
        print_huffman_tree(node.left, indent, True)
        print_huffman_tree(node.right, indent, False)

class HuffmanCompressor:

    def create_huffman_tree(self, huffman_table):
        heap = [huffman_node(char, freq) for char, freq in huffman_table]
        hq.heapify(heap)
        node_stack = list()
        root = None
        # for node in node_stack:
        #     print(f"{repr(node.char)} appears {node.freq} time(s)")
        if len(heap) == 0:
            print("Error: Huffman table with length 0 not allowed")
        while len(heap) != 1:
            left = hq.heappop(heap)
            right = hq.heappop(heap)
            internal_node = huffman_node(char=None, freq=left.freq + right.freq, left=left, right=right)
            hq.heappush(heap, internal_node)
            # for node in node_stack:
            #     print(f"{repr(node.char)} appears {node.freq} time(s)")
        root = hq.heappop(heap)
        return root

    def create_encoding_table(self, node, bit='', encoding_table={}):
        if (node.char is not None): # base case
            encoding_table[node.char] = bit
        if (node.left is not None):
            self.create_encoding_table(node.left, bit = f'{bit}0', encoding_table=encoding_table)
        if (node.right is not None):
            self.create_encoding_table(node.right, bit = f'{bit}1', encoding_table=encoding_table)
        return encoding_table

    def resolve_same_frequency(self, incomplete_table):
        current_freq = 0
        current_pairs = list()
        resolved_table = list()
        for entry in incomplete_table:
            if entry[1] != current_freq: # handle frequency not being the same as the current frequency
                if not current_pairs: # handle empty current_pairs list
                    current_pairs.append(entry)
                    current_freq = entry[1]
                else: # handle adding current pairs to resolved pairs and clearing the list
                    current_pairs.sort(key=lambda tup: tup[0])
                    resolved_table.extend(current_pairs) # sorts in place
                    current_pairs.clear()
                    current_pairs.append(entry)
                    current_freq = entry[1]
            else:
                current_pairs.append(entry)
        
        current_pairs.sort(key=lambda tup: tup[0])
        resolved_table.extend(current_pairs) # sorts in place
        return resolved_table

    def serialize_huffman_tree(self, pairs):
        serialized_end = b'\x00\x00\x00\x00'
        serialzed_tree = bytearray()
        for pair in pairs:
            serialzed_tree.extend(struct.pack('<BI', pair[0], pair[1]))
        serialzed_tree.extend(serialized_end)
        return serialzed_tree

        

    def deserialize_huffman_tree(self, data, index=0):
        if index >= len(data):
            return None, index
        if data[index] == '1':
            return huffman_node(char=data[index + 1], freq=0), index + 2
        left, next_index = self.deserialize_huffman_tree(data, index + 1)
        right, next_index = self.deserialize_huffman_tree(data, next_index)
        return huffman_node(char=None, freq=0, left=left, right=right), next_index

    # @timing_and_profiling
    def compress_bin(self, folder_path, input_file):
        start_time = time.time()
        # Count byte frequencies
        d = dict()
        with open(f"{folder_path}/{input_file}", 'rb') as file:
            pairs = list(Counter(file.read()).items())
        pairs.sort(key=lambda x: x[1]) 

        # Create tree and encoding table
        tree = self.create_huffman_tree(pairs)
        encoding_table = self.create_encoding_table(tree)
        # Serialize the Huffman tree
        serialized_tree = self. serialize_huffman_tree(pairs)

        # Generate bit string
        bit_list = []
        with open(f"{folder_path}/{input_file}", 'rb') as file:
            while (chunk := file.read(4096)):  # Read in chunks
                for byte in chunk:
                    bit_list.append(encoding_table[byte])

        bit_string = ''.join(bit_list)
        # Add byte at beginning to indicate padding amount
        pad_amount = 8 - (len(bit_string) % 8)
        pad_byte = bytearray()
        pad_byte.extend(struct.pack('B', pad_amount))
        byte_array = bytearray()

        for i in range(0, len(bit_string), 8):
            byte_chunk = bit_string[i:i + 8]
            if len(byte_chunk) < 8:
                byte_chunk = byte_chunk.ljust(8, '0')  # Pad the last byte if necessary
            byte_array.append(int(byte_chunk, 2))

        # Write the serialized tree and compressed data to file
        with open(f"{folder_path}/{input_file}.enc", 'wb') as file:
            file.write(pad_byte)  # Write the padding byte
            file.write(serialized_tree)  # Write the serialized tree
            file.write(byte_array)  # Write the compressed data

        total_time = time.time() - start_time
        return total_time

    def compress(self,folder_path, input_file):
        start_time = time.time()
        # Count character frequencies
        with open(f"{folder_path}{input_file}", 'r') as file:
            pairs = list(Counter(file.read()).items())
        pairs.sort(key=lambda x: x[1]) 

        # Create tree and encoding table
        tree = self.create_huffman_tree(pairs)
        encoding_table = self.create_encoding_table(tree)

        serialized_tree = self.serialize_huffman_tree(pairs)

        # Generate bit string
        bit_string = ''
        with open(f"{folder_path}/{input_file}", 'r') as file:
            for line in file:
                for char in line:
                    bit_string += encoding_table[char]

        # Convert to byte array
        byte_array = bytearray()
        for i in range(0, len(bit_string), 8):
            byte_chunk = bit_string[i:i + 8]
            if len(byte_chunk) < 8:
                byte_chunk = byte_chunk.ljust(8, '0')  # Pad the last byte if necessary
            byte_array.append(int(byte_chunk, 2))

        # Write the serialized tree and enc data to file
        with open(f"{folder_path}/{input_file}.enc", 'wb') as file:
            file.write(serialized_tree)  # Write the serialized tree
            file.write(byte_array)  # Write the enc data

        total_time = time.time() - start_time
        return total_time


        # except Exception as e:
        #     print(f"An error occurred during encoding: {e}")
        #     return 0


    # def decompress(self, folder_path, enc_file):
    #     # Read the serialized tree and enc data from the file
    #     with open(f"{folder_path}{enc_file}.enc", 'rb') as file:
    #         enc_data = file.read()  # Read the rest of the file (enc data)

    #     pairs = list()
    #     # Deserialize the Huffman tree
    #     while enc_data[0:4] != b'\x00\x00\x00\x00':
    #         char, freq = struct.unpack('<BI', enc_data[:5])
    #         enc_data = enc_data[5:]
    #         pairs.append((chr(char), freq))

    #     enc_data = enc_data[4:]  # Skip the serialized tree end marker

    #     # Convert byte array to bit string
    #     bit_string = ''.join(f'{byte:08b}' for byte in enc_data)

    #     # decompress bit string using Huffman tree
    #     tree = self.create_huffman_tree(pairs)
    #     node = tree
    #     dec_output = []
    #     for bit in bit_string:
    #         node = node.left if bit == '0' else node.right

    #         if node.char is not None:
    #             dec_output.append(node.char)
    #             node = tree

    #     with open(f"{folder_path}{enc_file}.dec", 'w') as file:
    #         file.write(''.join(dec_output))
    
    def decompress(self, folder_path, enc_file):
        # Read the serialized tree and enc data from the file
        with open(os.path.join(folder_path, f"{enc_file}.enc"), 'rb') as file:
            enc_data = file.read()  # Read the rest of the file (enc data)


        # Read padding length
        padding_length = enc_data[0]
        enc_data = enc_data[1:]

        pairs = list()
        # Deserialize the Huffman tree
        while enc_data[:4] != b'\x00\x00\x00\x00':
            char, freq = struct.unpack('<BI', enc_data[:5])
            enc_data = enc_data[5:]
            pairs.append((char, freq))

        enc_data = enc_data[4:]  # Skip the serialized tree end marker

        # Create Huffman tree from pairs
        tree = self.create_huffman_tree(pairs)

        # Remove padding bits from the last byte
        if padding_length > 0:
            enc_data = enc_data[:-1] + bytes([enc_data[-1] >> padding_length << padding_length])

        # Decompress the data
        node = tree
        dec_output = bytearray()
        for byte in enc_data:
            for bit_pos in range(8):
                bit = (byte >> (7 - bit_pos)) & 1
                node = node.left if bit == 0 else node.right
                if node.char is not None:
                    dec_output.append(node.char)
                    node = tree

        # Write the decompressed data to a file
        with open(os.path.join(folder_path, f"{enc_file}.dec"), 'wb') as file:
            file.write(dec_output)

        return dec_output

    def test(self, folder_path, input_file):
        # if input_file.endswith('.enc'):
        #     print("File already compressd.")
        #     return
        if input_file.endswith('.txt'):
            compression_time = self.compress(folder_path, input_file)
            decompression_time = self.decompress(folder_path, input_file)
        else:   
            compression_time = self.compress_bin(folder_path, input_file)
            decompression_time = self.decompress(folder_path, input_file)
        detailed_report("Huffman", f"{folder_path}{input_file}", compression_time, 0)    
