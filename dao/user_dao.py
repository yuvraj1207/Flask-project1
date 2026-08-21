from config.database import db
from models.user import User

class UserDAO:
    @staticmethod
    def create_user(username,email,password_hash,role='student'):
        user= User(username=username, email = email, password_hash= password_hash, role = role)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def get_by_username(username):
        return User.query.filter_by(username=username).first()

    @staticmethod
    def get_by_email(email):
        return User.query.filter_by(email=email).first()

    @staticmethod
    def get_all_users():
        return User.query.all()