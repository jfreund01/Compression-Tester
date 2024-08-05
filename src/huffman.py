import heapq as hq
import pickle
import os
import time
import struct
from utils import detailed_report

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
            # print()
            # print()
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
            serialzed_tree.extend(struct.pack('<II', ord(pair[0]), pair[1]))
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

    def compress_bin(self, folder_path, input_file):
        start_time = time.time()
        # Count byte frequencies
        d = dict()
        with open(f"{folder_path}/{input_file}", 'rb') as file:
            byte = file.read(1)
            while byte:
                if byte not in d:
                    d[byte] = 1
                else:
                    d[byte] += 1
                byte = file.read(1)
        
        # Sort by frequency
        pairs = list(d.items())
        pairs.sort(key=lambda x: x[1]) 

        # Create tree and encoding table
        tree = self.create_huffman_tree(pairs)
        encoding_table = self.create_encoding_table(tree)

        # Serialize the Huffman tree
        serialized_tree = self. serialize_huffman_tree(pairs)

        # Generate bit string
        bit_string = ''
        with open(f"{folder_path}/{input_file}", 'rb') as file:
            byte = file.read(1)
            while byte:
                bit_string += encoding_table[byte]
                byte = file.read(1)

        # Convert to byte array
        byte_array = bytearray()
        for i in range(0, len(bit_string), 8):
            byte_chunk = bit_string[i:i + 8]
            if len(byte_chunk) < 8:
                byte_chunk = byte_chunk.ljust(8, '0')  # Pad the last byte if necessary
            byte_array.append(int(byte_chunk, 2))

        # Write the serialized tree and compressed data to file
        with open(f"{folder_path}/{input_file}.enc", 'wb') as file:
            file.write(serialized_tree)  # Write the serialized tree
            file.write(byte_array)  # Write the compressed data

        print(f"Encoding complete. Compresssd file saved as '{input_file}.enc'.")
        total_time = time.time() - start_time
        return total_time

    def compress(self,folder_path, input_file):
        start_time = time.time()
        # Count character frequencies
        d = dict()
        with open(f"{folder_path}{input_file}", 'r') as file:
            for line in file:
                for character in line:
                    if character not in d:
                        d[character] = 1
                    else:
                        d[character] += 1
        # Sort by frequency
        pairs = list(d.items())
        pairs.sort(key=lambda x: x[1]) 

        # Create tree and encoding table
        tree = self.create_huffman_tree(pairs)
        encoding_table = self.create_encoding_table(tree)

        # Serialize the Huffman tree
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

        # print(f"Encoding complete. compressd file saved as '{input_file}.enc'.")
        total_time = time.time() - start_time
        return total_time


        # except Exception as e:
        #     print(f"An error occurred during encoding: {e}")
        #     return 0


    def decompress(self, folder_path, enc_file):
        start_time = time.time()

        # Read the serialized tree and enc data from the file
        with open(f"{folder_path}{enc_file}.enc", 'rb') as file:
            enc_data = file.read()  # Read the rest of the file (enc data)

        pairs = list()
        # Deserialize the Huffman tree
        while enc_data[0:4] != b'\x00\x00\x00\x00':
            char, freq = struct.unpack('<II', enc_data[:8])
            enc_data = enc_data[8:]
            pairs.append((chr(char), freq))

        enc_data = enc_data[4:]  # Skip the serialized tree end marker

        # Convert byte array to bit string
        bit_string = ''
        for byte in enc_data:
            bit_string += f'{byte:08b}'

        # decompress bit string using Huffman tree
        tree = self.create_huffman_tree(pairs)
        node = tree
        dec_output = ''
        for bit in bit_string:
            if bit == '0':
                node = node.left
            else:
                node = node.right
            
            if node.char is not None:
                dec_output += node.char
                node = tree

        with open(f"{folder_path}{enc_file}.dec", 'w') as file:
            file.write(dec_output)

        # print(f"Decoding complete. dec file saved as '{enc_file}'.")
        total_time = time.time() - start_time
        return total_time



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