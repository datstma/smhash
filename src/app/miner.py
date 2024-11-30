import sha256
import time
import smhash



def hash_sha256_with_nonce(text: str, nonce: int) -> str:
    """Create SHA-256 hash of the text combined with nonce"""
    return sha256.hash_string(f"{text}{nonce}")


def mine_sha_256_hash(text: str, num_zeros: int, max_nonce: int = 10000000) -> None:
    """Mine for a hash with specified number of leading zeros"""
    target = '0' * num_zeros
    start_time = time.perf_counter()

    for nonce in range(max_nonce):
        if nonce % 100000 == 0:  # Progress update every 100,000 attempts
            print(f"Trying nonce: {nonce}")

        current_hash = hash_sha256_with_nonce(text, nonce)
        if current_hash.startswith(target):
            end_time = time.perf_counter()
            print(f"\nSuccess! Found matching hash:")
            print(f"Text: {text}")
            print(f"Nonce: {nonce}")
            print(f"Hash: {current_hash}")
            print(f"Time taken: {end_time - start_time:.4f} seconds")
            print(f"Hashes calculated: {nonce:,}")
            print(f"Hashes per second: {nonce / (end_time - start_time):,.2f}")
            return

    print(f"Could not find a matching hash after {max_nonce:,} attempts")

def hash_smhash_with_nonce(text: str, nonce: int) -> str:
    """Create SHA-256 hash of the text combined with nonce"""
    return smhash.hash_string(f"{text}{nonce}")
def mine_smhash_hash(text: str, num_zeros: int, max_nonce: int = 10000000) -> None:
    """Mine for a hash with specified number of leading zeros"""
    target = '0' * num_zeros
    start_time = time.perf_counter()

    for nonce in range(max_nonce):
        if nonce % 100000 == 0:  # Progress update every 100,000 attempts
            print(f"Trying nonce: {nonce}")

        current_hash = hash_smhash_with_nonce(text, nonce)
        if current_hash.startswith(target):
            end_time = time.perf_counter()
            print(f"\nSuccess! Found matching hash:")
            print(f"Text: {text}")
            print(f"Nonce: {nonce}")
            print(f"Hash: {current_hash}")
            print(f"Time taken: {end_time - start_time:.4f} seconds")
            print(f"Hashes calculated: {nonce:,}")
            print(f"Hashes per second: {nonce / (end_time - start_time):,.2f}")
            return

    print(f"Could not find a matching hash after {max_nonce:,} attempts")


if __name__ == "__main__":
    text = "Hello, world"
    num_zeros = 3  # Change this to try different numbers of zeros
    print('sha256')
    mine_sha_256_hash(text, num_zeros)
    print('smhash')
    mine_smhash_hash(text, num_zeros)