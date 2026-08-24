import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging(app):

    # Create logs folder
    log_folder = app.config["LOG_FOLDER"]
    os.makedirs(log_folder, exist_ok=True)

    # Log format
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    # Application logger
    app_logger = logging.getLogger("lms.app")
    app_logger.setLevel(logging.INFO)
    app_logger.propagate = False

    if not app_logger.handlers:

        handler = RotatingFileHandler(
            os.path.join(log_folder, "application.log"),
            maxBytes=5 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8"
        )

        handler.setFormatter(formatter)
        app_logger.addHandler(handler)

    # Audit logger
    audit_logger = logging.getLogger("lms.audit")
    audit_logger.setLevel(logging.INFO)
    audit_logger.propagate = False

    if not audit_logger.handlers:

        handler = RotatingFileHandler(
            os.path.join(log_folder, "audit.log"),
            maxBytes=10 * 1024 * 1024,
            backupCount=10,
            encoding="utf-8"
        )

        handler.setFormatter(formatter)
        audit_logger.addHandler(handler)


def app_log(level, message, *args):

    logger = logging.getLogger("lms.app")

    getattr(logger, level)(message, *args)


def audit_log(message, *args):

    logger = logging.getLogger("lms.audit")

    logger.info(message, *args)