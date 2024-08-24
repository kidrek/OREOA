import hashlib, logging, os, subprocess

def sha256_generate(filepath:str):
    logging.info(f'Task SHA256 : Generate Hash')

    sha256_hash = hashlib.sha256()
    with open(filepath,"rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096),b""):
            sha256_hash.update(byte_block)
        with open(f"{filepath}.sha256","w") as f:
            f.write(sha256_hash.hexdigest())
        return(f"Filepath: {filepath} / SHA256: {sha256_hash.hexdigest()}")


