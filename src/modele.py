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
from contextlib import closing
try:
    from src import app
except ImportError:
    from config import DevelopmentConfig as dev_conf
from help_connect import ping_connection
from src.hashing_ import hash_password,check_password
import logging
logging.basicConfig(level=logging.DEBUG)

def connect_and_get(query,**kwargs):
    """
    Connects to db, executes query 
    """
    try:
        eng = create_engine(app.config["DATABASE"], pool_recycle=3600)
    except NameError as e:
        eng = create_engine(dev_conf.DATABASE)
    try:
        with closing(eng.connect()) as con:
            result = con.execute(query,**kwargs)      
        return result
    except Exception as e:
        logging.error(e)
        logging.info("query was: %s " % query)
        return False

def zip_results(columns, results):
    """
    Zip columns of a given table
    with a set of results obtained
    from a query.
        :columns accepts a list of column names,
        :results a list of tuples obtained by running fetchall method on cursor object
    
    DO NOT PASS CURSOR, PASS ONLY A LIST OBTAINED BY CURSOR.FETCHALL()
    
    returns a dictionary
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

    def check_pass(self, username, plain_pass):
        """ Or rather check password, used when user logs in """
        t = self.structure
        s = select([t.c.password]).where(t.c.username == username)        
        db_pass = connect_and_get(s).fetchone()
        if db_pass:
            if check_password(db_pass[0], plain_pass):
                return True
        return False

    def get_profile(self, username):
        """
        Display user's profile
        """
        t = self.structure
        s = select([t.c.uid, t.c.username, t.c.email, t.c.about_me, \
                t.c.points, t.c.date_created]). \
                where(t.c.username == username)
        row = connect_and_get(s).fetchone()
        if row:    
            profile = dict(uid=row[0], username=row[1], email=row[2],
                           about_me=row[3], points=row[4],
                           date_created=row[5])
            return profile
        return False

    def update_profile(self, username, **kwargs):
        """
        to_insert should be 
        username a string
        """
        #logging.debug(kwargs)
        t = self.structure
        upd = t.update().where(t.c.username == username).values(**kwargs)
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

    def select_user_requests(self, uid):
        """
        accepts an integer - user id
        returns a dictionary
        """
        query = select([self.structure]).where(self.structure.c.uid == uid)
        result = connect_and_get(query).fetchall()
        if result:
            return zip_results(self.structure.columns, result)[0]
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
            return int(re.fetchone()[0]/self.limes)
        return False

    def get_request_review(self, num):
        """
        Displays one single review request
        after the user clicks on the title
        on the homepage.

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

    def update_review_request(self, num, title, content, category, deadline):
        query = self.structure.update().where(self.structure.c.reqId == num).\
            values(title=title, content=content, category=category, \
                deadline=deadline)
        result = connect_and_get(query)
        if result.rowcount == 1:
            return True
        return False

    def get_best_requests(self, offset):
        """
        Returns best review requests
        """
        pass

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
    
    # username below is the username of someone who
    # published request review. It is not the username
    # of user who writes review
    # cols = [User.structure.c.username, ReviewRequestModel.structure.c.title, \
    #         structure.c.review_text, structure.c.rating, \
    #          structure.c.date_written, structure.c.rate_review]

    cols = ['reviewRequests.title', 'reviews.review_text', 'some.reviewed', \
            'reviews.date_written','reviews.rating', 'reviews.rate_review']
    def get_users_reviews(self, username):
        """
        Returns all reviews written by user username.
        So for Alice this will return her review of Hugo
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
            return zip_results(self.cols,result)
        return False
   
    def get_reviews_by_user(self, username):
        """
        This is the reverse of the function above
        it displays all reviews written by given user
        for admin it will return all things that this user
        had written about others
        """
        t = self.structure
        s = select([t]).where(t.c.reviewer == username)
        result = connect_and_get(s)
        if result:
            return zip_results(self.structure.columns, result)
        return False

    def get_best_reviews(self, offset):
        """
        returns best reviews, highest rated ones
        """
        query = """
        SELECT reviewRequests.title, reviews.review_text, 
        users.username as reviewed, reviews.date_written,
        reviews.rating,reviews.rate_review 
        from reviewRequests,reviews,users 
        where reviewRequests.reqId=reviews.reqId 
        and reviewRequests.uid=users.uid;
            """
        pass
