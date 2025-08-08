from chordauth.ChordAuth import *
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from waitress import serve
import os
import getpass
import time
import hmac
import hashlib
import uuid
import json
import threading
from filelock import FileLock
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
from base64 import urlsafe_b64encode, urlsafe_b64decode
import base64

HERE = os.path.dirname(os.path.abspath(__file__))

def local_path(filename):
    return os.path.join(HERE, filename)

cab = ChordAuthBackend()
app = Flask(__name__)
initial_block_lock_path = local_path("chordauth_startup.lock")
register_block_lock_path = local_path("chordauth_register.lock")
write_database_block_lock_path = local_path("chordauth_write_database.lock")
get_database_block_lock_path = local_path("chordauth_get_database.lock")
remove_from_database_block_lock_path = local_path("remove_from_database_block_lock_path.lock")
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    storage_uri="memory://"
)

# encryption & decryption
def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return urlsafe_b64encode(kdf.derive(password.encode()))

def encrypt(password: str, string: str) -> str:
    salt = os.urandom(16)
    key = derive_key(password, salt)
    fernet = Fernet(key)
    encrypted = fernet.encrypt(string.encode())
    return urlsafe_b64encode(salt).decode() + ":" + encrypted.decode()
def decrypt(password: str, token: str) -> str:
    salt_b64, encrypted = token.split(":")
    salt = urlsafe_b64decode(salt_b64)
    key = derive_key(password, salt)
    fernet = Fernet(key)
    decrypted = fernet.decrypt(encrypted.encode())
    return decrypted.decode()
# end encryption & decryption
try:
    with FileLock(initial_block_lock_path):
        if os.path.exists(local_path("used_chordauth_already.chordauth_config")):
            try:
                print("Verification process beginning...")
                user_private_key = input("Enter your private key file's path: ").strip()
                user_public_key = input("Enter your public key file's path: ").strip()
                user_passkey = getpass.getpass(prompt="Enter your passkey: ")
                
                with open(str(user_public_key)) as u:
                    user_public_key = u.read()

                with open(local_path("chordauth_public_key.chordauth_config")) as i:
                    integrity_public_key = i.read()

                if not integrity_public_key.strip() == user_public_key.strip():
                    print("This public key is not registered on this machine. Use the intended one please.")
                    exit()
                try:
                    with open(str(user_private_key)) as r:        
                        raw_private_key = r.read()
                    user_private_key = base64.b64decode(decrypt(user_passkey, raw_private_key)).decode()
                except Exception as e:
                    print(f"Your password either is wrong or your private key is corrupted. {e}")
                    exit()
                
                to_be_signed = str(int(time.time()))
                try:
                    signed = cab.sign_data(user_private_key, to_be_signed)
                    if signed[0] == False:
                        print("Invalid information.")
                        print(signed[1])
                        exit()
                    verify = cab.verify_signature(to_be_signed, signed[1], user_public_key)
                    if verify[0] == True:
                        print("Success! Starting server...")
                    else:
                        print("Invalid information.")
                        print(verify[1])
                        exit()
                except Exception as e:
                    print(f"Your keys are invalid or corrupted. {e}")
                    exit()
            except Exception as e:
                print(f"Fatal error: {e}")
                exit()
        else:
            try:
                print("Creating new ChordAuth account.")
                keys = cab.create_keys()
                if keys[0] is True:
                    user_passkey = getpass.getpass(prompt="Pick a password: ")
                    private_key_contents = encrypt(user_passkey, base64.b64encode(keys[2].encode()).decode())
                    public_key_contents = keys[1]
                    
                    private_key_path = str(input("Choose a file path for your private key: "))
                    public_key_path = str(input("Choose a file path for your public key: "))
                    
                    if os.path.exists(private_key_path):
                        print("The private key path already exists. Pick another one.")
                        exit()
                    
                    if os.path.exists(public_key_path):
                        print("This public key path already exists. Pick another one.")
                        exit()
                    
                    with open(private_key_path, "w") as file:
                        file.write(private_key_contents)
                    with open(public_key_path, "w") as file:
                        file.write(public_key_contents)
                    with open(local_path("used_chordauth_already.chordauth_config"), 'w') as f:
                        f.write("Already used.")
                    
                    with open(local_path("chordauth_public_key.chordauth_config"), "w") as file:
                        file.write(public_key_contents)
                    
                    print("Success, keys created in desired locations. Please restart the application.")
                    exit()
                else:
                    print("Backend error.")
                    exit()
            except Exception as e:
                print(f"Fatal error: {e}")
                exit()
