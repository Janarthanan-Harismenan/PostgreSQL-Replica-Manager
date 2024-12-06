from flask import Flask
from blueprints.replica import replica_blueprint
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})


# Enable CORS for all routes
# CORS(app)
    
# Register blueprints
app.register_blueprint(replica_blueprint, url_prefix="/api")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)