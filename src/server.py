from flask import Flask, jsonify, request, send_from_directory, render_template
from flask_sqlalchemy import SQLAlchemy
from redis import Redis
from models import db, User, Ad
import os
import random

app = Flask(__name__)
redis = Redis(host='redis', port=6379)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://postgres:password@db:5432/advertising"
app.static_folder = '/app/src/static'
app.app_context().push()
db.init_app(app)
db.create_all()

# When user initially loads the page
@app.route('/', methods=['GET'])
def index():
    # Get a random user
    num_users = len(User.query.all())

    if num_users > 0:
        rand = random.randint(0, num_users-1)
        user = User.query.all()[rand]
    else:
        return jsonify({"Error":"users table returned 0 results."})

    if user:
        # Get an appropriate ad for user
        ad = get_ad(user)

        return render_template('index.html', user=user, ad=ad, rating=get_rating(user, ad))
    else:
        return jsonify({"Error":"error finding random user"})


# When user refreshes ad (choosing to retain user)
@app.route('/<userid>', methods=['GET'])
def retain_user_info(userid):
    # Get the user object for the given userid
    user = User.query.filter_by(user_id=userid).first()

    if user:
        # Get an appropriate ad for user
        ad = get_ad(user)

        # Set the ad as the last one the user saw, so that they will receive a different one next time.
        redis.set(str(userid), str(ad.brand).encode('utf-8'))

        return render_template('index.html', user=user, ad=ad, rating=get_rating(user, ad))
    else:
        return jsonify({"Error":"userid not found"})


# Find an appropriate ad for the given user
def get_ad(user):
    user_gender = ""
    if user.gender == "Male":
        user_gender = "M"
    else:
        user_gender = "F"

    last_ad = ""
    if redis.exists(user.user_id):
        last_ad = redis.get(user.user_id).decode('utf-8')
    
    # See if any ad meets all criteria.
    relevant_ads = Ad.query.filter((Ad.target_gender == user_gender) | (Ad.target_gender == "B")) \
        .filter((Ad.age_lower_bound <= user.age) & ((Ad.age_upper_bound >= user.age) | (Ad.age_upper_bound == 0))) \
        .filter((Ad.salary_lower_bound <= user.estimated_salary) & ((Ad.salary_upper_bound >= user.estimated_salary) | (Ad.salary_upper_bound == 0)))\
        .filter((Ad.brand != last_ad))
    if relevant_ads.count() > 1:
        return return_random(relevant_ads)

    # See if ad meets gender and age criteria (but not salary)
    relevant_ads = Ad.query.filter((Ad.target_gender == user_gender) | (Ad.target_gender == "B"))\
        .filter((Ad.age_lower_bound <= user.age) & ((Ad.age_upper_bound >= user.age) | (Ad.age_upper_bound == 0)))\
        .filter(Ad.brand != last_ad)
    if relevant_ads.count() > 0:
        return return_random(relevant_ads)

    # See if ad meets age and salary criteria (but not gender)
    relevant_ads = Ad.query.filter((Ad.age_lower_bound <= user.age) & ((Ad.age_upper_bound >= user.age) | (Ad.age_upper_bound == 0)))\
        .filter((Ad.salary_lower_bound <= user.estimated_salary) & ((Ad.salary_upper_bound >= user.estimated_salary) | (Ad.salary_upper_bound == 0)))\
        .filter(Ad.brand != last_ad)
    if relevant_ads.count() > 0:
        return return_random(relevant_ads)

    # See if ad meets salary and gender (but not age)
    relevant_ads = Ad.query.filter((Ad.target_gender == user_gender) | (Ad.target_gender == "B"))\
        .filter((Ad.salary_lower_bound <= user.estimated_salary) & ((Ad.salary_upper_bound >= user.estimated_salary) | (Ad.salary_upper_bound == 0)))\
        .filter(Ad.brand != last_ad)
    if relevant_ads.count() > 0:
        return return_random(relevant_ads)

    # Just gender
    relevant_ads = Ad.query.filter((Ad.target_gender == user_gender) | (Ad.target_gender == "B"))\
        .filter(Ad.brand != last_ad)
    if relevant_ads.count() > 0:
        return return_random(relevant_ads)
    
    # Just age
    relevant_ads = Ad.query.filter((Ad.age_lower_bound <= user.age) & ((Ad.age_upper_bound >= user.age) | (Ad.age_upper_bound == 0)))\
        .filter(Ad.brand != last_ad)
    if relevant_ads.count() > 0:
        return return_random(relevant_ads)

    # Just salary
    relevant_ads = Ad.query.filter((Ad.salary_lower_bound <= user.estimated_salary) & ((Ad.salary_upper_bound >= user.estimated_salary) | (Ad.salary_upper_bound == 0)))\
        .filter(Ad.brand != last_ad)
    if relevant_ads.count() > 0:
        return return_random(relevant_ads)
    
    # If absolutely no other ads fit any descriptor, send a random one
    ads = Ad.query.all()
    ad = return_random(ads)

    return ad

# Given a query with multiple results, return one at random.
def return_random(ads):
    rand = random.randint(0, ads.count()-1)
    return ads[rand]

# Return a rating from 0-3, on how many attributes of the user this ad fits.
def get_rating(user, ad):
    rating = 0

    # +1 for the correct gender (or if ad targets both genders)
    if user.gender == "Male" and ad.target_gender != "F":
        rating += 1
    elif user.gender == "Female" and ad.target_gender != "M":
        rating += 1
    
    # +1 if relevant age
    if user.age >= ad.age_lower_bound and (user.age <= ad.age_upper_bound or ad.age_upper_bound == 0):
        rating += 1

    # +1 if relevant salary
    if user.estimated_salary >= ad.salary_lower_bound and (user.estimated_salary <= ad.salary_upper_bound or ad.salary_upper_bound == 0):
        rating += 1

    return rating
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)