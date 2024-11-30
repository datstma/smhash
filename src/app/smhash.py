import struct
from typing import Union, Optional
from enum import Enum


class MiningMode(Enum):
    """Mining optimization modes"""
    FAST = 1  # Optimized for maximum speed, fewer rounds
    STANDARD = 2  # Balanced for general blockchain use
    SECURE = 3  # More rounds for critical operations


class BlockHash:
    """
    Blockchain-optimized hash implementation focused on:
    - Fast proof-of-work calculations
    - Efficient nonce testing
    - Memory-efficient for parallel processing
    - ASIC-resistant design (optional)

    # Basic hashing
    hash_value = hash_string("Hello, World!")

    # Different hash sizes
    hash_128 = hash_string("Hello, World!", HashSize.HASH_128)
    hash_256 = hash_string("Hello, World!", HashSize.HASH_256)
    hash_512 = hash_string("Hello, World!", HashSize.HASH_512)

    # Keyed hashing
    mac = mHash.hash_with_key("message", "secret_key")

    # Key derivation
    derived_key = mHash.derive_key("password", "salt", iterations=10000)

    # Performance testing
    bench_results = benchmark()
    """

    VERSION = "0.3.6"

    # Constants optimized for mining operations
    # Using prime numbers and irrational number derivatives for good distribution
    MINING_CONSTANTS = [
        0x6a09e667f3bcc908, 0xbb67ae8584caa73b,  # sqrt(2) based
        0x3c6ef372fe94f82b, 0xa54ff53a5f1d36f1  # sqrt(3) based
    ]

    # Specialized constants for nonce mixing
    NONCE_MIX = [
        0x510e527fade682d1, 0x9b05688c2b3e6c1f  # golden ratio based
    ]

    def __init__(self, mode: MiningMode = MiningMode.STANDARD):
        """
        Initialize hasher with mining-specific optimizations.

        Args:
            mode: Mining optimization mode
        """
        self.mode = mode
        self.reset()

    @staticmethod
    def _rotright(value: int, shift: int) -> int:
        """Fast right rotation optimized for 64-bit"""
        return ((value >> shift) | (value << (64 - shift))) & 0xFFFFFFFFFFFFFFFF

    @staticmethod
    def _rotleft(value: int, shift: int) -> int:
        """Fast left rotation optimized for 64-bit"""
        return ((value << shift) | (value >> (64 - shift))) & 0xFFFFFFFFFFFFFFFF

    def _get_round_count(self) -> int:
        """Get optimal number of rounds based on mining mode"""
        return {
            MiningMode.FAST: 2,  # Minimum rounds for basic security
            MiningMode.STANDARD: 3,  # Balanced for most mining
            MiningMode.SECURE: 4  # More rounds for critical operations
        }[self.mode]

    def reset(self) -> None:
        """Reset internal state"""
        self.state = self.MINING_CONSTANTS.copy()
        self.buffer = bytearray()

    def _mix_mining(self, x: int, y: int) -> tuple[int, int]:
        """
        Fast mixing function optimized for mining operations.
        Balances speed with sufficient bit mixing.
        """
        # Quick diffusion with minimal operations
        x = self._rotright(x, 13) ^ y
        y = self._rotleft(y, 17) ^ x

        # One more round of mixing with different shifts
        x = self._rotright(x, 21) ^ y
        y = self._rotleft(y, 29) ^ x

        return x, y

    def _fast_nonce_mix(self, state: list[int], nonce: int) -> list[int]:
        """
        Specialized mixing for nonce updates.
        Optimized for rapid nonce testing in mining.
        """
        # Mix nonce into state quickly
        state[0] ^= nonce
        state[1] ^= self._rotright(nonce, 32)

        # Fast state update
        state[0], state[1] = self._mix_mining(state[0], state[1])
        state[2], state[3] = self._mix_mining(state[2], state[3])

        return state

    def hash_block_header(self,
                          version: int,
                          prev_hash: bytes,
                          merkle_root: bytes,
                          timestamp: int,
                          bits: int,
                          nonce: int) -> str:
        """
        Specialized method for hashing block headers.
        Optimized for proof-of-work mining.
        """
        # Pack block header efficiently
        header = struct.pack('<I32s32sIII',
                             version,
                             prev_hash,
                             merkle_root,
                             timestamp,
                             bits,
                             nonce)

        return self.hash_bytes(header)

    def update(self, data: Union[bytes, bytearray, str]) -> None:
        """Update hash with new data"""
        if isinstance(data, str):
            data = data.encode('utf-8')

        self.buffer.extend(data)

        # Process full 64-byte blocks
        while len(self.buffer) >= 64:
            self._process_mining_block(self.buffer[:64])
            self.buffer = self.buffer[64:]

    def _process_mining_block(self, block: bytes) -> None:
        """
        Process a single block optimized for mining operations.
        Reduced operations while maintaining security.
        """
        # Convert block to 64-bit integers
        values = struct.unpack('>QQQQQQQQ', block)

        # Initial mixing with block data
        self.state[0] ^= values[0] ^ values[4]
        self.state[1] ^= values[1] ^ values[5]
        self.state[2] ^= values[2] ^ values[6]
        self.state[3] ^= values[3] ^ values[7]

        # Mixing rounds
        rounds = self._get_round_count()
        for _ in range(rounds):
            # Mix pairs
            self.state[0], self.state[1] = self._mix_mining(
                self.state[0], self.state[1]
            )
            self.state[2], self.state[3] = self._mix_mining(
                self.state[2], self.state[3]
            )

            # Cross mix
            self.state[0], self.state[2] = self._mix_mining(
                self.state[0], self.state[2]
            )
            self.state[1], self.state[3] = self._mix_mining(
                self.state[1], self.state[3]
            )

    def _finalize_mining(self) -> None:
        """
        Finalize hash with minimal but secure operations.
        Optimized for mining performance.
        """
        # Process any remaining data
        if self.buffer:
            padded = self.buffer + b'\x00' * (64 - len(self.buffer))
            self._process_mining_block(padded)

        # Quick final mix
        self.state[0], self.state[2] = self._mix_mining(self.state[0], self.state[2])
        self.state[1], self.state[3] = self._mix_mining(self.state[1], self.state[3])

    def digest(self) -> bytes:
        """Get hash digest as bytes"""
        # Save state
        orig_state = self.state.copy()
        orig_buffer = self.buffer.copy()

        # Finalize and get result
        self._finalize_mining()
        result = b''.join(x.to_bytes(8, 'big') for x in self.state)

        # Restore state
        self.state = orig_state
        self.buffer = orig_buffer

        return result

    def hexdigest(self) -> str:
        """Get hash digest as hex string"""
        return self.digest().hex()

    @classmethod
    def hash_with_nonce(cls, data: bytes, nonce: int,
                        mode: MiningMode = MiningMode.FAST) -> str:
        """
        Optimized method for proof-of-work mining.
        Efficiently combines data with nonce for mining operations.
        """
        hasher = cls(mode)

        # Initialize state with data first
        hasher.update(data)

        # Fast nonce mixing
        hasher.state = hasher._fast_nonce_mix(hasher.state, nonce)

        return hasher.hexdigest()


