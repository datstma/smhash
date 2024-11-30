class SHA256:
    def __init__(self):
        # Initialize hash values (first 32 bits of the fractional parts of the square roots of the first 8 primes)
        self.h = [
            0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
            0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19
        ]

        # Initialize round constants (first 32 bits of the fractional parts of the cube roots of the first 64 primes)
        self.k = [
            0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
            0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
            0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
            0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
            0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
            0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
            0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
            0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
        ]

    def _right_rotate(self, x: int, n: int) -> int:
        """Rotate a 32-bit integer right by n bits."""
        return ((x >> n) | (x << (32 - n))) & 0xFFFFFFFF

    def _sha256_functions(self, x: int, y: int, z: int, operation: str) -> int:
        """SHA-256 functions Ch (choice) and Maj (majority)."""
        if operation == "Ch":
            return (x & y) ^ (~x & z)
        return (x & y) ^ (x & z) ^ (y & z)  # Maj

    def _sigma(self, x: int, operation: str) -> int:
        """SHA-256 σ operations."""
        if operation == "big_0":
            return self._right_rotate(x, 2) ^ self._right_rotate(x, 13) ^ self._right_rotate(x, 22)
        elif operation == "big_1":
            return self._right_rotate(x, 6) ^ self._right_rotate(x, 11) ^ self._right_rotate(x, 25)
        elif operation == "small_0":
            return self._right_rotate(x, 7) ^ self._right_rotate(x, 18) ^ (x >> 3)
        return self._right_rotate(x, 17) ^ self._right_rotate(x, 19) ^ (x >> 10)  # small_1

    def _pad_message(self, message: bytes) -> bytes:
        """Pad the message according to SHA-256 specifications."""
        message_len = len(message) * 8
        message = bytearray(message)
        message.append(0x80)
        while (len(message) * 8 + 64) % 512 != 0:
            message.append(0x00)
        message.extend(message_len.to_bytes(8, 'big'))
        return bytes(message)

    def _process_block(self, block: bytes) -> None:
        """Process a 512-bit block."""
        # Create message schedule
        w = [0] * 64
        for i in range(16):
            w[i] = int.from_bytes(block[i * 4:(i + 1) * 4], 'big')

        for i in range(16, 64):
            s0 = self._sigma(w[i - 15], "small_0")
            s1 = self._sigma(w[i - 2], "small_1")
            w[i] = (w[i - 16] + s0 + w[i - 7] + s1) & 0xFFFFFFFF

        # Initialize working variables
        a, b, c, d, e, f, g, h = self.h

        # Main loop
        for i in range(64):
            S1 = self._sigma(e, "big_1")
            ch = self._sha256_functions(e, f, g, "Ch")
            temp1 = (h + S1 + ch + self.k[i] + w[i]) & 0xFFFFFFFF
            S0 = self._sigma(a, "big_0")
            maj = self._sha256_functions(a, b, c, "Maj")
            temp2 = (S0 + maj) & 0xFFFFFFFF

            h = g
            g = f
            f = e
            e = (d + temp1) & 0xFFFFFFFF
            d = c
            c = b
            b = a
            a = (temp1 + temp2) & 0xFFFFFFFF

        # Update hash values
        self.h = [(x + y) & 0xFFFFFFFF for x, y in zip(self.h, [a, b, c, d, e, f, g, h])]

    def hash(self, message: bytes) -> str:
        """Compute SHA-256 hash of the message."""
        # Reset hash values
        self.__init__()

        # Pad message
        padded = self._pad_message(message)

        # Process message in 512-bit blocks
        for i in range(0, len(padded), 64):
            self._process_block(padded[i:i + 64])

        # Produce final hash value (concatenate hash values)
        return ''.join(f'{x:08x}' for x in self.h)


def hash_string(text: str) -> str:
    """Hash a string using SHA-256."""
    sha256 = SHA256()
    return sha256.hash(text.encode('utf-8'))


def hash_bytes(byte_data: bytes) -> str:
    """Hash bytes using SHA-256."""
    sha256 = SHA256()
    return sha256.hash(byte_data)