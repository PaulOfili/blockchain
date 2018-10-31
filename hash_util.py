import hashlib
import json


def hash_string_256(string):
    return hashlib.sha256(string).hexdigest()


def convert_to_hash(block):
    # return "-".join([str(block_items) for block_items in block.values()])
    return hash_string_256(json.dumps(block, sort_keys=True).encode())

