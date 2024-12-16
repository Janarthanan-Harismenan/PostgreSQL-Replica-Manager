from flask import Flask, jsonify, request
from flask_cors import CORS
from blueprints.replica import replica_blueprint
from blueprints.recovery import recover_blueprint # Ensure this is properly imported
from blueprints.catcheck import catcheck_blueprint
from blueprints.walfounder import wal_blueprint

app = Flask(__name__)

# CORS for the API routes
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

# Register the blueprints
app.register_blueprint(replica_blueprint, url_prefix="/api")
app.register_blueprint(catcheck_blueprint, url_prefix="/api")
app.register_blueprint(wal_blueprint, url_prefix="/api")
app.register_blueprint(recover_blueprint, url_prefix="/api")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)



