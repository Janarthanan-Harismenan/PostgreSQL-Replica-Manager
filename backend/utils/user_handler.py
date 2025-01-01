import json
from flask_bcrypt import Bcrypt
 
bcrypt = Bcrypt()
 
# Load users from JSON file
def load_users():
    try:
        with open("users.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
 
# Save users to JSON file
def save_users(users):
    with open("users.json", "w") as file:
        json.dump(users, file, indent=4)
 
# Hash a password
def hash_password(password):
    return bcrypt.generate_password_hash(password).decode("utf-8")
 
# Verify a password
def verify_password(password, hashed_password):
    return bcrypt.check_password_hash(hashed_password, password)