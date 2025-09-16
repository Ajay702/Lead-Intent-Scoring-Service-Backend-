from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from .config import Config
import os
import time
import errno

# Global db instance
db = SQLAlchemy()
migrate = Migrate()

def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    # Load configuration
    if test_config:
        app.config.from_mapping(test_config)
    else:
        app.config.from_object(Config)

    # Ensure instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    # Normalize SQLite URI to absolute path for Docker compatibility
    uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    if uri.startswith("sqlite:///"):
        path_part = uri[len("sqlite:///"):]
        # Only process relative paths
        is_absolute = path_part.startswith("/") or (len(path_part) > 1 and path_part[1] == ":")
        if not is_absolute:
            if path_part.startswith("instance/"):
                abs_path = os.path.join(app.instance_path, path_part[len("instance/"):])
            else:
                abs_path = os.path.join(app.root_path, path_part)
            
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            # Ensure DB file exists
            if not os.path.exists(abs_path):
                open(abs_path, "a").close()
            
            # Convert to POSIX path for SQLite URI
            abs_posix = abs_path.replace("\\", "/")
            if not abs_posix.startswith("/"):
                abs_posix = "/" + abs_posix
            app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{abs_posix}"

    # Init extensions
    app.config.setdefault("SQLALCHEMY_ENGINE_OPTIONS", {"pool_pre_ping": True})
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from .routes import bp as api_bp
    app.register_blueprint(api_bp)

    # Auto-create tables if enabled (useful for Docker without migrations)
    if not test_config and getattr(Config, "AUTO_CREATE_DB", False):
        _init_database(app)

    return app


def _init_database(app):
    """Initialize database with lock to prevent race conditions between workers."""
    lock_path = os.path.join(app.instance_path, "db_init.lock")
    sentinel_path = os.path.join(app.instance_path, ".db_initialized")

    def _try_acquire_lock(path: str) -> bool:
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            return True
        except OSError as e:
            return e.errno != errno.EEXIST

    def _release_lock(path: str):
        try:
            os.remove(path)
        except OSError:
            pass

    if not os.path.exists(sentinel_path):
        if _try_acquire_lock(lock_path):
            try:
                with app.app_context():
                    db.create_all()
                with open(sentinel_path, "w") as f:
                    f.write("ok")
            finally:
                _release_lock(lock_path)
        else:
            # Wait for other worker to finish
            for _ in range(40):  # up to ~20s
                if os.path.exists(sentinel_path):
                    break
                time.sleep(0.5)
