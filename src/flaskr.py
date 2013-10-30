# -*- coding: utf-8 -*-
import time
import string
import os
import logging
import math
import json
from functools import wraps
from datetime import datetime
from contextlib import closing

from authomatic.providers import oauth2, oauth1
from authomatic.adapters import WerkzeugAdapter as WerkZeug
from authomatic import Authomatic
from flask import Flask,request,session,g,redirect,url_for,abort,\
render_template,flash,escape,make_response, send_from_directory,\
jsonify, render_template_string, send_file
from werkzeug import secure_filename

from authConf import AUTHOMATIC_CONFIG
from hashing_ import check_password,hash_password
from forms import ReviewThis,Register,Login,ReviewRequest,Profile
from modele import ReviewRequestModel, Review, User
from src import app

logging.basicConfig(level=logging.DEBUG) 
logger = logging.getLogger(__name__)

# >>>>>>>>>>>>>>>>>>>>>>>>>
#          Main Page
# <<<<<<<<<<<<<<<<<<<<<<<<<

@app.route('/')
def hello():
    return redirect(url_for('startpage',n=0))

@app.route('/home/<n>', methods=["POST",'GET'])
def startpage(**kwargs):
    """Displays the default startpage with login or register forms"""
    reviewRequest = ReviewRequestModel()
    allRequests = reviewRequest.parse_all(int(kwargs['n']))
    numOfPages = [i for i in xrange(int(math.ceil(reviewRequest.count_all())))]
    loginForm = Login(request.form)
    if session.get('username'):
        if allRequests:
            flash("Here are all the review requests")
            return render_template ('main_page.html',reviews=allRequests, \
                loginForm=loginForm, numOfPages=numOfPages)
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
    return redirect(url_for('startpage',n=0))

@app.route("/error")
def error():
     return render_template('Errorpage.html')

@app.route('/login', methods=['GET','POST'])
def login():
    loginForm = Login(request.form)
    if request.method == 'POST' and loginForm.validate():
        user = User()
        username = request.form['username']
        password = request.form['password']
        uid = user.get_id(username)
        if uid is not None and user.check_pass(username, password):
            return log_user_in(username, uid)        
        flash('Invalid username or password','error')
    return render_template('register.html', loginForm=loginForm,registrationForm=False)

def log_user_in(username, uid):
    # to do sessions
    session['username'] = username
    session["uid"] = uid
    flash("Logged in as %s " % username)
    return redirect(url_for('startpage',n=0))

@app.route('/logout')
def logout():
    """Need to work on that"""
    session.pop('username', None)
    return redirect(url_for('startpage',n=0))

@app.route('/login/<provider_name>/', methods=["GET", "POST"])
def oauthLogin(provider_name):
    authomatic = Authomatic(AUTHOMATIC_CONFIG, 'your secret string', report_errors=True)
    response = make_response()
    result = authomatic.login(WerkZeug(request,response),provider_name)
    if result:
        if result.user:
            result.user.update()
            log_user_in(result.user.name,True,result.user.email)
        return redirect(url_for('startpage',n=0))
    return response

def oAuthLogin_continued():
    pass

    # user = User()
    # userDb = user.inDb(username)
    # if userDb:
    #     session['username'] = username

    # else:
    #     timestamp = datetime.fromtimestamp(time.time())
    #     query = user.insert_(dict(username=username,email=email,about_me="hello world",
    #                           points=10,date_created=timestamp,oAuth=1))
    #     session['username'] = username


@app.route('/add_user', methods=['POST', "GET"])
def add_user():
    """ This function handles the event of register form submission"""
    registrationForm = Register(request.form)
    loginForm = Login(request.form)
    if request.method == "POST" and registrationForm.validate():
        user = User()
        username = request.form["newUsername"].encode('utf-8').decode('ascii','ignore')
        if not user.inDb(username):
            timestamp = datetime.fromtimestamp(time.time())
            newPass  = request.form["newPassword"]
        try:
                if not checkStr(newPass):
                #check if string is ascii,
                #hmac has some difficulty with hashing unicode
                    flash("We can only tolerate ascii")
                    return redirect(url_for('startpage',n=0))
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
                return redirect(url_for('startpage',n=0))
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

@app.route('/edit_profile',methods=["GET"])
@login_required
def edit_profile():
    form = Profile(request.form)
    profile = User().get_profile(escape(session['uid']))
    if profile:
        flash("Edit your profile %s" % escape(session['username']))
        return render_template("edit_profile.html", profile=profile,form=form)    
    return render_template("Errorpage.html")

