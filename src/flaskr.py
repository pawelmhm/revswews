# -*- coding: utf-8 -*-
from flask import Flask,request,session,g,redirect,url_for,abort,render_template,flash,escape,make_response, send_from_directory,jsonify
from contextlib import closing
import time
from datetime import datetime
from forms import ReviewThis,Register,Login,ReviewRequest,Profile
from modele import ReviewRequestModel, ReviewX, User_
from src import app
import json
from authomatic.providers import oauth2, oauth1
from authomatic.adapters import WerkzeugAdapter as WerkZeug
from authomatic import Authomatic
from authConf import AUTHOMATIC_CONFIG
from functools import wraps
from hashing_ import check_password,hash_password
import string
from sqlalchemy import create_engine
from werkzeug import secure_filename
import os

# >>>>>>>>>>>>>>>>>>>>>>>>>
#          Main Page
# <<<<<<<<<<<<<<<<<<<<<<<<<

@app.route('/', methods=["POST",'GET'])
def startpage():
    """Displays the default startpage with login or register forms"""
    reviewRequest = ReviewRequestModel()
    allRequests = reviewRequest.parse_all()
    loginForm = Login(request.form)
    if session.get('username'):
        if allRequests:
            flash("Here are all the review requests")
            return render_template ('main_page.html',reviews=allRequests,loginForm=loginForm)
        return render_template('Errorpage.html')
    return render_template("starter.html",loginForm=loginForm)

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#        USER  (login,log out)
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

