# -*- coding: utf-8 -*-
""" 
Conatains all the communication with db
Uses sqlalchemy expressive language,
but not the ORM (no declarative base)
"""

from sqlalchemy import create_engine, MetaData,  \
Table, Column, ForeignKey, \
Integer, VARCHAR, DATETIME,TEXT,BOOLEAN, \
select, insert, update, join, desc
from sqlalchemy.sql import text
from sqlalchemy.exc import ProgrammingError
from contextlib import closing
try:
    from src import app
except ImportError:
    from config import DevelopmentConfig as dev_conf
from src.hashing_ import hash_password,check_password
import logging
logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(message)s')
logger = logging.getLogger(__name__)

def connect_and_get(query,**kwargs):
    """
    Connects to db, executes query 
    """
    try:
        eng = create_engine(app.config["DATABASE"], pool_recycle=3600)
        with closing(eng.connect()) as con:
            result = con.execute(query,**kwargs)      
        return result
    except Exception as e:
        logger.error(e)
        raise e
        return False
    
def zip_results(columns, results):
    """
    Zip columns of a given table
    with a set of results obtained
    from a query.
        :columns accepts a list of column names,
        :results a list of tuples obtained by running fetchall method on cursor object
    
    returns a list of dictionary with column names as keys and rows as values
    """
    cols = [str(col).split(".")[1] for col in columns]
    return [dict(zip(cols, row)) for row in results]

class Model(object):
    def insert_(self, vals):
        """ 
        Generic method for inserting things to one table.
        Accepts a dictionary of things to insert
        """
        query = self.structure.insert().values(vals)
        result = connect_and_get(query)
        if result == False:
            return False

    def select_(self, what, columnname, var_value):
        """
        Select where 
        """
        var_value = str(var_value)
        t = self.structure
        s = select([what]).where(columnname == var_value)
        return connect_and_get(s)

class User(Model):
    """ An object contaning methods relating to db activities of users """
    metadata = MetaData()
    structure = Table("users", metadata,
                               Column("uid",Integer,primary_key=True),
                               Column("username",VARCHAR(90),index=True),
                               Column("password",TEXT),
                               Column("email",VARCHAR(100)),
                               Column("about_me",TEXT),
                               Column("points",Integer),
                               Column("date_created",DATETIME),
                               Column("oAuth", BOOLEAN))

    def get_id(self, username):
        query = select([self.structure.c.uid]). \
            where(self.structure.c.username==username)
        result = connect_and_get(query).fetchone()
        if result is not None:
            return result[0]
        return None
        
    def check_pass(self, username, plain_pass):
        """ used when user logs in """
        t = self.structure
        s = select([t.c.password]).where(t.c.username == username)        
        db_pass = connect_and_get(s).fetchone()
        if db_pass:
            if check_password(db_pass[0], plain_pass):
                return True
        return False

    def get_profile(self, uid):
        """
        Display user's profile
        """
        t = self.structure
        s = select([t.c.uid, t.c.username, t.c.email, t.c.about_me, \
                t.c.points, t.c.date_created]). \
                where(t.c.uid == uid)
        row = connect_and_get(s).fetchone()
        if row:    
            profile = dict(uid=row[0], username=row[1], email=row[2],
                           about_me=row[3], points=row[4],
                           date_created=row[5])
            return profile
        return False

    def update_profile(self, uid, **kwargs):
        """
        to_insert should be 
        username a string
        """
        #logging.debug(kwargs)
        t = self.structure
        upd = t.update().where(t.c.uid == uid).values(**kwargs)
        result = connect_and_get(upd)
        return result

class ReviewRequestModel(Model):
    metadata = MetaData()
    structure = Table("reviewRequests", metadata,
                    Column("reqId",Integer, primary_key=True),
                    Column("uid",Integer, ForeignKey(User.structure.c.uid)),
                    Column("title",VARCHAR(64)),
                    Column("content",TEXT),
                    Column("category",VARCHAR(98)),
                    Column("date_requested",DATETIME),
                    Column("deadline",VARCHAR(90)),
                    Column("articleURL",TEXT),
                    Column("rate_req",Integer))
    
    # number of articles displayed on startpage
    limes = 5

    # columns needed for typical join
    cols = [User.structure.c.username, structure.c.reqId, \
            structure.c.title, structure.c.content, \
            structure.c.category, structure.c.date_requested, \
            structure.c.deadline, structure.c.articleURL, \
            structure.c.rate_req]

    def select_user_requests(self, username):
        """
        accepts a string username
        returns a list of dictionaries
        """

        query = text("SELECT reqs.title,reqs.content,reqs.category, \
                reqs.date_requested, reqs.deadline, reqs.articleURL, reqs.rate_req \
                from reviewRequests reqs,users \
                where users.uid=reqs.uid and users.username=:username")
        result = connect_and_get(query,username=username).fetchall()
        if result:
            # we return a different set of columns, so local columns
            cols = ['reqs.title', 'reqs.content', 'reqs.category', \
            'reqs.date_requested', 'reqs.deadline', 'reqs.articleURL' \
            'reqs.rate_req']
            return zip_results(cols, result)
        return False
    
    def parse_all(self, offset=0):
        off = offset * self.limes
        user_s = User.structure
        req_s = self.structure
        query = select(self.cols).  \
            select_from(join(req_s,user_s, user_s.c.uid)). \
            order_by(desc(req_s.c.date_requested)). \
            limit(self.limes). \
            offset(off)
        result = connect_and_get(query).fetchall()
        if result:
            return zip_results(self.cols,result)
        return False

    def count_all(self):
        s = self.structure.count()
        re = connect_and_get(s)
        if re:
            return int(re.fetchone()[0]/ self.limes)
        return False

    def get_request_review(self, num):
        """
        Displays one single review request
        after the user clicks on the title when she sees it on mainpage

        accepts an int
        returns a dict 
        """
        query = select(self.cols).  \
            select_from( \
            join(self.structure, User.structure)). \
            where(self.structure.c.reqId == num)
        result = connect_and_get(query).fetchall()
        if result:
            return zip_results(self.cols,result)[0]
        return False

    def rate_req_rev(self,reqId):
        query = text('UPDATE reviewRequests \
            set rate_req = rate_req + 1 \
            where reqId=:reqId')
        result = connect_and_get(query,reqId=reqId)
        if result.rowcount != 0:
            return True
        return False

    def rate_req_rev_minus(self,reqId):
        query = text('UPDATE reviewRequests \
            set rate_req = rate_req - 1 \
            where reqId=:reqId')
        result = connect_and_get(query,reqId=reqId)
        if result.rowcount != 0:
            return True
        return False

    def update_review_request(self, num, title, content, category, deadline):
        query = self.structure.update().where(self.structure.c.reqId == num).\
            values(title=title, content=content, category=category, \
                deadline=deadline)
        result = connect_and_get(query)
        if result.rowcount != 0:
            return True
        return False

