import os as os
from utils import detailed_report
import struct
from collections import deque
from functools import wraps
from time import time
import concurrent.futures

# Data will be compressed to this format:
#     4 bytes of "\x00\x00\x00\x00 to seperate blocks for each parallel
#     1 byte for number of blocks to split into for parallel processing
#     encoded data:
#         2 bytes for distance
#         1 byte for length
#         1 byte for next character (null byte for no character)
    

def timing(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = time()
        f(*args, **kw)
        te = time()
        execution_time = te - ts
        print(f'Function {f.__name__} executed in: {execution_time:.8f}s')
        return execution_time
    return wrap

# Pack tuple into bytes
def pack_tuple(tuple: tuple) -> bytes:
    return struct.pack('HBB', tuple[0], tuple[1], tuple[2])


class LZ77Compressor:
    SPECIAL_BYTE = 0
    PARALLEL_SEPERATOR_BYTES = b'\x00\x00\x00\x00'
    PARALLEL_SEPERATOR_AMOUNT = 4

    def __init__(self, search_buffer_size, lookup_buffer_size, block_number=1):
        self.search_buffer_size = search_buffer_size
        self.lookup_buffer_size = lookup_buffer_size
        self.block_number = block_number
    
    def hash_substring(self, substring: str) -> int:
        return hash(substring)
    
    
    def compress_block(self, index: int, data: str) -> bytearray:
        # output_string = []
        # temp_dict = {}
        byte_data = bytearray()
        for i in range(0, self.PARALLEL_SEPERATOR_AMOUNT):
            byte_data.extend(self.PARALLEL_SEPERATOR_BYTES)
        i = 0
        l = len(data)
        dictionary = {}
        while i < l:
            # print(i / l * 100)
            longest_location = 0
            longest_length = 0
            current_char = data[i]
            current_char_hash = self.hash_substring(data[i])
            # If the hash is found in the dictionary, we need to deal with out of bounds before
            if dictionary.get(current_char_hash):
                for pos in dictionary[current_char_hash]:
                    # make sure to remove locations that are out of bounds
                    if pos < i - self.search_buffer_size:
                        dictionary[current_char_hash].remove(pos)
                        # temp_dict[current_char].remove(pos)
                        if dictionary[current_char_hash] == []:
                            del dictionary[current_char_hash]
                            # del temp_dict[current_char]
                    # if the location is within bounds, we need to find the longest prefix
                    else:
                        current_length = 0
                        j = pos
                        temp_i = i
                        while temp_i < l and current_length < self.lookup_buffer_size and data[temp_i] == data[j]:
                            temp_i += 1
                            j += 1
                            current_length += 1
                            if current_length >= longest_length:
                                longest_length = current_length
                                longest_location = temp_i - j
                i += longest_length
                if i == l:
                    byte_data.extend(pack_tuple((longest_location, longest_length, 0)))
                    # output_string.append((longest_location, longest_length, ''))
                else:
                    byte_data.extend(pack_tuple((longest_location, longest_length, ord(data[i]))))
                    # output_string.append((longest_location, longest_length, data[i]))
                    i += 1
                # Add the characters in the substring to the dictionary
                for k in range((i - longest_length - 1), i):
                    current_char = data[k]
                    current_char_hash = self.hash_substring(current_char)
                    if dictionary.get(current_char_hash):
                        dictionary[current_char_hash].append(k)
                        # temp_dict[current_char].append(k)
                    else:
                        dictionary[current_char_hash] = [k]
                        # temp_dict[current_char] = [k]
            # If we dont find the hash in the dictionary, we need to add it and return the 0,0,char tuple
            else:
                byte_data.extend(pack_tuple((0, 0, ord(current_char[0]))))
                # output_string.append((0, 0, current_char[0]))
                dictionary[current_char_hash] = [i]
                # temp_dict[current_char] = [i]
                i += 1
            # print(# output_string)
        return (index, byte_data)
    
    @timing
    def compress(self, folder_path, input_file):
        data_list = []
        with open(f"{folder_path}{input_file}", "r") as file:
            data = file.read()
            for i in range(0, self.block_number):
                data_list.append(data[i * len(data) // self.block_number:(i + 1) * len(data) // self.block_number])
                # print (data_list[i])
                
        compressed_data = bytearray()
        indexed_blocks = [(i, block) for i, block in enumerate(data_list)]
        with concurrent.futures.ProcessPoolExecutor() as executor:
            results = list(executor.map(self.compress_block, \
                [i for i, block in indexed_blocks], \
                [block for i, block in indexed_blocks]))
        
        results.sort(key=lambda x: x[0])
        for result in results:
            compressed_data.extend(result[1])
            
        compressed_data = struct.pack('>I', self.block_number) + compressed_data
        with open(f"{folder_path}{input_file}.enc", "wb") as file:
            file.write(compressed_data)
                
# class KMP_LZ77Compressor:

#     def __init__(self, search_buffer_size, lookup_buffer_size):
#         self.search_buffer_size = search_buffer_size
#         self.lookup_buffer_size = lookup_buffer_size

#     def create_input_string(self, file_path: str) -> str:
#         with open(file_path, "r") as file:
#             return list(file.read())


#     # KMP algorithm to build prefix table
#     def build_prefix_table(lookup_buffer: list) -> list:
#         prefix_table = [0] * len(lookup_buffer)
#         j = 0
#         for i in range(1, len(lookup_buffer)):
#             if lookup_buffer[i] == lookup_buffer[j]:
#                 j += 1
#                 prefix_table[i] = j
#             else:
#                 while j > 0 and lookup_buffer[i] != lookup_buffer[j]:
#                     j = prefix_table[j - 1]

#         prefix_table[-1] = prefix_table[j] + 1
#         # print(prefix_table)
#         return(prefix_table)

#     # KMP algorithm to find longest prefix
#     def find_longest_prefix_KMP(search_buffer: list, look_ahead_buffer: list) -> tuple:
#         prefix_table = self.build_prefix_table(look_ahead_buffer)
#         i = 0
#         j = 0
#         longest_location = 0
#         longest_length = 0
#         while i < len(search_buffer):
#             if search_buffer[i] == look_ahead_buffer[j]:
#                 i += 1
#                 j += 1
#                 if j >= longest_length:
#                     longest_length = j
#                     longest_location = i - j
#                 if j == len(look_ahead_buffer):
#                     return (len(search_buffer) - longest_location, longest_length, '-')
#             else: 
#                 if j != 0:
#                     j = prefix_table[j - 1]
#                 else:
#                     i += 1
#         return (len(search_buffer) - longest_location, longest_length, look_ahead_buffer[j + 1])


#     def compress(self, input_file: str) -> str:
#         input_string = self.create_input_string(input_file)
#         full_len = len(input_string)
#         # output_string = []
#         output_buffer = bytearray()
#         search_buffer = deque(maxlen=SEARCH_BUFFER_SIZE)
#         look_ahead_buffer = input_string[:LOOK_AHEAD_BUFFER_SIZE]
#         input_pos = 0

#         while input_pos <= full_len:
#             print(((full_len - input_pos) / full_len) * 100)
#             if look_ahead_buffer[0] not in search_buffer:
#                 byte_string = pack_tuple((0, 0, ord(look_ahead_buffer[0])))
#                 # # output_string.append((0, 0, look_ahead_buffer[0]))
#                 output_buffer.extend(byte_string)
#                 search_buffer.append(look_ahead_buffer[0])
#                 input_pos += 1
#                 look_ahead_buffer = input_string[input_pos:input_pos + LOOK_AHEAD_BUFFER_SIZE]
#             else:
#                 prefix_location, prefix_length, next_char = self.find_longest_prefix_KMP(search_buffer, look_ahead_buffer)
#                 byte_string = pack_tuple((prefix_location, prefix_length, ord(next_char)))
#                 # # output_string.append((prefix_location, prefix_length, next_char))
#                 output_buffer.extend(byte_string)
#                 move_len = prefix_length + 1
#                 search_buffer.extend(look_ahead_buffer[:move_len])
#                 input_pos += move_len
#                 look_ahead_buffer = input_string[input_pos:input_pos + LOOK_AHEAD_BUFFER_SIZE]

#         with open("../text_encoded_files/lz77_encoded.bin", "wb") as file:
#             file.write(output_buffer)
#             e):


#         decompressed_data = []

#         with open(f"{folder_path}{input_file}.enc", 'rb') as f:
#             while True:
#                 chunk = f.read(struct.calcsize('HBB'))
#                 if not chunk:
#                     break
#                 distance, length, next_char = struct.unpack('HBB', chunk)
#                 # print (distance, length, chr(next_char))
#                 if next_char == self.SPECIAL_BYTE:
#                     # Special case: entire remaining string is a match
#                     match_start = len(decompressed_data) - distance
#                     match_string = decompressed_data[match_start:match_start + length]
#                     decompressed_data.extend(match_string)
#                 elif distance > 0 and length > 0:
#                     # Match found
#                     match_start = len(decompressed_data) - distance
#                     for i in range(length):
#                         decompressed_data.append(decompressed_data[match_start + i])
#                     if next_char != 0:
#                         decompressed_data.append(chr(next_char))
#                 else:
#                     # Literal character
#                     decompressed_data.append(chr(next_char))
#         decompressed_string = ''.join(decompressed_data)

#         with open(f"{folder_path}{input_file}.dec", "w") as file:
#             file.write(str(decompressed_string))

#     def test(self, folder_path, input_file):
#         comp_time = self.compress(folder_path, input_file)
#         decomp_time = self.decompress(folder_path, input_file)
#         detailed_report("LZ77", f"{folder_path}{input_file}", comp_time, decomp_time)