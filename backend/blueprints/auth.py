from flask import Blueprint, request, jsonify
from utils.user_handler import load_users, save_users, hash_password, verify_password
 
auth_blueprint = Blueprint("auth", __name__)
 
@auth_blueprint.route("/signup", methods=["POST"])
def signup():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
 
    if not name or not email or not password:
        return jsonify({"message": "All fields are required!"}), 400
 
    users = load_users()
 
    # Check if email already exists
    if email in users:
        return jsonify({"message": "Email is already registered!"}), 409
 
    # Hash password and save user
    hashed_password = hash_password(password)
    users[email] = {"name": name, "password": hashed_password}
    save_users(users)
 
    return jsonify({"message": "Signup successful!"}), 201
 
@auth_blueprint.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")
 
    if not email or not password:
        return jsonify({"message": "All fields are required!"}), 400
 
    users = load_users()
 
    # Check if email exists
    if email not in users:
        return jsonify({"message": "Email is not registered!"}), 404
 
    # Verify password
    if not verify_password(password, users[email]["password"]):
        return jsonify({"message": "Incorrect password!"}), 401
 
    return jsonify({"message": "Login successful!"}), 200