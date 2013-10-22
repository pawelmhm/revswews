# -*- coding: utf-8 -*-
from sqlalchemy import create_engine,MetaData,Table,Column, ForeignKey, \
Integer, VARCHAR, DATETIME,TEXT,BOOLEAN, \
select,insert,update,desc
from contextlib import closing
try:
    from src import app
except ImportError:
    from config import DevelopmentConfig as dev_conf
from help_connect import ping_connection
import logging

def connect_and_get(query):
    try:
        eng = create_engine(app.config["DATABASE"], pool_recycle=3600)
    except:
        # minor hack for development (sometimes
        # it is useful to test models on their own
        # without the context of app object )
        eng = create_engine(dev_conf.DATABASE)
    try:
        with closing(eng.connect()) as con:
            result = con.execute(query)
        return result
    except Exception as e:
        logging.error(e)
        logging.info("query was: %s " % query)
        return False

def zip_results(columns,results):
    """
    Zip columns of a given table
    with a set of results obtained
    from a query.
        :columns accepts sql collection of columns,
        :results a list of tuples obtained by running fetchall method on cursor object
    
    DO NOT PASS CURSOR, PASS ONLY A LIST OBTAINED BY CURSOR.FETCHALL()
    
    returns a dictionary
    """
    cols = [str(col).split(".")[1] for col in columns]
    return [dict(zip(cols,row)) for row in results]

class Model(object):
    def create_db(self,name):
        query = connect_and_get("CREATE DATABASE " + name + " IF not exist")    
        return query

    def insert_(self,to_insert):
        """
        To insert has to be a dict with columns names as keys
        and elements to insert as values
        """
        ins = self.structure.insert().values(to_insert)
        return connect_and_get(ins)

    def select(self,what,columnname,var_value):
        """
        Select where 
        """
        var_value = str(var_value)
        t = self.structure
        s = select([what]).where(columnname == var_value)
        return connect_and_get(s)
 

class User_(Model):
    metadata = MetaData()
    structure = Table("users", metadata,
                               Column("uid",Integer,primary_key=True),
                               Column("username",VARCHAR(90),index=True),
                               Column("password",TEXT),
                               Column("email",VARCHAR(100)),
                               Column("about_me",TEXT),
                               Column("points",VARCHAR(90)),
                               Column("date_created",DATETIME),
                               Column("oAuth", BOOLEAN))

    def getPass(self,username):
        """ Or rather check password, used when user logs in """
        t = self.structure
        s = select([t.c.password, t.c.oAuth]).where(t.c.username == username)
        result = connect_and_get(s)
        if result:
            row = result.fetchone()
            if row != None and not row[1]:
                saved_password = dict(password=row[0])
                return saved_password
            return False
        return False

    def inDb(self,username):
        t = self.structure
        s = select([t.c.username]).where(t.c.username == username)
        result = connect_and_get(s)
        if result:
            row = result.fetchone()
            if row == None:
                return False
            return True
        return False
    
    def get_username(self,username):
        t = self.structure
        s = select([t.c.id]).where(t.c.username == username)
        result = connect_and_get(s)
        return result

    def get_profile(self,username):
        """
        Display user's profile
        """
        t = self.structure
        s = select([t.c.id,t.c.username,t.c.email,t.c.about_me,t.c.points,t.c.date_created]).where(t.c.username == str(username))
        result = connect_and_get(s)
        if result:    
            row = result.fetchone()
            profile = dict(num=row[0],username=row[1],email=row[2],
                           about_me=row[3],points=row[4],
                           date_created=row[5])
            return profile
        return False

    def update_profile(self,username,to_insert):
        """
        Modify profile
        """
        t = self.structure
        upd = t.update().where(t.c.username == str(username)).values(to_insert)
        return upd

class ReviewRequestModel(Model):
    metadata = MetaData()
    structure = Table("reviewRequests", metadata,
                    Column("reqId",Integer,primary_key=True),
                    Column("uid",VARCHAR(90),index=True),
                    Column("title",VARCHAR(64)),
                    Column("content",TEXT),
                    Column("category",VARCHAR(98)),
                    Column("date_requested",DATETIME),
                    Column("deadline",VARCHAR(90)),
                    Column("articleURL",TEXT)
                    Column("rate_req",Iteger))
    
    # number of articles displayed on startpage
    limes = 5

    def select_user_requests(self,username):
        """
        
        """
        s = select([self.structure]).where(self.structure.c.username == username)
        result = connect_and_get(s).fetchall()
        if result:
            return zip_results(self.structure.columns,result)
        return False
    
    def parse_all(self,offset=0):
        off = offset * self.limes
        s = select([self.structure]).order_by(desc("date_requested")).limit(self.limes).offset(off)
        result = connect_and_get(s)
        if result:
            allRequests = [dict(id=row[0],title=row[1],content=row[2],
                      category=row[3],date_requested=row[4],
                      deadline=row[5],username=row[6],articleURL=row[7]) for row in result.fetchall()]
            return allRequests
        return False

    def count_all(self):
        s = self.structure.count()
        re = connect_and_get(s)
        if re:
            return int(re.fetchone()[0]/self.limes)
        return False

    def get_request_review(self,num):
        """
        Displays one single review request
        after the user clicks on the title
        on the homepage.
        """
        t = self.structure
        s = select([t]).where(t.c.id == num)
        result = connect_and_get(s)
        if result:
            row = result.fetchone()
            singleRR = dict(num=row[0],title=row[1],
                             content=row[2],category=row[3],
                             date_requested=row[4],deadline=row[5],
                             username=row[6],articleURL=row[7])
            result.close()
            return singleRR
        return False

    def update_post(self,num,title,content,category,deadline):
        t = self.structure
        u = t.update().where(t.c.id == num).\
        values(title=title,content=content,
            category=category,deadline=deadline)
        res = connect_and_get(u)
        print res
        if res:
            return True
        return False

    def get_best_requests(self,offset):
        """
        Returns best review requests
        """
        pass

class ReviewX(Model):
    metadata = MetaData()
    structure = Table("reviews", metadata,
                    Column("revid",Integer,primary_key=True),
                    Column("reqId",Integer, index=True), #ForeignKey(ReviewRequestModel.structure.c.id,onupdate="CASCADE")),
                    Column("uid",VARCHAR(90),index=True),
                    Column("review_text",TEXT),
                    Column("rating",VARCHAR(4)),
                    Column("date_written",DATETIME),
                    Column("rate_review", Integer)
                    )

    def get_reviews_of_user(self,username):
        """
        Returns all responses to request reviews
        So for user admin it returns all responses
        to request reviews made by admin
        """
        t = self.structure
        s = select([t]).where(t.c.reviewed == username)
        result = connect_and_get(s).fetchall()
        if result:
            return zip_results(self.structure.columns,result)
        return False
   
    def get_reviews_by_user(self,username):
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
            return zip_results(self.structure.columns,result)
        return False

    def get_best_reviews(self,offset):
        """
        returns best reviews, highest rated ones
        """
        pass