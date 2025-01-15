# from flask import Flask, jsonify
# from flask_cors import CORS
# import logging

# # Import blueprints
# from blueprints.replica import replica_blueprint
# from blueprints.recovery import recovery_blueprint
# from blueprints.catcheck import catcheck_blueprint
# from blueprints.walfounder import wal_blueprint
# from blueprints.auth import auth_blueprint
# from blueprints.dbadder import dbadder_blueprint
# from blueprints.logfile import logs_blueprint

# def create_app():
#     """Create and configure the Flask application."""
#     app = Flask(__name__)

#     # Setup CORS (Cross-Origin Resource Sharing)
#     CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

#     # Configure logging
#     logging.basicConfig(
#         level=logging.INFO,
#         format="%(asctime)s - %(levelname)s - %(message)s",
#         handlers=[logging.StreamHandler()],
#     )
#     app.logger.info("Flask application initialized.")

#     # Register blueprints
#     blueprints = [
#         replica_blueprint,
#         recovery_blueprint,
#         catcheck_blueprint,
#         wal_blueprint,
#         auth_blueprint,
#         dbadder_blueprint,
#         logs_blueprint
#     ]
#     for blueprint in blueprints:
#         app.register_blueprint(blueprint, url_prefix="/api")
#         app.logger.info(f"Registered blueprint: {blueprint.name}")

#     # Add global error handler
#     @app.errorhandler(Exception)
#     def handle_exception(e):
#         """Global error handler for unhandled exceptions."""
#         app.logger.error(f"Unhandled exception: {e}")
#         response = {
#             "status": "error",
#             "message": str(e),
#         }
#         return jsonify(response), 500
    
#     return app


# if __name__ == "__main__":
#     app = create_app()
#     app.logger.info("Starting Flask application.")
#     app.run(host="0.0.0.0", port=5000, debug=True)

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import logging
import threading
import time
import requests
import csv
import os
 
# Import blueprints
from blueprints.replica import replica_blueprint
from blueprints.recovery import recovery_blueprint
from blueprints.catcheck import catcheck_blueprint
from blueprints.walfounder import wal_blueprint
from blueprints.auth import auth_blueprint
from blueprints.dbadder import dbadder_blueprint
from blueprints.logfile import logs_blueprint
from utils.replica_manager import fetch_replica_status
 
 
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
        recovery_blueprint,
        catcheck_blueprint,
        wal_blueprint,
        auth_blueprint,
        dbadder_blueprint,
        logs_blueprint,
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
 
    # # Route to serve the CSV file
    # @app.route('/api/static/replica_status', methods=['GET'])
    # def serve_csv():
    #     """Serve the replica status CSV file."""
    #     try:
    #         return send_from_directory(
    #             os.path.join(app.root_path, 'static'),  # Path to static folder
    #             'replica_status.csv',                   # File to serve
    #             mimetype='text/csv'                     # Correct mime type for CSV
    #         )
    #     except Exception as e:
    #         app.logger.error(f"Error serving CSV: {e}")
    #         return jsonify({"error": "Failed to fetch CSV file"}), 500
 
    # Start background thread for periodic API calls
    threading.Thread(target=fetch_replica_status, daemon=True).start()
 
    return app
 
 
if __name__ == "__main__":
    app = create_app()
    app.logger.info("Starting Flask application.")
    app.run(host="0.0.0.0", port=5000, debug=True)