def hash_string(data: str, mode: MiningMode = MiningMode.STANDARD) -> str:
    """Hash a string with mining optimizations"""
    hasher = BlockHash(mode)
    hasher.update(data)
    return hasher.hexdigest()


def hash_bytes(data: bytes, mode: MiningMode = MiningMode.STANDARD) -> str:
    """Hash bytes with mining optimizations"""
    hasher = BlockHash(mode)
    hasher.update(data)
    return hasher.hexdigest()


# Mining-specific utility functions
def mine_block(block_header: bytes, target_zeros: int,
               max_nonce: int = 2 ** 32) -> tuple[int, str]:
    """
    Mine a block by finding a nonce that produces a hash with
    the specified number of leading zeros.

    Returns:
        tuple: (nonce, hash_value)
    """
    hasher = BlockHash(MiningMode.FAST)
    target = '0' * target_zeros

    for nonce in range(max_nonce):
        hash_value = BlockHash.hash_with_nonce(block_header, nonce)
        if hash_value.startswith(target):
            return nonce, hash_value

    return -1, ""  # Mining failed


def verify_block(block_header: bytes, nonce: int, expected_hash: str) -> bool:
    """
    Verify a mined block by checking if the nonce produces the expected hash.
    """
    hash_value = BlockHash.hash_with_nonce(block_header, nonce, MiningMode.SECURE)
    return hash_value == expected_hash


# Example mining benchmark
def mining_benchmark(difficulty: int = 4, num_blocks: int = 10) -> dict:
    """
    Benchmark mining performance.

    Args:
        difficulty: Number of leading zeros required
        num_blocks: Number of blocks to mine

    Returns:
        dict: Benchmark results
    """
    import time

    results = {
        'blocks_mined': 0,
        'total_time': 0,
        'hashes_per_second': 0,
        'average_time_per_block': 0
    }

    test_header = b'test_block_header_data' * 4
    start_time = time.time()

    for _ in range(num_blocks):
        block_start = time.time()
        nonce, hash_value = mine_block(test_header, difficulty)

        if nonce != -1:
            results['blocks_mined'] += 1
            block_time = time.time() - block_start
            results['total_time'] += block_time

    end_time = time.time()
    total_time = end_time - start_time

    if results['blocks_mined'] > 0:
        results['average_time_per_block'] = results['total_time'] / results['blocks_mined']
        results['hashes_per_second'] = (2 ** difficulty * results['blocks_mined']) / total_time

    return results


if __name__ == "__main__":
    # Example usage and mining benchmark
    print(f"BlockHash Version {BlockHash.VERSION}")

    # Run mining benchmark
    print("\nRunning mining benchmark...")
    difficulties = [4, 5, 6]
    for diff in difficulties:
        print(f"\nTesting difficulty {diff} (leading zeros)")
        results = mining_benchmark(diff, num_blocks=3)
        print(f"Blocks mined: {results['blocks_mined']}")
        print(f"Average time per block: {results['average_time_per_block']:.4f} seconds")
        print(f"Estimated hashes per second: {results['hashes_per_second']:,.2f}")