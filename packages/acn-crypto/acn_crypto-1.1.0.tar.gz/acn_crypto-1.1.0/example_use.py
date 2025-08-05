import os
import time
from acn import ACN, save_key, visualize_acn_key

def main():
    print("--- ACN Feistel Network Demo (High-Speed, High-Security GPU) ---")

    architecture = [64, 32, 128]
    
    print(f"\n[Step 1] Creating a new ACN with architecture: {architecture}")
    
    acn_encryptor = ACN(architecture=architecture)
    
    KEY_FILE = "my_acn_feistel_gpu.key"
    save_key(acn_encryptor.key, KEY_FILE)
    print(f"✅ Key saved to '{KEY_FILE}'")

    data_size_mb = 256
    large_data = os.urandom(data_size_mb * 1024 * 1024)
    print(f"\n[Step 2] Generated {data_size_mb} MB of random data for testing.")

    print("\n[Step 3] Encrypting data...")
    start_time = time.time()
    ciphertext = acn_encryptor.encrypt(large_data)
    end_time = time.time()
    encryption_duration = end_time - start_time
    throughput = data_size_mb / encryption_duration
    print(f"✅ Encryption successful in {encryption_duration:.4f} seconds.")
    print(f"   Throughput: {throughput:.2f} MB/s")

    print("\n[Step 4] Decrypting data...")
    acn_decryptor = ACN.from_key_file(KEY_FILE)
    start_time = time.time()
    decrypted_text = acn_decryptor.decrypt(ciphertext)
    end_time = time.time()
    decryption_duration = end_time - start_time
    throughput = data_size_mb / decryption_duration
    print(f"✅ Decryption successful in {decryption_duration:.4f} seconds.")
    print(f"   Throughput: {throughput:.2f} MB/s")
    
    print("\n[Step 5] Verifying the result...")
    if large_data == decrypted_text:
        print("✅ SUCCESS: The decrypted data matches the original data!")
    else:
        print("❌ FAILURE: The decrypted data does NOT match!")

    VIS_FILE = "acn_feistel_gpu_diagram"
    print(f"\n[Step 6] Generating network visualization...")
    visualize_acn_key(acn_encryptor.key, VIS_FILE, view=False)

    if os.path.exists(KEY_FILE):
        os.remove(KEY_FILE)
    print(f"\n🧹 Cleaned up '{KEY_FILE}'.")


if __name__ == "__main__":
    main()