import time
import random
import string
import statistics
from collections import defaultdict
import matplotlib.pyplot as plt
import smhash
from sha256 import SHA256


class CryptoAnalyzer:
    def __init__(self):
        self.sha256 = SHA256()

    def generate_random_string(self, length=10):
        """Generate a random string of given length."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def hex_to_binary(self, hex_str: str) -> str:
        """Convert a hexadecimal string to binary string."""
        return ''.join(bin(int(c, 16))[2:].zfill(4) for c in hex_str)

    def hamming_distance(self, str1: str, str2: str) -> int:
        """Calculate the Hamming distance between two binary strings."""
        return sum(c1 != c2 for c1, c2 in zip(str1, str2))

    def test_preimage_resistance(self, num_tests=1000, target_prefix='00'):
        """
        Test preimage resistance by trying to find inputs that produce hashes
        starting with specific prefixes.
        """
        sha256_attempts = []
        smhash_attempts = []

        for _ in range(num_tests):
            attempts = 0
            while True:
                attempts += 1
                test_str = self.generate_random_string()
                if smhash.hash_string(test_str).startswith(target_prefix):
                    smhash_attempts.append(attempts)
                    break
                if attempts > 10000:  # Limit attempts to prevent infinite loops
                    smhash_attempts.append(10000)
                    break

            attempts = 0
            while True:
                attempts += 1
                test_str = self.generate_random_string()
                if self.sha256.hash(test_str.encode('utf-8')).startswith(target_prefix):
                    sha256_attempts.append(attempts)
                    break
                if attempts > 10000:
                    sha256_attempts.append(10000)
                    break

        return {
            'sha256_avg_attempts': statistics.mean(sha256_attempts),
            'smhash_avg_attempts': statistics.mean(smhash_attempts),
            'sha256_attempts': sha256_attempts,
            'smhash_attempts': smhash_attempts
        }

    def test_collision_resistance(self, num_pairs=1000):
        """
        Test collision resistance by generating pairs of similar inputs
        and analyzing their hash differences.
        """
        sha256_collisions = []
        smhash_collisions = []

        for _ in range(num_pairs):
            # Generate two similar strings
            str1 = self.generate_random_string()
            str2 = str1[:-1] + chr(ord(str1[-1]) ^ 1)

            # Get hashes
            sha256_hash1 = self.sha256.hash(str1.encode('utf-8'))
            sha256_hash2 = self.sha256.hash(str2.encode('utf-8'))
            smhash_hash1 = smhash.hash_string(str1)
            smhash_hash2 = smhash.hash_string(str2)

            # Check for partial collisions (matching bits)
            sha256_bin1 = self.hex_to_binary(sha256_hash1)
            sha256_bin2 = self.hex_to_binary(sha256_hash2)
            smhash_bin1 = self.hex_to_binary(smhash_hash1)
            smhash_bin2 = self.hex_to_binary(smhash_hash2)

            sha256_collisions.append(self.hamming_distance(sha256_bin1, sha256_bin2))
            smhash_collisions.append(self.hamming_distance(smhash_bin1, smhash_bin2))

        return {
            'sha256_avg_diff': statistics.mean(sha256_collisions),
            'smhash_avg_diff': statistics.mean(smhash_collisions),
            'sha256_min_diff': min(sha256_collisions),
            'smhash_min_diff': min(smhash_collisions)
        }

    def test_avalanche_effect(self, num_tests=1000):
        """
        Test the avalanche effect by measuring how changing one bit affects the output.
        """
        sha256_changes = []
        smhash_changes = []

        for _ in range(num_tests):
            # Generate original string and modified string (1 bit different)
            orig_str = self.generate_random_string()
            mod_str = orig_str[:-1] + chr(ord(orig_str[-1]) ^ 1)

            # Get original and modified hashes
            sha256_orig = self.hex_to_binary(self.sha256.hash(orig_str.encode('utf-8')))
            sha256_mod = self.hex_to_binary(self.sha256.hash(mod_str.encode('utf-8')))
            smhash_orig = self.hex_to_binary(smhash.hash_string(orig_str))
            smhash_mod = self.hex_to_binary(smhash.hash_string(mod_str))

            # Calculate percentage of bits changed
            sha256_changes.append(self.hamming_distance(sha256_orig, sha256_mod) / len(sha256_orig) * 100)
            smhash_changes.append(self.hamming_distance(smhash_orig, smhash_mod) / len(smhash_orig) * 100)

        return {
            'sha256_avg_change': statistics.mean(sha256_changes),
            'smhash_avg_change': statistics.mean(smhash_changes),
            'sha256_std_dev': statistics.stdev(sha256_changes),
            'smhash_std_dev': statistics.stdev(smhash_changes)
        }

    def test_distribution_uniformity(self, num_tests=10000):
        """
        Test the uniformity of hash distribution across the output space.
        """
        sha256_dist = defaultdict(int)
        smhash_dist = defaultdict(int)

        for _ in range(num_tests):
            input_str = self.generate_random_string()

            sha256_hash = self.sha256.hash(input_str.encode('utf-8'))[:2]  # First byte
            smhash_hash = smhash.hash_string(input_str)[:2]  # First byte

            sha256_dist[sha256_hash] += 1
            smhash_dist[smhash_hash] += 1

        # Calculate chi-square statistic for uniformity
        expected = num_tests / 256  # Expected count for perfect uniformity

        sha256_chi = sum((obs - expected) ** 2 / expected for obs in sha256_dist.values())
        smhash_chi = sum((obs - expected) ** 2 / expected for obs in smhash_dist.values())

        return {
            'sha256_chi_square': sha256_chi,
            'smhash_chi_square': smhash_chi,
            'sha256_distribution': dict(sha256_dist),
            'smhash_distribution': dict(smhash_dist)
        }

    def plot_security_metrics(self, avalanche_results, distribution_results):
        """Plot security metrics for visual comparison."""
        plt.figure(figsize=(15, 10))

        # Plot avalanche effect
        plt.subplot(2, 1, 1)
        algorithms = ['SHA-256', 'smhash']
        avalanche_values = [avalanche_results['sha256_avg_change'],
                            avalanche_results['smhash_avg_change']]
        plt.bar(algorithms, avalanche_values)
        plt.title('Avalanche Effect (Average Bit Changes %)')
        plt.ylabel('Percentage of Bits Changed')

        # Plot distribution uniformity
        plt.subplot(2, 1, 2)
        sha256_dist = list(distribution_results['sha256_distribution'].values())
        smhash_dist = list(distribution_results['smhash_distribution'].values())

        plt.plot(sha256_dist, label='SHA-256', alpha=0.5)
        plt.plot(smhash_dist, label='smhash', alpha=0.5)
        plt.title('Hash Value Distribution')
        plt.xlabel('Hash Value (First Byte)')
        plt.ylabel('Frequency')
        plt.legend()

        plt.tight_layout()
        plt.show()


def main():
    analyzer = CryptoAnalyzer()

    print("=== Cryptographic Security Analysis ===\n")

    # Test preimage resistance
    print("Testing Preimage Resistance...")
    preimage_results = analyzer.test_preimage_resistance()
    print(f"Average attempts to find matching prefix:")
    print(f"SHA-256: {preimage_results['sha256_avg_attempts']:.2f}")
    print(f"smhash: {preimage_results['smhash_avg_attempts']:.2f}\n")

    # Test collision resistance
    print("Testing Collision Resistance...")
    collision_results = analyzer.test_collision_resistance()
    print(f"Average bit differences in similar inputs:")
    print(f"SHA-256: {collision_results['sha256_avg_diff']:.2f} bits")
    print(f"smhash: {collision_results['smhash_avg_diff']:.2f} bits")
    print(f"Minimum bit differences found:")
    print(f"SHA-256: {collision_results['sha256_min_diff']} bits")
    print(f"smhash: {collision_results['smhash_min_diff']} bits\n")

    # Test avalanche effect
    print("Testing Avalanche Effect...")
    avalanche_results = analyzer.test_avalanche_effect()
    print(f"Average percentage of bits changed:")
    print(f"SHA-256: {avalanche_results['sha256_avg_change']:.2f}%")
    print(f"smhash: {avalanche_results['smhash_avg_change']:.2f}%")
    print(f"Standard deviation of bit changes:")
    print(f"SHA-256: {avalanche_results['sha256_std_dev']:.2f}%")
    print(f"smhash: {avalanche_results['smhash_std_dev']:.2f}%\n")

    # Test distribution uniformity
    print("Testing Distribution Uniformity...")
    distribution_results = analyzer.test_distribution_uniformity()
    print(f"Chi-square test results (lower is better):")
    print(f"SHA-256: {distribution_results['sha256_chi_square']:.2f}")
    print(f"smhash: {distribution_results['smhash_chi_square']:.2f}\n")

    # Plot results
    analyzer.plot_security_metrics(avalanche_results, distribution_results)


if __name__ == "__main__":
    main()