@app.route('/edit_profile',methods=["POST"])
@login_required
def edit_profile_post():
    form = Profile(request.form)
    if form.validate():
        User().update_profile(escape(session["uid"]), **form.data)
        flash('Your profile has been updated')
        return redirect(url_for('startpage',n=0))
    return redirect(url_for('edit_profile'))


# >>>>>>>>>>>>>>>>>>>>>>
# Review requests
# <<<<<<<<<<<<<<<<<<<<<<

@app.route('/request_review', methods=["GET"])
def request_review():
    form = ReviewRequest(request.form)
    flash("Request review of your article, book, or anything you'd like.")
    return render_template("post_request_review.html", form=form)

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
            return redirect(url_for("startpage",n=0))
            # except:
            #     flash('For security reasons the file can be only in .doc .pdf or .txt formats. \
            #           It cannot be bigger then 1 megabyte','error')

    flash('We detected some errors in your submission','error')
    return redirect(url_for('request_review'))

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

# >>>>>>>>>>>>>>>>>>>>
#       Reviews
# <<<<<<<<<<<<<<<<<<<<

@app.route("/req/<reqId>", methods=["GET"])
@login_required
def respond_for_review(reqId):
    """
    Displays one single review request
    redirects to template which contains form for review
    """
    login_form = Login(request.form)
    form = ReviewThis(request.form)
    rev_req_form= ReviewRequest(request.form)
    item = ReviewRequestModel().get_request_review(reqId)
    if item:
        return render_template('respond_for_review.html',
            item=item, form=form,
            login_form=login_form, revReq=rev_req_form)
    return render_template("Errorpage.html")

@app.route("/req/post/<reqId>", methods=["POST"])
@login_required
def post_response(reqId):
    rev = ReviewThis(request.form)

    if rev.validate():
        form_data = rev.data
        form_data["reqId"] = int(reqId)
        form_data["date_written"] = datetime.fromtimestamp(time.time())
        form_data["uid"] = int(escape(session["uid"]))
        Review().insert_(form_data)
        flash("Your review has been added")
        return redirect(url_for('startpage', n=0))

    flash('We detected some errors in your submission.','error')
    return redirect(url_for('respond_for_review', reqId=reqId))

@app.route("/req/update/<reqId>", methods=["POST"])
@login_required
def update_review_request(reqId):
    """
    Updates a review request by given user
    if the user is allowed to update.
        
        :reqId = id of article to update
    
    """
    req = ReviewRequestModel().get_request_review(reqId)
    form = ReviewRequest(request.form)
    if req and req["username"] == session.get('username'):  
        if form.validate(): 
            ReviewRequestModel().insert_(form.data)
            # TODO not a string but response
            return "ok"
            #return redirect(url_for('respond_for_review',reqId=reqId))
    #logger.debug(form.errors)
    # TODO should return 404 and not form invalid 
    return "form invalid %s " % form.errors
     
@app.route("/display_user_reviews")
@login_required
def display_user_reviews():
    username = escape(session["username"])
    review = Review()
    my_reviews = review.get_reviews_of_user(username)
    flash("All reviews written by you %s" % username)
    return render_template("show_my_reviews.html", my_reviews = my_reviews ) 

@app.route("/responses")
@login_required
def display_responses():
    """ Displays responses to my review request"""
    username = escape(session["username"])
    review = Review()
    responses_to_my_request = review.get_users_reviews(username)
    if responses_to_my_request:
        flash("Responses to your review requests %s" % username)
        return render_template("response_to_my_request.html", responses = responses_to_my_request)
    return render_template("response_to_my_request.html",responses = None )


# >>>>>>>>>>>>>>>>>>>>>>>>>>>
#              AJAX
# <<<<<<<<<<<<<<<<<<<<<<<<<<<

@app.route('/ajax/test.json',methods=['POST', 'GET'])
def startpageAjax():
    reviewRequest = ReviewRequestModel()
    allRequests = reviewRequest.parse_all()
    dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime)  \
        or isinstance(obj, datetime.date) else None
    if allRequests:
        return json.dumps(allRequests, default=dthandler)
    return False

@app.route('/usernameCheck',methods=["POST"])
def checkUsername():
    user = User()
    username = request.form["what"]
    if user.inDb(username):
        return json.dumps(True)
    return json.dumps(False)
