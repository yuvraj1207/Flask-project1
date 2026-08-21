from flask import Flask
from config.database import init_db,db

app = Flask(__name__)

init_db(app)

@app.route("/")

def home():
    return "Connected to LMS Database!!"

if __name__ =="__main__":
    with app.app.context():
        db.create_all()
    app.run(debug=True)