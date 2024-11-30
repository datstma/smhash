import smhash
import sha256
import time

def main():
    # Your main code goes here
    # Hash a string
    theword = "Hello, world"
    start_time = time.perf_counter()
    result = smhash.hash_string(theword)
    end_time = time.perf_counter()
    print('smHash result for: ', theword)
    print(result)  # 64-character hex string
    elapsed_time = end_time - start_time
    print(f"Time taken: {elapsed_time:.6f} seconds")

    start_time = time.perf_counter()
    result = sha256.hash_string(theword)
    end_time = time.perf_counter()
    print('SHA256 result for: ', theword)
    print(result)  # 64-character hex string
    elapsed_time = end_time - start_time
    print(f"Time taken: {elapsed_time:.6f} seconds")


    # Hash bytes
    ##data = b"Binary data"
    ##result = mhash.hash_bytes(data)
    ##print(result)  # 64-character hex string

if __name__ == "__main__":
    main()