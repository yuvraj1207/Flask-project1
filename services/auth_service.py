import datetime
import jwt
from flask import current_app
from werkzeug.security import generate_password_hash

from dao.user_dao import UserDAO, DAOError

VALID_ROLES = {"student", "instructor", "admin"}


class AuthError(Exception):
    """Raised for all authentication / authorisation failures."""


class AuthService:

    @staticmethod
    def register(name: str, email: str, password: str, role: str = "student"):
        """Validate inputs, ensure no duplicate email, then persist a new user."""
        if not name or not name.strip():
            raise AuthError("Name is required.")
        if not email or not email.strip():
            raise AuthError("Email is required.")
        if not password:
            raise AuthError("Password is required.")
        if len(password) < 6:
            raise AuthError("Password must be at least 6 characters.")
        if role not in VALID_ROLES:
            raise AuthError(f"Invalid role '{role}'. Choose from: {', '.join(sorted(VALID_ROLES))}.")

        try:
            existing = UserDAO.get_by_email(email.strip().lower())
        except DAOError as exc:
            raise AuthError(f"Database error during registration: {exc}") from exc

        if existing:
            raise AuthError("An account with this email already exists.")

        try:
            user = UserDAO.create(
                name=name.strip(),
                email=email.strip().lower(),
                password_hash=generate_password_hash(password),
                role=role,
            )
        except DAOError as exc:
            raise AuthError(f"Could not save new user: {exc}") from exc

        return user

    @staticmethod
    def authenticate(email: str, password: str):

        if not email or not password:
            raise AuthError("Email and password are required.")

        try:
            user = UserDAO.get_by_email(email.strip().lower())
        except DAOError as exc:
            raise AuthError(f"Database error during authentication: {exc}") from exc

        if not user or not user.check_password(password):
            raise AuthError("Invalid email or password.")

        return user

    @staticmethod
    def generate_jwt(user) -> str:
        """Encode a signed JWT containing user_id and role."""
        try:
            payload = {
                "user_id": user.id,
                "role":    user.role,
                "exp":     datetime.datetime.utcnow() + current_app.config["JWT_ACCESS_TOKEN_EXPIRES"],
                "iat":     datetime.datetime.utcnow(),
            }
            return jwt.encode(payload, current_app.config["JWT_SECRET_KEY"], algorithm="HS256")
        except Exception as exc:
            raise AuthError(f"Could not generate token: {exc}") from exc

    @staticmethod
    def decode_jwt(token: str) -> dict:
        """Decode and verify a JWT. Raises AuthError on failure."""
        try:
            return jwt.decode(token, current_app.config["JWT_SECRET_KEY"], algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise AuthError("Token has expired. Please log in again.")
        except jwt.InvalidTokenError as exc:
            raise AuthError(f"Invalid token: {exc}") from exc
