from filelock import FileLock
import threading
import hashlib
import json
import rsa
import os

# ChordAuth by SeafoodStudios
# https://seafoodstudios.com/
# ChordAuth is a decentralized authentication system.
# The user can authenticate using the usual private/public key pairs.
# The data of the user is all stored locally as a JSON dictionary.
# The server can check authenticity by storing a hash of the JSON and comparing it with the local one.

class ChordAuthBackend:
    _lock = threading.Lock()
    def __init__(self):
        self.HERE = os.path.dirname(os.path.abspath(__file__))
    def local_path(self, filename):
            return os.path.join(self.HERE, filename)
    def create_keys(self):
        try:
            public_key, private_key = rsa.newkeys(2048)
            public_key = public_key.save_pkcs1().decode()
            private_key = private_key.save_pkcs1().decode()
            return True, public_key, private_key
        except Exception as e:
            return False, str(e), None
    def sign_data(self, private_key, string):
        try:
            string = string.encode('utf-8')
            private_key = rsa.PrivateKey.load_pkcs1(private_key.encode())
            signature = rsa.sign(string, private_key, 'SHA-256')
            return True, signature.hex()
        except Exception as e:
            return False, str(e)
    def verify_signature(self, original_string, signed_string, public_key):
        try:
            original_string = original_string.encode('utf-8')
            signed_string = bytes.fromhex(signed_string)
            public_key = rsa.PublicKey.load_pkcs1(public_key.encode())
            rsa.verify(original_string, signed_string, public_key)
        except Exception as e:
            return False, str(e)
        return True, None
    def create_group(self, group_name, json_contents, filepath):
        filepath = self.local_path(filepath)
        lock = FileLock(f"{filepath}.lock")
        try:
            with lock:
                with ChordAuthBackend._lock:
                    if not isinstance(group_name, str):
                        raise ValueError("Group name should be a string.")
                    if not isinstance(json_contents, str):
                        raise ValueError("JSON contents should be a string.")
                    else:
                        try:
                            parsed = json.loads(json_contents)
                            if not isinstance(parsed, dict):
                                raise ValueError("JSON should be a dictionary.")
                        except json.JSONDecodeError:
                            raise ValueError("Invalid JSON.")
                    if not isinstance(filepath, str):
                        raise ValueError("File path should be a string.")
                    
                    if not os.path.exists(filepath):
                        with open(filepath, 'w') as f:
                            json.dump([], f)
                    with open(filepath, 'r') as file:
                        database = json.load(file)
                    
                    for group in database:
                        if group["group_name"] == group_name:
                            raise ValueError("Group name already exists.")
                    new_group_dict = {
                        "group_name" : group_name,
                        "json_contents": parsed
                    }
                    
                    database.append(new_group_dict)
                    temp_path = filepath + '.tmp'
                    with open(temp_path, 'w') as f:
                        json.dump(database, f)
                    os.replace(temp_path, filepath)

                    return True, None
        except Exception as e:
            return False, str(e)
    def remove_group(self, group_name, filepath):
        filepath = self.local_path(filepath)
        lock = FileLock(f"{filepath}.lock")
        try:
            with lock:
                with ChordAuthBackend._lock:
                    if not isinstance(group_name, str):
                        raise ValueError("Group name should be a string.")
                    if not isinstance(filepath, str):
                        raise ValueError("File path should be a string.")
                    if not os.path.exists(filepath):
                        raise ValueError("File path does not exist.")
                    with open(filepath, 'r') as file:
                        database = json.load(file)
                    found = False
                    new_database = []
                    for group in database:
                        if group["group_name"] == group_name:
                            found = True
                        else:
                            new_database.append(group)
                            
                    if not found:
                        return False, "Group not found."
                    
                    temp_path = filepath + '.tmp'
                    with open(temp_path, 'w') as f:
                        json.dump(new_database, f)
                    os.replace(temp_path, filepath)
                    return True, None
        except Exception as e:
            return False, str(e)
    def edit_group(self, group_name, json_contents, filepath):
        filepath = self.local_path(filepath)
        lock = FileLock(f"{filepath}.lock")
        try:
            with lock:
                with ChordAuthBackend._lock:
                    if not isinstance(group_name, str):
                        raise ValueError("Group name should be a string.")
                    if not isinstance(json_contents, str):
                        raise ValueError("JSON contents should be a string.")
                    else:
                        try:
                            parsed = json.loads(json_contents)
                            if not isinstance(parsed, dict):
                                raise ValueError("JSON should be a dictionary.")
                        except json.JSONDecodeError:
                            raise ValueError("Invalid JSON.")
                    if not isinstance(filepath, str):
                        raise ValueError("File path should be a string.")
                    
                    if not os.path.exists(filepath):
                        raise ValueError("File does not exist.")

                    with open(filepath, 'r') as file:
                        database = json.load(file)

                    found = False
                    for group in database:
                        if group["group_name"] == group_name:
                            found = True
                            group["json_contents"] = parsed

                    if not found:
                        return False, "Group does not exist."

                    temp_path = filepath + '.tmp'
                    with open(temp_path, 'w') as f:
                        json.dump(database, f)
                    os.replace(temp_path, filepath)

                    return True, None
        except Exception as e:
            return False, str(e)
    def read_group(self, group_name, filepath):
        filepath = self.local_path(filepath)
        lock = FileLock(f"{filepath}.lock")
        try:
            with lock:
                with ChordAuthBackend._lock:
                    if not isinstance(group_name, str):
                        raise ValueError("Group name should be a string.")
                    if not isinstance(filepath, str):
                        raise ValueError("File path should be a string.")
                    if not os.path.exists(filepath):
                        raise ValueError("File path does not exist.")
                    with open(filepath, 'r') as file:
                        database = json.load(file)
                    found = False
                    found_json = None
                    for group in database:
                        if group["group_name"] == group_name:
                            found = True
                            found_json = group["json_contents"]
                            
                    if found:
                        return True, found_json
                    else:
                        return False, "Group not found."
        except Exception as e:
            return False, str(e)
cab = ChordAuthBackend()