except Exception as e:
    print(f"Fatal error: {e}")
    exit()
    
@app.route("/api/auth", methods=["POST"])
@limiter.limit("10 per minute")
def auth():
    try:
        data = request.get_json()
        challenge = data.get("challenge")
        if challenge is not None:
            if isinstance(challenge, str):
                if challenge.isalnum():
                    response = cab.sign_data(user_private_key, challenge)
                    if response[0] == True:
                        return response[1]
                    else:
                        return "Could not sign data.", 500
                else:
                    return "Challenge must be alphanumerical.", 400
            else:
                return "Challenge JSON field must be a string.", 400
        else:
            return "Missing challenge JSON field.", 400
    except:
        return "Generic Error", 400

@app.route("/api/register", methods=["POST"])
@limiter.limit("2 per hour")
def register():
    try:
        with FileLock(register_block_lock_path):
            unique_id = str(uuid.uuid4())
            api_key = hmac.new(key=user_private_key.encode(), msg=unique_id.encode(), digestmod=hashlib.sha256).hexdigest()
            cab.create_group(unique_id, "{}", "chord_auth_database.json")
            
            if not os.path.exists(local_path("chord_auth_api_keys.json")):
                keys_dict = {}
            else:
                with open(local_path('chord_auth_api_keys.json'), 'r') as file:
                    keys_dict = json.load(file)
            
            keys_dict[hashlib.sha256(api_key.encode()).hexdigest()] = unique_id
            
            with open(local_path('chord_auth_api_keys.json'), 'w') as f:
                json.dump(keys_dict, f)
                
            return jsonify(api_key=api_key, unique_id=unique_id), 200
    except:
        return "Generic Error", 400
    
@app.route("/api/write_database", methods=["POST"])
@limiter.limit("10 per minute")
def write_database():
    try:
        with FileLock(write_database_block_lock_path):
            data = request.get_json()
            api_key = data.get("api_key")
            new_json = data.get("new_json")

            if not os.path.exists(local_path("chord_auth_api_keys.json")):
                return "Database not initialized, also means API key has not been registered.", 400
            else:
                with open(local_path('chord_auth_api_keys.json'), 'r') as file:
                    keys_dict = json.load(file)

            unique_id = keys_dict[hashlib.sha256(api_key.encode()).hexdigest()]
            ideal_api_key = hmac.new(key=user_private_key.encode(), msg=unique_id.encode(), digestmod=hashlib.sha256).hexdigest()

            validity = hmac.compare_digest(api_key, ideal_api_key)

            if validity is True:
                if isinstance(new_json, str):
                    try:
                        parsed_json_data = json.loads(new_json)
                        if isinstance(parsed_json_data, dict):
                            response = cab.edit_group(unique_id, new_json, "chord_auth_database.json")
                            if response[0] is True:
                                return "Success!", 200
                            else:
                                return "General error.", 400
                        else:
                            return "JSON must be a dictionary.", 400
                    except:
                        return "JSON is corrupted or invalid.", 400
                else:
                    return "JSON must be a string.", 400
            else:
                return "Invalid API Key", 400
    except:
        return "Generic Error", 400

@app.route("/api/get_database", methods=["POST"])
@limiter.limit("10 per minute")
def get_database():
    try:
        with FileLock(get_database_block_lock_path):
            data = request.get_json()
            api_key = data.get("api_key")
            
            if not os.path.exists(local_path("chord_auth_api_keys.json")):
                return "Key database not initialized, also means API key has not been registered.", 400
            else:
                with open(local_path('chord_auth_api_keys.json'), 'r') as file:
                    keys_dict = json.load(file)

            unique_id = keys_dict[hashlib.sha256(api_key.encode()).hexdigest()]
            ideal_api_key = hmac.new(key=user_private_key.encode(), msg=unique_id.encode(), digestmod=hashlib.sha256).hexdigest()

            validity = hmac.compare_digest(api_key, ideal_api_key)

            if validity is True:
                if not os.path.exists(local_path("chord_auth_database.json")):
                    return "Storage database not initialized.", 400
                else:
                    with open(local_path('chord_auth_database.json'), 'r') as file:
                        chord_db = json.load(file)
                for item in chord_db:
                    if item["group_name"] == keys_dict[hashlib.sha256(api_key.encode()).hexdigest()]:
                        return str(json.dumps(item["json_contents"])), 200
                return "Group not found.", 400
            else:
                return "Invalid API Key", 400
    except:
        return "Generic Error", 400
