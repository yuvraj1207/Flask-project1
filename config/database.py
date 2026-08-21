from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):

    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:yuvraj@localhost/lms_db"
    app.config["SQL_ALCHEMY_TRACK_MODIFICATION"] = False

    db.init_app(app)