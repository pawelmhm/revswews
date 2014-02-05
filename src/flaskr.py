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
    loginForm = Login(request.form)
    return render_template("starter.html",loginForm=loginForm)

@app.route('/home/<n>', methods=["POST",'GET'])
def startpage(**kwargs):
    """Displays the default startpage with login or register forms"""
    reviewRequest = ReviewRequestModel()
    allRequests = reviewRequest.parse_all(offset=int(kwargs['n']))
    numOfPages = [i for i in xrange(int(math.ceil(reviewRequest.count_all())))]
    loginForm = Login(request.form)
    if session.get('username'):
        if allRequests:
            flash("Here are all the review requests")
            return render_template('reviewRequest/all_requests.html',requests=allRequests,
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

@app.route('/login', methods=['GET'])
def login():
    loginForm = Login(request.form)
    registrationForm = Register(request.form)
    return render_template('users/register.html', loginForm=loginForm,
        registrationForm=registrationForm)

@app.route('/login', methods=["POST"])
def login_post():
    loginForm = Login(request.form)
    registrationForm = Register(request.form)
    if loginForm.validate():
        user = User()
        username = request.form['username']
        password = request.form['password']
        uid = user.get_id(username)
        if uid is not None and user.check_pass(username, password):
            return log_user_in(username, uid)
        flash('Invalid username or password','error')
    return redirect(url_for('login'))


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

@app.route('/add_user', methods=["GET", "POST"])
def add_user():
    """ This function handles the event of register form submission"""
    registrationForm = Register(request.form)
    loginForm = Login(request.form)
    if request.method == "POST" and registrationForm.validate():
        message = register_user(registrationForm.data)
        if message is None:
            flash('Hello {name}, please login here'.format(name=request.form[
                "username"]))
            return redirect(url_for('startpage',n=0))
        else:
            flash(message, 'error')
    return render_template('users/register.html', registrationForm=registrationForm,
        loginForm=loginForm)

def register_user(form_data):
    """
    Takes a form data returns error message
    that is going to be returned to user.
    """
    username = form_data['username']
    password = form_data["password"]
    user = User()
    if not is_ascii(username) or not is_ascii(password):
        return "password and username must be in ascii"
    if user.get_id(username) is not None:
        return "username taken!"

    form_data["password"] = hash_password(form_data["password"])
    form_data['points'] = 10
    form_data["date_created"] = datetime.fromtimestamp(time.time())
    form_data["about_me"] = "Who are you {user}?". \
        format(user=form_data["username"])
    form_data.pop("confirm", None)

    user.insert_(form_data)
    return None

@app.route('/login/<provider_name>/', methods=["GET", "POST"])
def oauthLogin(provider_name):
    authomatic = Authomatic(AUTHOMATIC_CONFIG, 'your secret string', report_errors=True)
    response = make_response()
    result = authomatic.login(WerkZeug(request,response),provider_name)
    if result:
        if result.user:
            result.user.update()
            appuser = dict(username = result.user.username,
                email = result.user.email,password="randomString")
            logging.debug(appuser)
            user = User()
            uid = user.get_id(appuser['username'])
            if uid is not None:
                log_user_in(appuser['username'],uid)
            else:
                # call register user
                message = register_user(appuser)
                if message is None:
                    return log_user_in(appuser['username'],uid)
                return str(message)
            # query db and see if result.user.email is there,
            # if the answer is yes, get username and all stuff for this user
            # log him in with the data from our database
            # if he is not there then add result.user.email, result.user.stuff
            # generate password for him and log him in with that
            #log_user_in(appuser.username,appuser.uid) #,True,result.user.email)
        return redirect(url_for('startpage',n=0))
    return response

def oAuthLogin_continued():
    pass

def is_ascii(s):
    """
    checks if a string is ascii
    """
    try:
        s.encode("ascii")
        return True
    except UnicodeEncodeError:
        return False

@app.route('/edit_profile',methods=["GET"])
@login_required
def edit_profile():
    form = Profile(request.form)
    profile = User().get_profile(escape(session['uid']))
    if profile:
        flash("Edit your profile %s" % escape(session['username']))
        return render_template("users/edit_profile.html", profile=profile,form=form)
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

@app.route('/request_review', methods=["GET","POST"])
@login_required
def request_review():
    uid = escape(session["uid"])
    form = ReviewRequest(request.form)
    if request.method == "POST":
        if form.validate():
            if request.files.get('file'):
                message = handle_data(request.files["file"], form.data, uid)
                if message is None:
                    flash("New review request sucessfuly added")
                    return redirect(url_for("startpage", n=0))
                else:
                    # error message from handle_upload
                    flash(message,'error')
            else:
                # no file
                flash("No file added",'error')
        else:
            # invalid form
            flash('We detected some errors in your submission. Invalid form.','error')
    flash("Request review of your article, book, or anything you'd like.")
    return render_template("reviewRequest/post_request_review.html", form=form)

def handle_data(file_, data, uid):
    if not allowed_file(file_.filename):
        return "The following formats are allowed: .doc .pdf .docx .txt"

    filename = file_.filename.replace(file_.filename.split('.',1)[0],
            uid+str(time.time()))
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    data["uid"] = uid
    data['articleURL'] = '/files/{name}'.format(name=filename)
    data['date_requested'] = datetime.fromtimestamp(time.time())
    ReviewRequestModel().insert_(data)
    file_.save(path)
    flash('file uploaded')
    return None

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

@app.route('/files/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"],filename)


@app.route('/display_user_requests/<uid>')
@login_required
def display_user_requests(uid):
    """ Displays requests for review made by given user"""
    #username = escape(session["uid"])
    rev_req = ReviewRequestModel()
    user_review_requests = rev_req.select_user_requests(uid)
    #logger.debug(user_review_requests)
    flash("Requests that you have made %s" % escape(session['username']))
    return render_template("reviewRequest/all_requests.html", requests=user_review_requests, numOfPages=[1,2])

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
        return render_template('reviewRequest/respond.html',
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


# >>>>>>>>>>>>>>>>>>>>
#       Reviews
# <<<<<<<<<<<<<<<<<<<<

@app.route('/reviews',methods=["GET"])
@login_required
def all_reviews():
    revs = Review().get_best_reviews()
    flash("All reviews written by all users")
    return render_template('review/all_reviews.html',revs=revs)

@app.route('/reviews/<revid>')
@login_required
def one_review(revid):
    rev = Review().get_review(revid)
    return render_template('review/one_review.html',rev=rev)

@app.route("/reviews_of_user/<uid>")
@login_required
def reviews_of_user(uid):
    """
    Responses to users requests.
    """
    revs = Review().get_reviews_of_user(int(uid))
    if revs:
        flash("All reviews of drafts published by %s" % 'you')
        return render_template('review/all_reviews.html',revs=revs)
    flash('no reviews here so far')
    return render_template('review/all_reviews.html')

@app.route("/reviews_by_user/<uid>")
@login_required
def reviews_by_user(uid):
    """
    Reviews written by users
    """
    revs = Review().get_reviews_by_user(int(uid))
    if revs:
        if uid == escape(session["uid"]):
            flash("Responses to your review requests")
        else:
            flash("Reviews by user: TODO")
        return render_template('review/all_reviews.html',
                revs=revs)
    flash('no reviews here so far')
    return render_template('review/all_reviews.html',revs=None)


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
