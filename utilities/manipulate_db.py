"""
Creates a group of fictional users, fictional manuscripts and fictional reviews.
Used mainly for testing purposes. None of those usernames
will be stored in production. 
"""

from src.modele import  Review, User, ReviewRequestModel, create_engine
from src.config import DevelopmentConfig as dev_conf
from src.hashing_ import hash_password
from datetime import datetime, timedelta
from random import choice
import time
from contextlib import closing
from sqlalchemy import select
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def addUsers():
    user = User()
    usersNames = ["Hugo","Alice","Bob","Mary","Don","Jake","admin","pawelmmh"]
    passwords = ["secret","verysecret","lovely","mistaken","delta","bobby","default","diogenes"]
    about_me = ["I love cats","love dogs","explorer of new lands", "web designer",
                "sex in the city is my favorite series","phd in philosophy ","admin of this place","lover of wisdom"]
    email = ["sssss@o2.pl","rolaaa@pla.ll","dolta@90.pl","klasao@commma.com","dola@me.pl","hello@o2.pl","admin@admin.ad","delta@o2.pl"]

    date_created = datetime.fromtimestamp(time.time())
    for i in range(len(usersNames)):
        hashed = hash_password(passwords[i])
        newDict = dict(username=usersNames[i],password=hashed,email=email[i],about_me=about_me[i],points=20,date_created=date_created,oAuth=0)
        user.insert_(newDict)

def addRequests():
    request = ReviewRequestModel()
    titles = ["Faith and free market","abook on love","review of manuscript","essay on desire","chapter on sex"]
    contents = ["I need a review of a fragment of my article on faith","I need a brief recommendations concerning my book on love",
                "I'm writing a book on the life of aristocracy in Paris in XVIII century, any careful reader will be appreciated","this is on desire, please read it",
                "no problem with finding a review right? a book on sex"]
    timestamp = datetime.fromtimestamp(time.time())
    deadlines = [str(datetime.fromtimestamp(time.time()) + timedelta(i)) for i in range(5)]
    userIds = [x for x in range(1,len(titles)+1)]
    reqIds = [j for j in xrange(101,101+len(titles)+1)]
    for i in range(len(titles)):
        user = User()
        #getId = user.select_(user.structure.c.id,user.structure.c.username,userNames[i])
        #idN = getId.fetchone()[0]
        req = dict(reqId=reqIds[i],uid=userIds[i],
                    title=titles[i], content=contents[i],
                    category="academic", date_requested=timestamp,
                    deadline=deadlines[i], rate_req=0
        )
        query = request.insert_(req)
    #logging.info("requests added %s" % query)


def addReviews():
    reviewModel = Review()
    reviews = ["Well how do I begin I loved the introduction",
               "Ok this was not such a bad reading but you could improe grammar",
               "Hmm, why are you interested in this topic, can't see passion here",
               "Nice one, I want more!"]
    
    dates  = [datetime.fromtimestamp(time.time()) + timedelta(choice([10])) for i in range(5)]
    request = ReviewRequestModel()
    userIds = [x for x in range(2,len(reviews)+2)]
    reqIds = [j for j in xrange(101,101+len(reviews)+1)]
    revIds = [k for k in xrange(201,201+len(reviews)+1)]
    t = request.structure
    for i in range(len(reviews)):
        review = dict(revid=revIds[i],reqId=reqIds[i],uid=userIds[i],
                    review_text=reviews[i],rating=5,
                    date_written=dates[i],rate_review=1)
        res = reviewModel.insert_(review)
     #   logging.debug("review %s inserted" % str(revIds[i]))
    #logging.debug("Done")

def init_db(db_params):
    review = Review()
    user = User()
    reviewRequest = ReviewRequestModel()
    eng = create_engine(db_params)
    #logging.debug("eng created with db  %s" % dev_conf.DATABASE)
    with closing(eng.connect()) as con:
        user.structure.create(eng)
        #logging.debug("user table created")
        reviewRequest.structure.create(eng)
        #logging.debug("review requests table created")
        review.structure.create(eng)
        #logging.debug("review table created. Done")

def remove_db(db_params):
    review = Review()
    user = User()
    reviewRequest = ReviewRequestModel()
    eng = create_engine(db_params)
    with closing(eng.connect()) as con:
        review.structure.drop(eng,checkfirst=True)
        reviewRequest.structure.drop(eng,checkfirst=True)
        user.structure.drop(eng, checkfirst=True)
    logger.debug("database %s removed" % db_params.split('/')[-1].upper())


def populateDb(db_params):
    remove_db(db_params)
    init_db(db_params)
    addUsers()
    addRequests()
    addReviews()
    logger.debug("database %s populated" % db_params.split('/')[-1].upper())

#remove_db()
#init_db()
#addUsers()
#addRequests()
#addReviews()
#u = modele.User_()
#u.structure.create(eng)
#rev = modele.ReviewRequestModel()
#rev.structure.create(eng)
#descri = con.execute('describe users')
#review = modele.Review()
#review.structure.create(eng)
#populateDb()

