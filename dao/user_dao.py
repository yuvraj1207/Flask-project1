from sqlalchemy.exc import SQLAlchemyError
from models import db
from models.user import User


class DAOError(Exception):
    """Raised when a low-level database operation fails."""


class UserDAO:

    @staticmethod
    def create(name: str, email: str, password_hash: str, role: str = "student") -> User:
        try:
            user = User(name=name, email=email, password_hash=password_hash, role=role)
            db.session.add(user)
            db.session.commit()
            return user
        except SQLAlchemyError as exc:
            db.session.rollback()
            raise DAOError(f"Failed to create user: {exc}") from exc

    @staticmethod
    def get_by_id(user_id: int):
        try:
            return db.session.get(User, user_id)
        except SQLAlchemyError as exc:
            raise DAOError(f"Failed to fetch user by id: {exc}") from exc

    @staticmethod
    def get_by_email(email: str):
        try:
            return User.query.filter_by(email=email).first()
        except SQLAlchemyError as exc:
            raise DAOError(f"Failed to fetch user by email: {exc}") from exc

    @staticmethod
    def get_all(role: str = None):
        try:
            query = User.query
            if role:
                query = query.filter_by(role=role)
            return query.order_by(User.id).all()
        except SQLAlchemyError as exc:
            raise DAOError(f"Failed to list users: {exc}") from exc

    @staticmethod
    def update(user: User) -> User:
        try:
            db.session.commit()
            return user
        except SQLAlchemyError as exc:
            db.session.rollback()
            raise DAOError(f"Failed to update user: {exc}") from exc

    @staticmethod
    def delete(user: User) -> None:
        try:
            db.session.delete(user)
            db.session.commit()
        except SQLAlchemyError as exc:
            db.session.rollback()
            raise DAOError(f"Failed to delete user: {exc}") from exc
