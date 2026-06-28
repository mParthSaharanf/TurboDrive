import os
import config

def plan_chunks(file_path):
    """
    Analyzes file size and calculates the byte boundaries for every chunk.
    Returns a list of tuples: (chunk_index, start_byte, end_byte)
    """
    file_size = os.path.getsize(file_path)
    chunks = []
    chunk_index = 0
    start_byte = 0

    while start_byte < file_size:
        # End byte is either the end of the 8MB chunk or the actual end of the file
        end_byte = min(start_byte + config.CHUNK_SIZE - 1, file_size - 1)
        chunks.append((chunk_index, start_byte, end_byte))
        
        chunk_index += 1
        start_byte = end_byte + 1

    return chunks

def get_chunk_bytes(file_path, start_byte, end_byte):
    """
    Streams a specific slice of a file from disk into memory.
    Ensures memory footprint remains minimal regardless of overall file size.
    """
    # Calculate exactly how many bytes we need to read
    bytes_to_read = (end_byte - start_byte) + 1
    
    # 'rb' means Read Binary - essential for tracking exact raw file bytes
    with open(file_path, 'rb') as f:
        # Jump directly to the starting position of this specific chunk
        f.seek(start_byte)
        # Read only the planned segment
        return f.read(bytes_to_read)