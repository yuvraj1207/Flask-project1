from sqlalchemy.exc import SQLAlchemyError
from models import db
from models.material import Material
from dao.user_dao import DAOError


class MaterialDAO:

    @staticmethod
    def create(
        course_id: int,
        module_id: int,
        filename: str,
        stored_path: str,
        file_type: str,
        size_bytes: int,
    ) -> Material:
        try:
            material = Material(
                course_id=course_id,
                module_id=module_id,
                filename=filename,
                stored_path=stored_path,
                file_type=file_type,
                size_bytes=size_bytes,
            )
            db.session.add(material)
            db.session.commit()
            return material
        except SQLAlchemyError as exc:
            db.session.rollback()
            raise DAOError(f"Failed to create material: {exc}") from exc

    @staticmethod
    def get(material_id: int):
        try:
            return db.session.get(Material, material_id)
        except SQLAlchemyError as exc:
            raise DAOError(f"Failed to fetch material: {exc}") from exc

    @staticmethod
    def get_for_course(course_id: int):
        try:
            return Material.query.filter_by(course_id=course_id).all()
        except SQLAlchemyError as exc:
            raise DAOError(f"Failed to list materials for course: {exc}") from exc

    @staticmethod
    def get_for_module(module_id: int):
        try:
            return Material.query.filter_by(module_id=module_id).all()
        except SQLAlchemyError as exc:
            raise DAOError(f"Failed to list materials for module: {exc}") from exc

    @staticmethod
    def delete(material: Material) -> None:
        try:
            db.session.delete(material)
            db.session.commit()
        except SQLAlchemyError as exc:
            db.session.rollback()
            raise DAOError(f"Failed to delete material: {exc}") from exc
