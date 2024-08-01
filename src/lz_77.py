import os as time
from utils import detailed_report

SEARCH_BUFFER_SIZE = 8
LOOK_AHEAD_BUFFER_SIZE = 4

def create_input_string(file_path: str) -> str:
    with open(file_path, "r") as file:
        return list(file.read())

def find_longest_prefix(search_buffer: list, look_ahead_buffer: list) -> tuple:
    j = 0
    longest_prefix = 0
    longest_prefix_location = 0
    for i in range (0, len(search_buffer)):
        current_length = 0
        while j < len(look_ahead_buffer) and i < len(search_buffer) and search_buffer[i] == look_ahead_buffer[j]:
            current_length += 1
            i += 1
            j += 1
            if current_length > longest_prefix:
                longest_prefix = current_length
                longest_prefix_location = i - (current_length - 1)
    return (longest_prefix, longest_prefix_location, look_ahead_buffer[j])

# def find_longest_prefix(search_buffer: list, look_ahead_buffer: list) -> tuple:
#     current_char = look_ahead_buffer[0]
#     look_ahead_buffer.pop(0)
#     prefix_length = 0
#     prefix_location = 0
#     for i in range(0, len(search_buffer)):
#         if search_buffer[i] == current_char:
#             prefix_location = i
#             for j in range(0, len(look_ahead_buffer)):
#                 if look_ahead_buffer[j] == search_buffer[i + j]:
#                     prefix_length += 1
#                 else:
#                     break
#             if prefix_length > 1:
#                 return (prefix_length, prefix_location)

def lz77_encode(input_file: str) -> str:
    input_string = create_input_string(input_file)
    output_string = list()
    search_buffer = []
    look_ahead_buffer = [None] * LOOK_AHEAD_BUFFER_SIZE
    look_ahead_buffer[:] = input_string[:LOOK_AHEAD_BUFFER_SIZE]
    while input_string:
        if input_string[0] not in search_buffer:
            output_string.append((0, 0, input_string[0]))
            search_buffer.insert(0,input_string[0])
            while len(search_buffer) > SEARCH_BUFFER_SIZE:
                search_buffer.pop(-1)
            look_ahead_buffer[:] = input_string[1:LOOK_AHEAD_BUFFER_SIZE + 1]
            input_string = input_string[1:]
        else:
            prefix_length, prefix_location, next_char = find_longest_prefix(search_buffer, look_ahead_buffer)
            output_string.append((prefix_length, prefix_location, next_char))
            input_string[:] = input_string[prefix_length:]
            look_ahead_buffer[:] = input_string[:LOOK_AHEAD_BUFFER_SIZE]
            for x in range(0, prefix_length + 1):
                search_buffer.append(input_string[x])
            while len(search_buffer) > SEARCH_BUFFER_SIZE:
                search_buffer.pop(-1)
    print(str(output_string))
    return(str(output_string))