class Review(Model):
    metadata = MetaData()
    structure = Table("reviews", metadata,
                    Column("revid",Integer,primary_key=True),
                    Column("reqId",Integer, \
                        ForeignKey(ReviewRequestModel.structure.c.reqId)),
                    Column("uid",Integer,\
                        ForeignKey(User.structure.c.uid)),
                    Column("review_text",TEXT),
                    Column("rating",Integer),
                    Column("date_written",DATETIME),
                    Column("rate_review", Integer)
                    )

    def get_review(self,revid):
        query = text('SELECT u1.username as requesting,\
            req.title,rev.review_text,req.reqId, \
            rev.revid,u2.username as reviewer, \
            rev.rating, rev.rate_review, rev.date_written \
            from users u1,users u2,reviewRequests req,reviews rev \
            where rev.reqId=req.reqId and rev.uid=u2.uid \
            and req.uid=u1.uid and revid=:revid')

        result = connect_and_get(query,revid=revid)
        if result:
            cols = ["u1.requesting","req.title","rev.review_text","req.reqId", \
            "rev.revid", 'u2.reviewer',"rev.rating","rev.rate_review","rev.date_written"]
            return zip_results(cols,result.fetchall())[0]
        return False

    def get_users_reviews(self, username):
        """
        Returns all reviews written by user username.
        So for Alice this will return Alice's review of Hugo
        """
        # Ok I give up I'm going to write
        # plain sql query, it's easier

        query = text("SELECT reviewRequests.title, \
            reviews.review_text, users.username AS reviewed, \
            reviews.date_written,reviews.rating, reviews.rate_review \
            FROM reviewRequests, reviews, users \
            where reviewRequests.reqId=reviews.reqId \
            and reviewRequests.uid=users.uid \
            and reviews.uid = \
                (select uid from users where username=:username)")

        result = connect_and_get(query,username=username).fetchall()
        
        if result:
            # column names to zip with results
            cols = ['reviewRequests.title', 'reviews.review_text', 'some.reviewed', \
            'reviews.date_written','reviews.rating', 'reviews.rate_review']
            return zip_results(cols,result)
        return False
   
    def get_reviews_of_user(self, username):
        """
        This is the reverse of the function above.

        For Hugo it will return Alice's review of Hugo's article.

        """
        query = text("SELECT reqs.title, \
            revs.review_text, users.username AS reviewed, \
            revs.date_written,revs.rating, revs.rate_review \
            FROM reviewRequests reqs, reviews revs, users \
            where revs.uid=users.uid \
            and reqs.reqId=revs.reqId \
            and reqs.uid= (select uid from users \
                where username=:username)")

        result = connect_and_get(query,username=username).fetchall()
        if result:
            cols = ['reviewRequests.title', 'reviews.review_text', 'some.reviewer', \
            'reviews.date_written','reviews.rating', 'reviews.rate_review']
            return zip_results(cols, result)
        return False

    def get_best_reviews(self,offset=0,limit=10):
        """
        returns best reviews, highest rated ones
        """
        query = text('SELECT reqs.title,revs.review_text,reviewer.username \
            as reviewer, reviewed.username as reviewed,revs.date_written,revs.rate_review  \
            from reviewRequests reqs,reviews revs, users reviewer,users reviewed \
            where reqs.reqid=revs.reqid and revs.uid=reviewer.uid \
            and reqs.uid=reviewed.uid \
            order by rate_review desc, date_written limit :limit offset :offset')

        result = connect_and_get(query,limit=limit,offset=offset).fetchall()
        if result:
            cols = ['reviewRequests.title', 'reviews.review_text', 'some.reviewer', \
            'some.reviewed','reviews.date_written', 'reviews.rate_review']
            return zip_results(cols,result)
        return False

    def rate_review(self,revId):
        query = text('UPDATE reviews \
            set rate_review = rate_review + 1 \
            where revId=:revId')
        result = connect_and_get(query,revId=revId)
        if result.rowcount != 0:
            return True
        return False

    def rate_review_minus(self,revId):
        query = text('UPDATE reviews \
            set rate_review = rate_review - 1 \
            where revId=:revId')
        result = connect_and_get(query,revId=revId)
        if result.rowcount != 0:
            return True
        return False
