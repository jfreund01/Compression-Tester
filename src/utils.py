import os
def detailed_report(encoding_name, input_file, compression_time, decompression_time):
    input_size = os.path.getsize(f"{input_file}")
    compressed_size = os.path.getsize(f"{input_file}.enc")
    compression_ratio = float(input_size/compressed_size)
    a = f"""
----------------------------------------
{encoding_name} Statistics

Input File Size:    {input_size/1000:.1f} KB
Output File Size:   {compressed_size/1000:.1f} KB
Compression Ratio:  {compression_ratio:.2f}
Compression Time    {compression_time:.3f}s
Decompression Time: {decompression_time:.3f}s
----------------------------------------"""
    print(a)