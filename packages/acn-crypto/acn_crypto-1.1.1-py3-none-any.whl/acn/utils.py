import cupy as cp
from .exceptions import DataError
from .primitives import DTYPE

def data_to_gpu_array(data: bytes, block_size_in_chunks: int, chunk_dtype=DTYPE):
    if not isinstance(data, bytes):
        raise DataError("Input data must be of type bytes.")
    
    bytes_per_chunk = cp.dtype(chunk_dtype).itemsize
    bytes_per_block = block_size_in_chunks * bytes_per_chunk
    
    if len(data) % bytes_per_block != 0:
        padding_size = bytes_per_block - (len(data) % bytes_per_block)
        data += b'\x00' * padding_size

    arr = cp.frombuffer(data, dtype=chunk_dtype)
    return arr.reshape(-1, block_size_in_chunks)

def gpu_array_to_data(gpu_array):
    return cp.asnumpy(gpu_array).tobytes()