from klvm_rs import Program


def generate_hash_bytes(klvm_bytes: bytes) -> bytes:
    serialized_hash = Program.from_bytes(klvm_bytes).tree_hash()
    return serialized_hash
