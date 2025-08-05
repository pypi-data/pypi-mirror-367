from .primitives import get_primitive_function

class CryptographicNeuron:
    def __init__(self, neuron_config: dict):
        self.functions = []
        sequence = neuron_config.get("sequence", [])
        subkeys = neuron_config.get("subkeys", {})
        
        for name in sequence:
            func = get_primitive_function(name)
            if name in ["xor_const", "add_mod"]:
                subkey = subkeys.get(name, 0)
                self.functions.append(lambda n, f=func, sk=subkey: f(n, sk))
            else:
                self.functions.append(func)

class CryptographicLayer:
    def __init__(self, layer_config: list):
        self.neurons = [CryptographicNeuron(cfg) for cfg in layer_config]