@app.route("/api/remove_from_database", methods=["POST"])
@limiter.limit("10 per minute")
def remove_from_database():
    try:
        with FileLock(remove_from_database_block_lock_path):
            data = request.get_json()
            api_key = data.get("api_key")
            passkey = data.get("passkey")
            group = data.get("group")

            if (api_key and passkey) or (not api_key and not passkey):
                return "Request must contain exactly one of 'api_key' or 'passkey'.", 400
            if api_key and group:
                return "The API key does not require the group field.", 400
            if passkey and not group:
                return "The passkey requires the group field.", 400

            
            if api_key:
                if not os.path.exists(local_path("chord_auth_api_keys.json")):
                    return "Key database not initialized, also means API key has not been registered.", 400
                else:
                    with open(local_path('chord_auth_api_keys.json'), 'r') as file:
                        keys_dict = json.load(file)

                unique_id = keys_dict[hashlib.sha256(api_key.encode()).hexdigest()]
                ideal_api_key = hmac.new(key=user_private_key.encode(), msg=unique_id.encode(), digestmod=hashlib.sha256).hexdigest()

                validity = hmac.compare_digest(api_key, ideal_api_key)

                if validity is True:
                    if not os.path.exists(local_path("chord_auth_database.json")):
                        return "Storage database not initialized.", 400
                    else:
                        with open(local_path('chord_auth_database.json'), 'r') as file:
                            chord_db = json.load(file)
                    i = -1
                    for item in chord_db:
                        i += 1
                        if item["group_name"] == keys_dict[hashlib.sha256(api_key.encode()).hexdigest()]:
                            del chord_db[i]
                            with open(local_path('chord_auth_database.json'), 'w') as file:
                                json.dump(chord_db, file)
                            del keys_dict[hashlib.sha256(api_key.encode()).hexdigest()]
                            with open(local_path('chord_auth_api_keys.json'), 'w') as file:
                                json.dump(keys_dict, file)
                            return "Success!", 200
                    return "Group not found.", 400
                else:
                    return "Invalid API Key", 400
            elif passkey:
                if passkey == user_passkey:
                    if not os.path.exists(local_path("chord_auth_database.json")):
                        return "Storage database not initialized.", 400
                    else:
                        with open(local_path('chord_auth_database.json'), 'r') as file:
                            chord_db = json.load(file)
                    i = -1
                    for item in chord_db:
                        i += 1
                        if item["group_name"] == group:
                            del chord_db[i]
                            with open(local_path('chord_auth_database.json'), 'w') as file:
                                json.dump(chord_db, file)

                            with open(local_path('chord_auth_api_keys.json'), 'r') as file:
                                keys_dict = json.load(file)
                            
                            for key in list(keys_dict.keys()):
                                if keys_dict[key] == item["group_name"]:
                                    del keys_dict[key]
                                    with open(local_path('chord_auth_api_keys.json'), 'w') as file:
                                        json.dump(keys_dict, file)
                                    return "Success!", 200
                            
                            return "Group found, but deletion unsuccessful.", 400
                    return "Group not found.", 400
            else:
                return "Request must contain exactly one of 'api_key' or 'passkey'.", 400
            return "Fatal error.", 500  
    except:
        return "Generic Error", 400
@app.route("/api/public_key", methods=["GET"])
@limiter.limit("20 per minute")
def public_key():
    try:
        return user_public_key, 200
    except:
        return "Fatal error.", 400
@app.route("/api/ping", methods=["GET"])
@limiter.limit("50 per minute")
def ping():
    try:
        return "Pinged!", 200
    except:
        return "Fatal error.", 400
def run_app():
    serve(app, host='127.0.0.1', port=5001)