def login_required(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        if session:
            if session.get("username"):
                return func(*args,**kwargs)
            else:
                return unauthorized(*args,**kwargs)
        else:
            return unauthorized(*args,**kwargs)
    return wrapped

def logged_in():
    if session:
        if "username" in session:
            return True
    return False

def unauthorized(*args,**kwargs):
    flash("You are not authorized to view this page, please register first")
    return redirect(url_for('startpage'))

@app.route("/error")
def error():
     return render_template('Errorpage.html')

@app.route('/add_user', methods=['POST', "GET"])
def add_user():
    """ This function handles the event of register form submission"""
    registrationForm = Register(request.form)
    loginForm = Login(request.form)
    if request.method == "POST" and registrationForm.validate():
        user = User_()
        username = request.form["newUsername"].encode('utf-8').decode('ascii','ignore')
        if not user.inDb(username):
            timestamp = datetime.fromtimestamp(time.time())
            newPass  = request.form["newPassword"]
	    try:
                if not checkStr(newPass):
                #check if string is ascii,
                #hmac has some difficulty with hashing unicode
                    flash("We can only tolerate ascii")
                    return redirect(url_for('startpage'))
            #now we know it's ascii let's make it formally ascii
            # default encoding for the rest is unicode
                newPass = newPass.encode('ascii','ignore')
                password = hash_password(newPass)
                to_insert = dict(username = username,
                    password = password,
                    email = registrationForm.email.data,
                    about_me = "Tell us something about you",
                    points=10,
                    date_created=timestamp,
                    oAuth=0)
                user.insert_(to_insert)
                flash('Hello {name}, please login here'.format(name=username))
                return redirect(url_for('startpage'))
	    except:
                return render_template("Errorpage.html")
        else:
            flash("username taken!",'error')
            return render_template('register.html', registrationForm=registrationForm, loginForm=loginForm)

    return render_template('register.html', registrationForm=registrationForm, loginForm=loginForm)

def checkStr(s):
    for i in s:
        if i not in string.ascii_letters and i not in string.digits and i not in string.punctuation and i != " ":
            return False
    return True

@app.route('/login', methods=['GET','POST'])
def login():
    loginForm = Login(request.form)
    if request.method == 'POST' and loginForm.validate():
        user = User_()
        username = request.form['username']
        password = str(request.form['password'])
        dbPass = user.getPass(username)
        if dbPass:
            if check_password(dbPass["password"],password):
                return log_user_in(request.form['username'],False,'')
            else:
                flash('Invalid username or password','error')
        else:
            flash("We don't have you in our database",'error')
    flash('We detected some errors in your submission','error')
    return render_template('register.html', loginForm=loginForm,registrationForm=False)


@app.route('/login/<provider_name>/', methods=["GET", "POST"])
def oauthLogin(provider_name):
    authomatic = Authomatic(AUTHOMATIC_CONFIG, 'your secret string', report_errors=True)
    response = make_response()
    result = authomatic.login(WerkZeug(request,response),provider_name)
    if result:
        if result.user:
            result.user.update()
            log_user_in(result.user.name,True,result.user.email)
        return redirect(url_for('startpage'))
    return response#response

def log_user_in(username,oAuth,email):
    if not oAuth:
        session['username'] = username
        flash("Logged in as %s " % username)
    else:
        user = User_()
        userDb = user.inDb(username)
        if userDb:
            session['username'] = username

        else:
            timestamp = datetime.fromtimestamp(time.time())
            query = user.insert_(dict(username=username,email=email,about_me="hello world",
                              points=10,date_created=timestamp,oAuth=1))

            session['username'] = username
    return redirect(url_for('startpage'))

@app.route('/logout')
def logout():
    """Need to work on that"""
    session.pop('username', None)
    return redirect(url_for('startpage'))

# >>>>>>>>>>>>>>>>>>>>>>
#      USER  (profile)
# <<<<<<<<<<<<<<<<<<<<<<

@app.route('/edit_profile',methods=["GET","POST"])
@login_required
def edit_profile():
    userX = User_()
    username = escape(session["username"])
    form = Profile(request.form)
    if request.method == "POST" and form.validate():
        to_insert = dict(email=request.form['email'],about_me = request.form['about_me'])
        userX.update_profile(username,to_insert)
        flash('Your profile has been updated')
        return redirect(url_for('startpage'))
    else:
        profile = userX.get_profile(username)
        if profile:
            flash("Edit your profile %s" % username )
            return render_template("edit_profile.html", profile=profile,form=form)
        
        return render_template("Errorpage.html")


# >>>>>>>>>>>>>>>>>>>>>>
# Review requests
# <<<<<<<<<<<<<<<<<<<<<<

@app.route('/request_review', methods=["GET"])
def request_review():
    form = ReviewRequest(request.form)
    flash("Request review of your article, book, or anything you'd like.")
    return render_template("request_review.html", form=form)

@app.route('/post_request_review', methods=["POST"])
@login_required
def post_request_review():
    """ TO DO this is ugly please rework ME"""
    username = escape(session["username"])
    form = ReviewRequest(request.form)
    if request.method == "POST" and form.validate():
        f = request.files['file']
        if f and allowed_file(f.filename):
            timestamp = datetime.fromtimestamp(time.time())
            filename = f.filename.replace(f.filename.split('.',1)[0],username+str(time.time())) #add username to filename
            fileURL = '/files/{name}'.format(name=filename)
            #try:
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
            
            f.save(path)
            flash('File uploaded')

            to_insert = dict(title = request.form['title'],
                content = request.form['content'],
                category = request.form['category'],
                date_requested = timestamp,
                deadline = request.form['deadline'],
                username=username,
                articleURL = fileURL)

            review_ = ReviewRequestModel()
            review_.insert_(to_insert)
            flash("New review request sucessfuly added")
            return redirect(url_for("startpage"))
            # except:
            #     flash('For security reasons the file can be only in .doc .pdf or .txt formats. \
            #           It cannot be bigger then 1 megabyte','error')

    flash('We detected some errors in your submission','error')
    return render_template("request_review.html", form=form)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

@app.route('/files/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"],filename)


@app.route('/display_user_requests')
@login_required
def display_user_requests():
    """ Displays requests for review made by given user"""
    username = escape(session["username"])
    model_ = ReviewRequestModel()
    user_review_requests = model_.select_user_requests(username)
    flash("Requests that you have made %s" % username)
    return render_template("display_user_requests.html", reviews=user_review_requests)

@app.route('/edit_requests', methods=["POST"])
@login_required
def edit_requests():
    if request.method == "POST":
        reviewRequest = ReviewRequestModel()
        reviewRequest.update_item()
        return True        

# >>>>>>>>>>>>>>>>>>>>
#       Reviews
# <<<<<<<<<<<<<<<<<<<<

@app.route("/req/<num>", methods=["GET", "POST"])
@login_required
def respond_for_review(num):
    """ Displays one single review request
    redirects to template which contains form for review
    this form posts to review_this function below"""
    loginForm = Login(request.form)
    form = ReviewThis(request.form)
    if request.method == 'POST':
        if form.validate() and not session.get("username")==None:
            username = escape(session["username"])
            timestamp = datetime.fromtimestamp(time.time())
            to_insert = dict(title=request.form['title'],
                             review=request.form['content'],
                             rating=request.form['rating'],
                             date_written=timestamp,
                             reviewer=username,
                             reviewed=request.form['reviewed'],
                             request_id=request.form['request_id'])
            review_re = ReviewX()
            #logging.info(review_re,type(review_re),review,dir(review_re))
            result = review_re.insert_(to_insert)
            flash("Your review has been added")
            return redirect(url_for('startpage'))
        else:
            flash('We detected some errors in your submission.','error')
    reviewRequest = ReviewRequestModel()
    singleReviewRequest = reviewRequest.get_request_review(num)
    if singleReviewRequest and form and loginForm:
        return render_template('together.html',item = singleReviewRequest, form=form,loginForm=loginForm)
    return render_template("Errorpage.html")

@app.route("/display_user_reviews")
@login_required
def display_user_reviews():
    username = escape(session["username"])
    review = ReviewX()
    my_reviews = review.get_reviews_by_user(username)
    flash("All reviews written by you %s" % username)
    return render_template("show_my_reviews.html", my_reviews = my_reviews )
    #return render_template("Errorpage.html")    

@app.route("/responses")
@login_required
def display_responses():
    """ Displays responses to my review request"""
    username = escape(session["username"])
    review = ReviewX()
    responses_to_my_request = review.get_reviews_of_user(username)
    
    if responses_to_my_request:
        flash("Responses to your review requests %s" % username)
        return render_template("response_to_my_request.html", responses = responses_to_my_request)
    else:
        return render_template("response_to_my_request.html",responses = None )


# >>>>>>>>>>>>>>>>>>>>>>>>>>>
#              AJAX
# <<<<<<<<<<<<<<<<<<<<<<<<<<<

@app.route('/ajax/test.json',methods=['POST', 'GET'])
def startpageAjax():
    reviews = get_all_review_requests()
    return json.dumps(reviews)

@app.route('/ajax2/test.json',methods=['POST', 'GET'])
def ajaxRevisited():
    #reviews = get_all_review_requests()
    content = request.json
    contentMaybe = request.data
    headers = request.headers
    method = request.method
    stream = request.stream
    #cont  = json.loads(content)
    #hope = json.loads(request.data)
    if request.form['what'] == 'newItems':
        return json.dumps(True)
    else:
        return "no!"
    return "ok"

@app.route('/newStart')
def newStart():
    form = Register(request.form)
    return render_template('newAjax.html',registrationForm=form)

@app.route('/usernameCheck',methods=["POST"])
def checkUsername():
    user = User_()
    if request.method == "POST":
        username = request.form["what"]#json.loads(request.form["who"])
        #usern = json.loads(username)
        if user.inDb(username):
            return json.dumps(True)
        else:
            return json.dumps(False)

def init_db():
    review = ReviewX()
    user = User_()
    reviewRequest = ReviewRequestModel()
    eng = create_engine(app.config["DATABASE"])
    with closing(eng.connect()) as con:
        user.structure.create(eng)
        reviewRequest.structure.create(eng)
        review.structure.create(eng)

def remove_db():
    review = ReviewX()
    user = User_()
    reviewRequest = ReviewRequestModel()
    eng = create_engine(app.config["DATABASE"])
    with closing(eng.connect()) as con:
        user.structure.drop(eng, checkfirst=True)
        reviewRequest.structure.drop(eng,checkfirst=True)
        review.structure.drop(eng,checkfirst=True)

def populateDb():
    from populateDb import addUsers, addRequests, addReviews
    addUsers()
    addRequests()
    addReviews()
