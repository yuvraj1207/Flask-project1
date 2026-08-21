import os 
import hashlib
from werkzeug.utils import secure_filename


ALLOWED_EXTENSION = {'pdf','png','jpg','jpeg','mp4'}
MAX_FILE_SIZE = 50*1024*1024    #50 Mb

class FileServices:
    @staticmethod
    def is_allowed_files(filename):
        return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSION

    @staticmethod
    def save_materail(file,upload_folder,course_id):
        if not file or file.filename == '':
            raise ValueError ("File not found!!")

        if not FileServices.is_allowed_files(file.filename):
            raise ValueError("Invalid File Extension: Allowed only PDF , IMG, VIDEO")

        file.seek(0)    # Is used to start from the beg once the file reach end of file 

        # Unique filename using SHA256 hash + original clean filename
        clean_filename = secure_filename(file.filename)
        file_hash = hashlib.sha256(file_bytes).hexdigest()[:10]
        unique_filename = f"{file_hash}_{clean_filename}"

        # Course-specific folder target: uploads/courses/<course_id>/
        course_dir = os.path.join(upload_folder, 'courses', str(course_id))
        os.makedirs(course_dir, exist_ok=True)

        full_path = os.path.join(course_dir, unique_filename)
        file.save(full_path)

        # Determine media category
        ext = clean_filename.rsplit('.', 1)[1].lower()
        if ext in {'pdf'}:
            file_type = 'PDF'
        elif ext in {'png', 'jpg', 'jpeg'}:
            file_type = 'Image'
        else:
            file_type = 'Video'

        rel_path = os.path.join('uploads', 'courses', str(course_id), unique_filename)
        return clean_filename, rel_path, file_type, file_size