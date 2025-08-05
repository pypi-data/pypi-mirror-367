import os
import cupy as cp
from .engine import CryptographicLayer
from .key_manager import generate_key_structure, load_key
from .utils import data_to_gpu_array, gpu_array_to_data
from .exceptions import ConfigurationError

class ACN:
    def __init__(self, architecture: list[int] = None, key: dict = None):
        if architecture:
            if not isinstance(architecture, list) or len(architecture) != 3:
                raise ConfigurationError(
                    f"Architecture configuration is invalid.\n"
                    f"It must be a list with exactly 3 integer elements: [Block_Size, F_Width, Num_Rounds].\n"
                    f"You provided: {architecture}"
                )
            
            block_size, f_width, num_rounds = architecture
            
            if not isinstance(block_size, int) or block_size <= 0 or block_size % 2 != 0:
                corrected_size = block_size + 1 if isinstance(block_size, int) and block_size > 0 else 16
                raise ConfigurationError(
                    f"Invalid Block_Size: '{block_size}'. It must be a positive, even integer.\n"
                    f"Suggestion: Use a power of 2 like 16, 32, or 64. For example, you could use {corrected_size}."
                )

            half_block_size = block_size // 2

            if not isinstance(f_width, int) or f_width != half_block_size:
                 raise ConfigurationError(
                    f"Configuration mismatch: F_Width ({f_width}) must be exactly half of Block_Size ({half_block_size}).\n"
                    f"For a Block_Size of {block_size}, please set F_Width to {half_block_size}.\n"
                    f"Correct architecture: [{block_size}, {half_block_size}, {num_rounds}]"
                )
            
            if not isinstance(num_rounds, int) or num_rounds <= 0:
                 raise ConfigurationError(f"Invalid Num_Rounds: '{num_rounds}'. It must be a positive integer.")
            elif num_rounds < 16:
                print(f"⚠️ Security Warning: The number of rounds ({num_rounds}) is low. For strong security, 16 or more rounds are recommended.")
            elif num_rounds > 64:
                print(f"ℹ️ Performance Note: The number of rounds ({num_rounds}) is very high. This will provide strong security but may impact performance.")

            self.key = generate_key_structure(architecture)
            
        elif key:
            self.key = key
        else:
            raise ConfigurationError("Must provide either an architecture or a key.")
        
        self.architecture = self.key['architecture']
        self.block_size_in_chunks = self.architecture[0]
        self.f_width = self.architecture[1]
        self.num_rounds = self.architecture[2]
        self.half_block_size = self.block_size_in_chunks // 2
        
        self.layers = self._build_network_from_key()
        
        if len(self.layers) != self.num_rounds:
             raise ConfigurationError("Mismatch between rounds in architecture and layers in the provided key.")

        print(f"✅ ACN Feistel Engine Initialized for GPU.\n"
              f"   - Block Size: {self.block_size_in_chunks} chunks ({self.block_size_in_chunks*8} bytes)\n"
              f"   - F-Function Width: {self.f_width} chunks\n"
              f"   - Rounds: {self.num_rounds}")

    def _build_network_from_key(self):
        layers = []
        layer_configs = self.key.get("layers", [])
        for layer_config in layer_configs:
            neuron_configs = layer_config.get("neurons", [])
            layers.append(CryptographicLayer(neuron_configs))
        return layers
    
    def _F(self, data_half, round_index):
        current_chunks = data_half
        layer = self.layers[round_index]
        substituted_chunks = cp.empty_like(current_chunks)
        for i in range(self.f_width):
            neuron_output = current_chunks[:, i].copy()
            for func in layer.neurons[i].functions:
                neuron_output = func(neuron_output)
            substituted_chunks[:, i] = neuron_output
        mixed_chunks = substituted_chunks.copy()
        for i in range(1, self.f_width):
            mixed_chunks[:, i] ^= mixed_chunks[:, i-1]
        return mixed_chunks

    def _process_feistel_network(self, blocks):
        L = blocks[:, :self.half_block_size].copy()
        R = blocks[:, self.half_block_size:].copy()
        for i in range(self.num_rounds):
            F_result = self._F(R, i)
            L, R = R, L ^ F_result
        return cp.hstack((R, L))
    
    def _generate_keystream(self, nonce, num_blocks):
        counter_base = cp.frombuffer(nonce, dtype=cp.uint64)
        counter_increments = cp.arange(num_blocks, dtype=cp.uint64).reshape(-1, 1)
        counter_blocks_flat = counter_base + counter_increments
        counter_blocks = cp.broadcast_to(counter_blocks_flat, (num_blocks, self.block_size_in_chunks))
        keystream = self._process_feistel_network(counter_blocks)
        return keystream

    def encrypt(self, data):
        if isinstance(data, str):
            data_bytes = data.encode('utf-8')
        elif isinstance(data, bytes):
            data_bytes = data
        else:
            raise TypeError("Input for encryption must be a string or bytes.")

        nonce = os.urandom(8)
        pt_array = data_to_gpu_array(data_bytes, self.block_size_in_chunks)
        num_blocks = pt_array.shape[0]
        keystream = self._generate_keystream(nonce, num_blocks)
        ct_array = pt_array ^ keystream
        ciphertext_bytes = gpu_array_to_data(ct_array)
        return nonce + ciphertext_bytes

    def decrypt(self, ciphertext: bytes, output_format='str'):
        if not isinstance(ciphertext, bytes):
            raise TypeError("Input for decryption must be bytes.")

        nonce = ciphertext[:8]
        ciphertext_data = ciphertext[8:]
        ct_array = data_to_gpu_array(ciphertext_data, self.block_size_in_chunks)
        num_blocks = ct_array.shape[0]
        keystream = self._generate_keystream(nonce, num_blocks)
        pt_array = ct_array ^ keystream
        plaintext_bytes = gpu_array_to_data(pt_array).rstrip(b'\x00')

        if output_format == 'str':
            try:
                return plaintext_bytes.decode('utf-8')
            except UnicodeDecodeError:
                print("⚠️ Warning: Decrypted data could not be decoded to a UTF-8 string. Returning bytes instead.")
                return plaintext_bytes
        elif output_format == 'bytes':
            return plaintext_bytes
        else:
            raise ValueError("Invalid output_format. Choose 'str' or 'bytes'.")

    @classmethod
    def from_key_file(cls, filepath: str):
        key = load_key(filepath)
        return cls(key=key)