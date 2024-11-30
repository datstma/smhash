import time
import random
import string
from collections import defaultdict
import matplotlib.pyplot as plt
import smhash
from sha256 import SHA256


class HashAnalyzer:
    def __init__(self):
        self.sha256 = SHA256()


    def generate_random_string(self, length=10):
        """Generate a random string of given length."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def bit_difference(self, hash1: str, hash2: str) -> int:
        """Calculate the number of different bits between two hash strings."""
        # Convert hex strings to binary
        bin1 = ''.join(bin(int(c, 16))[2:].zfill(4) for c in hash1)
        bin2 = ''.join(bin(int(c, 16))[2:].zfill(4) for c in hash2)
        return sum(b1 != b2 for b1, b2 in zip(bin1, bin2))

    def speed_test(self, num_iterations=1000):
        """Compare speed of both hash functions."""
        test_data = [self.generate_random_string() for _ in range(num_iterations)]

        # Test SHA-256
        start_time = time.perf_counter()
        for data in test_data:
            self.sha256.hash(data.encode('utf-8'))
        sha256_time = time.perf_counter() - start_time

        # Test smhash
        start_time = time.perf_counter()
        for data in test_data:
            smhash.hash_string(data)
        smhash_time = time.perf_counter() - start_time

        return {
            'sha256_time': sha256_time,
            'smhash_time': smhash_time,
            'iterations': num_iterations,
            'sha256_hashes_per_second': num_iterations / sha256_time,
            'smhash_hashes_per_second': num_iterations / smhash_time
        }

    def avalanche_test(self, num_tests=1000):
        """Test avalanche effect (how much output changes for small input changes)."""
        sha256_differences = []
        smhash_differences = []

        for _ in range(num_tests):
            # Generate two strings that differ by one character
            str1 = self.generate_random_string()
            str2 = str1[:-1] + chr(ord(str1[-1]) ^ 1)  # Flip one bit in last char

            # Get hashes
            sha256_hash1 = self.sha256.hash(str1.encode('utf-8'))
            sha256_hash2 = self.sha256.hash(str2.encode('utf-8'))
            smhash_hash1 = smhash.hash_string(str1)
            smhash_hash2 = smhash.hash_string(str2)

            # Calculate bit differences
            sha256_diff = self.bit_difference(sha256_hash1, sha256_hash2)
            smhash_diff = self.bit_difference(smhash_hash1, smhash_hash2)

            sha256_differences.append(sha256_diff)
            smhash_differences.append(smhash_diff)

        return {
            'sha256_avg_diff': sum(sha256_differences) / len(sha256_differences),
            'smhash_avg_diff': sum(smhash_differences) / len(smhash_differences),
            'sha256_differences': sha256_differences,
            'smhash_differences': smhash_differences
        }

    def distribution_test(self, num_tests=1000):
        """Test distribution of hash values."""
        sha256_first_bytes = defaultdict(int)
        smhash_first_bytes = defaultdict(int)

        for _ in range(num_tests):
            test_str = self.generate_random_string()

            sha256_hash = self.sha256.hash(test_str.encode('utf-8'))
            smhash_hash = smhash.hash_string(test_str)

            # Count distribution of first byte
            sha256_first_bytes[sha256_hash[:2]] += 1
            smhash_first_bytes[smhash_hash[:2]] += 1

        return {
            'sha256_distribution': dict(sha256_first_bytes),
            'smhash_distribution': dict(smhash_first_bytes)
        }

    def collision_test(self, num_tests=10000):
        """Test for hash collisions with small strings."""
        sha256_hashes = set()
        smhash_hashes = set()
        inputs = set()

        for _ in range(num_tests):
            test_str = self.generate_random_string(5)  # Small strings to increase collision chance
            inputs.add(test_str)

            sha256_hashes.add(self.sha256.hash(test_str.encode('utf-8')))
            smhash_hashes.add(smhash.hash_string(test_str))

        return {
            'inputs': len(inputs),
            'sha256_unique': len(sha256_hashes),
            'smhash_unique': len(smhash_hashes)
        }

    def plot_distribution(self, distribution_data):
        """Plot hash value distributions."""
        plt.figure(figsize=(15, 5))

        # SHA-256 distribution
        plt.subplot(121)
        plt.bar(range(len(distribution_data['sha256_distribution'])),
                list(distribution_data['sha256_distribution'].values()))
        plt.title('SHA-256 Hash Distribution')
        plt.xlabel('First Byte (hex)')
        plt.ylabel('Frequency')

        # smhash distribution
        plt.subplot(122)
        plt.bar(range(len(distribution_data['smhash_distribution'])),
                list(distribution_data['smhash_distribution'].values()))
        plt.title('smhash Hash Distribution')
        plt.xlabel('First Byte (hex)')
        plt.ylabel('Frequency')

        plt.tight_layout()
        plt.show()


def main():
    analyzer = HashAnalyzer()

    # Speed Test
    print("\n=== Speed Test ===")
    #speed_results = analyzer.speed_test()
    speed_results = analyzer.speed_test(num_iterations=10000)
    print(f"SHA-256: {speed_results['sha256_hashes_per_second']:.2f} hashes/second")
    print(f"smhash: {speed_results['smhash_hashes_per_second']:.2f} hashes/second")

    # Avalanche Test
    print("\n=== Avalanche Effect Test ===")
    #avalanche_results = analyzer.avalanche_test()
    avalanche_results = analyzer.avalanche_test(num_tests=10000)
    print(f"SHA-256 average bit difference: {avalanche_results['sha256_avg_diff']:.2f} bits")
    print(f"smhash average bit difference: {avalanche_results['smhash_avg_diff']:.2f} bits")

    # Collision Test
    print("\n=== Collision Test ===")
    collision_results = analyzer.collision_test()
    print(f"Input strings: {collision_results['inputs']}")
    print(f"SHA-256 unique hashes: {collision_results['sha256_unique']}")
    print(f"smhash unique hashes: {collision_results['smhash_unique']}")

    # Distribution Test and Plot
    distribution_results = analyzer.distribution_test()
    analyzer.plot_distribution(distribution_results)


if __name__ == "__main__":
    main()