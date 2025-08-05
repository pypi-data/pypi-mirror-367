import json
import random
import os
import cupy as cp
from .primitives import get_all_primitive_names
from .exceptions import KeyStructureError, ConfigurationError

def _expand_key(master_key, num_subkeys, subkey_size_bytes=8):
    subkeys = []
    current_key_material = master_key
    h_func = lambda data: cp.sum(cp.frombuffer(data, dtype=cp.uint64) * cp.uint64(0xDEADBEEFCAFEBABE)).tobytes()

    for _ in range(num_subkeys):
        h = h_func(current_key_material)
        subkey = h[:subkey_size_bytes]
        subkeys.append(subkey)
        current_key_material = subkey + current_key_material
        
    return [int.from_bytes(sk, 'big') for sk in subkeys]

def generate_key_structure(architecture: list[int]) -> dict:
    if len(architecture) < 3:
        raise ConfigurationError("Architecture for Feistel network requires at least 3 elements: [Block_Size, F_Width, Num_Rounds].")

    master_key_bytes = os.urandom(32)
    master_key_hex = master_key_bytes.hex()
    
    all_primitives = get_all_primitive_names()
    num_rounds = architecture[2]
    
    key = {
        "master_key": master_key_hex,
        "architecture": architecture,
        "layers": []
    }
    
    num_subkeys_needed = 0
    f_width = architecture[1]
    for _ in range(num_rounds):
        for _ in range(f_width):
            num_subkeys_needed += 2 
            
    subkeys = _expand_key(master_key_bytes, num_subkeys_needed)
    subkey_idx = 0

    num_primitives_per_neuron = len(all_primitives)
    for _ in range(num_rounds):
        layer_config = {"neurons": []}
        for _ in range(f_width):
            shuffled_primitives = random.sample(all_primitives, num_primitives_per_neuron)
            neuron_subkeys = {
                "xor_const": subkeys[subkey_idx],
                "add_mod": subkeys[subkey_idx + 1]
            }
            subkey_idx += 2
            layer_config["neurons"].append({
                "sequence": shuffled_primitives,
                "subkeys": neuron_subkeys
            })
        key["layers"].append(layer_config)

    return key

def save_key(key: dict, filepath: str):
    try:
        with open(filepath, 'w') as f:
            json.dump(key, f, indent=4)
    except IOError as e:
        raise KeyStructureError(f"Failed to save key to {filepath}: {e}")

def load_key(filepath: str) -> dict:
    try:
        with open(filepath, 'r') as f:
            key = json.load(f)
        if "architecture" not in key or "layers" not in key or "master_key" not in key:
            raise KeyStructureError("Invalid key file: required fields are missing.")
        return key
    except (IOError, json.JSONDecodeError) as e:
        raise KeyStructureError(f"Failed to load or parse key from {filepath}: {e}")