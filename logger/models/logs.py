from logger import db


class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    created = db.Column(db.DateTime())
    browser = db.Column(db.String())
    page_url = db.Column(db.String())
    country = db.Column(db.String())
    message = db.Column(db.String())
