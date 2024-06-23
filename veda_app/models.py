from veda_app import db

class YourModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    column1 = db.Column(db.String(128))
    column2 = db.Column(db.String(128))
