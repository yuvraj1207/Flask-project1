import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app


class FileValidationError(Exception):
    """Raised when a file fails extension or size validation."""


def _detect_file_type(filename: str):
    """Return (file_type, extension) or (None, extension) if not allowed."""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    for file_type, extensions in current_app.config["ALLOWED_EXTENSIONS"].items():
        if ext in extensions:
            return file_type, ext
    return None, ext


def validate_file(file_storage):
    """
    Validate extension and file size.
    Returns (file_type, extension, size_bytes, secure_filename).
    Raises FileValidationError on failure.
    """
    if not file_storage or not file_storage.filename:
        raise FileValidationError("No file selected.")

    filename  = secure_filename(file_storage.filename)
    if not filename:
        raise FileValidationError("Invalid filename.")

    file_type, ext = _detect_file_type(filename)
    if file_type is None:
        raise FileValidationError(f"File extension '.{ext}' is not allowed.")

    # Measure size without loading entire file into memory
    file_storage.stream.seek(0, os.SEEK_END)
    size = file_storage.stream.tell()
    file_storage.stream.seek(0)

    max_size = current_app.config.get("MAX_FILE_SIZE", {}).get(file_type)
    if max_size and size > max_size:
        mb = max_size // (1024 * 1024)
        raise FileValidationError(
            f"File too large for type '{file_type}'. Max allowed is {mb} MB."
        )

    return file_type, ext, size, filename


def save_course_file(file_storage, course_id: int, module_id: int) -> dict:
    """
    Validate and save the file under static/uploads/courses/<course_id>/<module_id>/.
    Returns a dict with keys: filename, stored_path, file_type, size_bytes.
    """
    file_type, ext, size, filename = validate_file(file_storage)

    unique_name  = f"{uuid.uuid4().hex}_{filename}"
    relative_dir = os.path.join("courses", str(course_id), str(module_id))
    absolute_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], relative_dir)

    try:
        os.makedirs(absolute_dir, exist_ok=True)
    except OSError as exc:
        raise FileValidationError(f"Could not create upload directory: {exc}") from exc

    absolute_path = os.path.join(absolute_dir, unique_name)
    try:
        file_storage.save(absolute_path)
    except OSError as exc:
        raise FileValidationError(f"Could not save file: {exc}") from exc

    relative_path = os.path.join(relative_dir, unique_name).replace("\\", "/")
    return {
        "filename":    filename,
        "stored_path": relative_path,
        "file_type":   file_type,
        "size_bytes":  size,
    }


def delete_course_file(relative_path: str) -> bool:
    """Delete a file from the upload folder. Returns True if deleted, False if not found."""
    absolute_path = os.path.join(current_app.config["UPLOAD_FOLDER"], relative_path)
    if os.path.exists(absolute_path):
        try:
            os.remove(absolute_path)
            return True
        except OSError:
            return False
    return False
