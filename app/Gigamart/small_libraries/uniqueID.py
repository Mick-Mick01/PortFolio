import hashlib
import json

def unique_ShopItemId(input):
    dict_bytes = json.dumps(input, sort_keys=True).encode() #//converting dictionary into raw-bytes
    file_hash = hashlib.sha256(dict_bytes).hexdigest()
    unique_name = file_hash
    return unique_name

def uniqueFileId(file):
    file_byte = file.read()
    file_hash = hashlib.sha256(file_bytes).hexdigest()
    unique_name = file_hash
    return unique_name #//Don't forget to add the extension of the file after the filename
