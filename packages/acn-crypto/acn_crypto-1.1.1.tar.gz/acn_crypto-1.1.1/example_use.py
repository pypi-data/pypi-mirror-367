from acn import ACN

# 1. Create a new cipher with a specific architecture
#    Architecture: [Block_Size, F_Function_Width, Num_Rounds]
try:
    cipher = ACN(architecture=[32, 16, 24])
except Exception as e:
    print(f"Configuration Error: {e}")
    exit()

# 2. Save the generated key (the network's architecture)
#    PROTECT THIS FILE. It's your secret key.
cipher.save_key("my_secret.key")

# 3. Encrypt data (strings or bytes)
message = "This is a secret message."
encrypted_data = cipher.encrypt(message)
print(f"Encrypted (hex): {encrypted_data.hex()}")

# 4. Decrypt data using a new ACN instance loaded from the key file
decryption_cipher = ACN.from_key_file("my_secret.key")
decrypted_message = decryption_cipher.decrypt(encrypted_data)
print(f"Decrypted: {decrypted_message}")