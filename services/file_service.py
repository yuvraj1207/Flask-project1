from dao.material_dao import MaterialDAO
from dao.course_dao import CourseDAO
from dao.user_dao import DAOError
from utils.file_uploader import save_course_file, delete_course_file, FileValidationError


class FileServiceError(Exception):
    """Raised for all file / material business-logic failures."""


class FileService:

    @staticmethod
    def upload_material(file_storage, course_id: int, module_id: int, uploader):
        """
        Validate, store and persist a course material.
        Raises FileServiceError on any problem.
        """
        if uploader.role not in ("instructor", "admin"):
            raise FileServiceError("Only instructors or admins can upload course materials.")

        try:
            course = CourseDAO.get_course(course_id)
        except DAOError as exc:
            raise FileServiceError(str(exc)) from exc

        if not course:
            raise FileServiceError("Course not found.")

        if uploader.role == "instructor" and course.instructor_id != uploader.id:
            raise FileServiceError("You may only upload materials to your own courses.")

        try:
            module = CourseDAO.get_module(module_id)
        except DAOError as exc:
            raise FileServiceError(str(exc)) from exc

        if not module or module.course_id != course_id:
            raise FileServiceError("Module not found for this course.")

        try:
            info = save_course_file(file_storage, course_id, module_id)
        except FileValidationError as exc:
            raise FileServiceError(str(exc)) from exc

        try:
            return MaterialDAO.create(
                course_id=course_id,
                module_id=module_id,
                filename=info["filename"],
                stored_path=info["stored_path"],
                file_type=info["file_type"],
                size_bytes=info["size_bytes"],
            )
        except DAOError as exc:
            # Roll back the saved file if DB insert fails
            delete_course_file(info["stored_path"])
            raise FileServiceError(str(exc)) from exc

    @staticmethod
    def get_material(material_id: int):
        try:
            material = MaterialDAO.get(material_id)
        except DAOError as exc:
            raise FileServiceError(str(exc)) from exc
        if not material:
            raise FileServiceError("Material not found.")
        return material

    @staticmethod
    def list_materials_for_course(course_id: int):
        try:
            return MaterialDAO.get_for_course(course_id)
        except DAOError as exc:
            raise FileServiceError(str(exc)) from exc

    @staticmethod
    def list_materials_for_module(module_id: int):
        try:
            return MaterialDAO.get_for_module(module_id)
        except DAOError as exc:
            raise FileServiceError(str(exc)) from exc

    @staticmethod
    def delete_material(material_id: int, requester) -> None:
        material = FileService.get_material(material_id)

        try:
            course = CourseDAO.get_course(material.course_id)
        except DAOError as exc:
            raise FileServiceError(str(exc)) from exc

        if requester.role == "instructor" and course.instructor_id != requester.id:
            raise FileServiceError("You may only delete materials from your own courses.")

        delete_course_file(material.stored_path)

        try:
            MaterialDAO.delete(material)
        except DAOError as exc:
            raise FileServiceError(str(exc)) from exc
