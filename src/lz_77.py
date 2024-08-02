import os as time
from utils import detailed_report
import math
import struct
from collections import deque

SEARCH_BUFFER_SIZE = 4096 
LOOK_AHEAD_BUFFER_SIZE = 20

def create_input_string(file_path: str) -> str:
    with open(file_path, "r") as file:
        return list(file.read())

# Simple function to find longest prefix (non-Dynamic Programming)
def find_longest_prefix(search_buffer: list, look_ahead_buffer: list) -> tuple:
    longest_prefix = 0
    longest_prefix_location = 0
    for i in range (0, len(search_buffer)):
        current_length = 0
        current_location = i
        j = 0
        while j < len(look_ahead_buffer) and i < len(search_buffer) and search_buffer[i] == look_ahead_buffer[j]:
            current_length += 1
            i += 1
            j += 1
            if current_length >= longest_prefix:
                longest_prefix = current_length
                longest_prefix_location = len(search_buffer) - current_location
            if j == len(look_ahead_buffer):
                return (longest_prefix, longest_prefix_location, '-')
    return (longest_prefix, longest_prefix_location, look_ahead_buffer[longest_prefix])

# KMP algorithm to build prefix table
def build_prefix_table(lookup_buffer: list) -> list:
    prefix_table = [0] * len(lookup_buffer)
    j = 0
    for i in range(1, len(lookup_buffer)):
        if lookup_buffer[i] == lookup_buffer[j]:
            j += 1
            prefix_table[i] = j
        else:
            while j > 0 and lookup_buffer[i] != lookup_buffer[j]:
                j = prefix_table[j - 1]

    prefix_table[-1] = prefix_table[j] + 1
    # print(prefix_table)
    return(prefix_table)

# Pack tuple into bytes
def pack_tuple(tuple: tuple) -> bytes:
    return struct.pack('HBB', tuple[0], tuple[1], tuple[2])

# KMP algorithm to find longest prefix
def find_longest_prefix_KMP(search_buffer: list, look_ahead_buffer: list) -> tuple:
    prefix_table = build_prefix_table(look_ahead_buffer)
    i = 0
    j = 0
    longest_location = 0
    longest_length = 0
    while i < len(search_buffer):
        if search_buffer[i] == look_ahead_buffer[j]:
            i += 1
            j += 1
            if j >= longest_length:
                longest_length = j
                longest_location = i - j
            if j == len(look_ahead_buffer):
                return (len(search_buffer) - longest_location, longest_length, '-')
        else: 
            if j != 0:
                j = prefix_table[j - 1]
            else:
                i += 1
    return (len(search_buffer) - longest_location, longest_length, look_ahead_buffer[j + 1])

# LZ77 encoding algorithm using HashLookup

# LZ77 encoding algorithm
def lz77_encode(input_file: str) -> str:
    input_string = create_input_string(input_file)
    full_len = len(input_string)
    output_string = []
    output_buffer = bytearray()
    search_buffer = deque(maxlen=SEARCH_BUFFER_SIZE)
    look_ahead_buffer = input_string[:LOOK_AHEAD_BUFFER_SIZE]
    input_pos = 0

    while input_pos <= full_len:
        print(((full_len - input_pos) / full_len) * 100)
        if look_ahead_buffer[0] not in search_buffer:
            byte_string = pack_tuple((0, 0, ord(look_ahead_buffer[0])))
            output_string.append((0, 0, look_ahead_buffer[0]))
            output_buffer.extend(byte_string)
            search_buffer.append(look_ahead_buffer[0])
            input_pos += 1
            look_ahead_buffer = input_string[input_pos:input_pos + LOOK_AHEAD_BUFFER_SIZE]
        else:
            prefix_location, prefix_length, next_char = find_longest_prefix_KMP(search_buffer, look_ahead_buffer)
            byte_string = pack_tuple((prefix_location, prefix_length, ord(next_char)))
            output_string.append((prefix_location, prefix_length, next_char))
            output_buffer.extend(byte_string)
            move_len = prefix_length + 1
            search_buffer.extend(look_ahead_buffer[:move_len])
            input_pos += move_len
            look_ahead_buffer = input_string[input_pos:input_pos + LOOK_AHEAD_BUFFER_SIZE]

    with open("../text_encoded_files/lz77_encoded.bin", "wb") as file:
        file.write(output_buffer)
