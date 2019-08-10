import flask_sqlalchemy

db = flask_sqlalchemy.SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key = True)
    gender = db.Column(db.String(10))
    age = db.Column(db.Integer)
    estimated_salary = db.Column(db.Integer)

    def __repr__(self):
        return '<User {}>'.format(self.user_id)

class Ad(db.Model):
    __tablename__ = 'ads'
    brand = db.Column(db.String(15), primary_key = True)
    target_gender = db.Column(db.String(10))
    age_lower_bound = db.Column(db.Integer)
    age_upper_bound = db.Column(db.Integer)
    salary_lower_bound = db.Column(db.Integer)
    salary_upper_bound = db.Column(db.Integer)
    ad = db.Column(db.String)

    def __repr__(self):
        return '<Post {}>'.format(self.brand)