from flask import Flask, jsonify
from flask_cors import CORS
import logging
from config import PATH_CONFIG  # Import PATH_CONFIG

# Import blueprints
from blueprints.replica import replica_blueprint
from blueprints.recovery import recover_blueprint
from blueprints.catcheck import catcheck_blueprint
from blueprints.walfounder import wal_blueprint
from blueprints.auth import auth_blueprint
from blueprints.dbadder import dbadder_blueprint
from blueprints.logfile import logs_blueprint

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Setup CORS (Cross-Origin Resource Sharing)
    CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )
    app.logger.info("Flask application initialized.")

    # Register blueprints
    blueprints = [
        replica_blueprint,
        recover_blueprint,
        catcheck_blueprint,
        wal_blueprint,
        auth_blueprint,
        dbadder_blueprint,
        logs_blueprint
    ]
    for blueprint in blueprints:
        app.register_blueprint(blueprint, url_prefix="/api")
        app.logger.info(f"Registered blueprint: {blueprint.name}")

    # Add global error handler
    @app.errorhandler(Exception)
    def handle_exception(e):
        """Global error handler for unhandled exceptions."""
        app.logger.error(f"Unhandled exception: {e}")
        response = {
            "status": "error",
            "message": str(e),
        }
        return jsonify(response), 500

    # Add route to fetch PATH_CONFIG
    @app.route("/api/get-path-config", methods=["GET"])
    def get_path_config():
        """API route to fetch paths from PATH_CONFIG."""
        try:
            paths = list(PATH_CONFIG.values())
            return jsonify({"paths": paths}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return app


if __name__ == "__main__":
    app = create_app()
    app.logger.info("Starting Flask application.")
    app.run(host="0.0.0.0", port=5000, debug=True)
