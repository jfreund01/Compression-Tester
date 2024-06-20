import heapq as hq
import pickle
import os
import time
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

def create_huffman_tree(huffman_table):
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

def create_encoding_table(node, bit='', encoding_table={}):
    if (node.char is not None): # base case
        encoding_table[node.char] = bit
    if (node.left is not None):
        create_encoding_table(node.left, bit = f'{bit}0', encoding_table=encoding_table)
    if (node.right is not None):
        create_encoding_table(node.right, bit = f'{bit}1', encoding_table=encoding_table)
    return encoding_table

def resolve_same_frequency(incomplete_table):
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

def serialize_huffman_tree(node):
    if node is None:
        return ''
    if node.char is not None:
        return f'1{node.char}'
    return f'0{serialize_huffman_tree(node.left)}{serialize_huffman_tree(node.right)}'

def deserialize_huffman_tree(data, index=0):
    if index >= len(data):
        return None, index
    if data[index] == '1':
        return huffman_node(char=data[index + 1], freq=0), index + 2
    left, next_index = deserialize_huffman_tree(data, index + 1)
    right, next_index = deserialize_huffman_tree(data, next_index)
    return huffman_node(char=None, freq=0, left=left, right=right), next_index


def encode(input_file):
    output_file = f"{os.path.splitext(input_file)[0]}.bin"
    start_time = time.time()
    try:
        # Count character frequencies
        d = dict()
        with open(input_file, 'r') as file:
            for line in file:
                for character in line:
                    if character not in d:
                        d[character] = 1
                    else:
                        d[character] += 1

        pairs = list(d.items())
        pairs.sort(key=lambda x: x[1])  # Sort by frequency
        tree = create_huffman_tree(pairs)
        encoding_table = create_encoding_table(tree)

        # Serialize the Huffman tree
        serialized_tree = pickle.dumps(tree)

        # Generate bit string
        bit_string = ''
        with open(input_file, 'r') as file:
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

        # Write the serialized tree and encoded data to file
        with open(output_file, 'wb') as file:
            file.write(len(serialized_tree).to_bytes(4, 'big'))  # Write the length of the serialized tree
            file.write(serialized_tree)  # Write the serialized tree
            file.write(byte_array)  # Write the encoded data

        print(f"Encoding complete. Encoded file saved as '{output_file}'.")
        total_time = time.time() - start_time
        return total_time


    except Exception as e:
        print(f"An error occurred during encoding: {e}")
        return 0


def decode(encoded_file):
    output_file = f"{os.path.splitext(encoded_file)[0]}.decoded"
    start_time = time.time()
    try:
        # Read the serialized tree and encoded data from the file
        with open(encoded_file, 'rb') as file:
            tree_size = int.from_bytes(file.read(4), 'big')  # Read the length of the serialized tree
            serialized_tree = file.read(tree_size)  # Read the serialized tree
            byte_array = file.read()  # Read the rest of the file (encoded data)

        # Deserialize the Huffman tree
        tree = pickle.loads(serialized_tree)

        # Convert byte array to bit string
        bit_string = ''
        for byte in byte_array:
            bit_string += f'{byte:08b}'

        # Decode bit string using Huffman tree
        node = tree
        decoded_output = ''
        for bit in bit_string:
            if bit == '0':
                node = node.left
            else:
                node = node.right
            
            if node.char is not None:
                decoded_output += node.char
                node = tree

        with open(output_file, 'w') as file:
            file.write(decoded_output)

        print(f"Decoding complete. Decoded file saved as '{output_file}'.")
        total_time = time.time() - start_time
        return total_time

    except Exception as e:
        print(f"An error occurred during decoding: {e}")
        return 0


def huffman_encode(input_file):
    input_file_base = os.path.splitext(input_file)[0]
    compression_time = encode(f"{input_file_base}.txt")
    decompression_time = decode(f"{input_file_base}.bin")
    detailed_report("Huffman Encode", input_file_base, input_file_base, compression_time, decompression_time)

