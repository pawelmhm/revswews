# -*- coding: utf-8 -*-
from sqlalchemy import *
from functools import wraps
from contextlib import closing
from src import app

def connect(func):
    eng = create_engine(app.config["DATABASE"])
    @wraps(func)
    def wrapped(*args,**kwargs):
        with closing(eng.connect()) as con:
            result = con.execute(func(*args,**kwargs))
        return result
    return wrapped
    
class Model(object):
    @connect
    def create_db(self,name):
        query = "CREATE DATABASE " + name + " IF not exist"
        return query

    def create_tables(self,tab1,tab2,tab3,eng):
        tab1.structure.create(eng)
        tab2.structure.create(eng)
        tab3.structure.create(eng)

    @connect
    def get_results(self):
        """
        takes table name and returns a query on the table
        """
        s = select([self.structure])
        return s

    @connect
    def insert_(self,to_insert):
        """
        To insert has to be a dict with columns names as keys
        and elements to insert as values
        """
        ins = self.structure.insert().values(to_insert)
        return ins
        
    @connect
    def select(self,what,columnname,var_value):
        """
        Select where 
        """
        var_value = str(var_value)
        t = self.structure
        s = select([what]).where(columnname == var_value)
        return s

class ReviewX(Model):
    def __init__(self):
        Model.__init__(self)
        self.metadata = MetaData()
        self.structure = Table("reviews", self.metadata,
                               Column("id",Integer,primary_key=True),
                               Column("title",VARCHAR(64)),
                               Column("review",TEXT),
                               Column("rating",VARCHAR(4)),
                               Column("date_written",DATETIME),
                               Column("reviewer",VARCHAR(90)),
                               Column("reviewed",VARCHAR(90)),
                               Column("request_id",Integer))

    @connect
    def get_reviews_of_user(self,username):
        """
        Returns all responses to request reviews
        So for user admin it returns all responses
        to request reviews made by admin
        """
        t = self.structure
        s = select([t]).where(t.c.reviewed == username)
        return s

    @connect
    def get_reviews_by_user(self,username):
        """
        This is the reverse of the function above
        it displays all reviews written by given user
        for admin it will return all things that this user
        had written about others
        """
        t = self.structure
        s = select([t]).where(t.c.reviewer == username)
        return s
    
class ReviewRequestModel(Model):
    def __init__(self):
        """ TODO remove username_id, its useless"""
        Model.__init__(self)
        self.metadata = MetaData()
        self.structure = Table("reviewRequests", self.metadata,
                               Column("id",Integer,primary_key=True),
                               Column("title",VARCHAR(64)),
                               Column("content",TEXT),
                               Column("category",VARCHAR(98)),
                               Column("date_requested",DATETIME),
                               Column("deadline",VARCHAR(90)),
                               Column("username_id",VARCHAR(90)),
                               Column("username",VARCHAR(90)),
                               Column("articleURL",TEXT))

    @connect
    def select_user_requests(self,username):
        """
        
        """
        s = select([self.structure]).where(self.structure.c.username == username)
        return s
    
    @connect
    def select_all(self):
        s = select([self.structure]).order_by(desc("date_requested"))
        return s

    def parse_all(self):
        result = self.select_all()
        allRequests = [dict(id=row[0],title=row[1],content=row[2],
                      category=row[3],date_requested=row[4],
                      deadline=row[5],username=row[7],articleURL=row[8]) for row in result.fetchall()]
        return allRequests

    @connect
    def display_request_review(self,num):
        """
        Displays one single review request
        after the user clicks on the title
        on the homepage.

        This should be somehwere else!
        """
        t = self.structure
        s = select([t]).where(t.c.id == num)
        return s

    def parse_request_review(self,num):
        result = self.display_request_review(num)
        row = result.fetchone()
        singleRR = dict(num=row[0],title=row[1],
                         content=row[2],category=row[3],
                         date_requested=row[4],deadline=row[5],
                         username_id=row[6],username=row[7],articleURL=row[8])            
        return singleRR
              
class User_(Model):
    def __init__(self):
        Model.__init__(self)
        self.metadata = MetaData()
        self.structure = Table("users", self.metadata,
                               Column("id",Integer,primary_key=True),
                               Column("username",VARCHAR(64)),
                               Column("password",TEXT),
                               Column("email",VARCHAR(100)),
                               Column("about_me",TEXT),
                               Column("points",VARCHAR(90)),
                               Column("date_created",DATETIME),
                               Column("oAuth", BOOLEAN))

    @connect
    def queryPass(self,username):
        """ Or rather check password, used when user logs in """
        t = self.structure
        s = select([t.c.password, t.c.oAuth]).where(t.c.username == username)
        return s

    def getPass(self,username):
        result = self.queryPass(username)
        if result:
            row = result.fetchone()
            if row != None and not row[1]:
                saved_password = dict(password=row[0])
                return saved_password
            else:
                return False
        else:
            return False

    @connect
    def checkDb(self,username):
        t = self.structure
        s = select([t.c.username]).where(t.c.username == username)
        return s

    def inDb(self,username):
        result = self.checkDb(username)
        if result:
            row = result.fetchone()
            if row == None:
                return False
            else:
                return True
    
    @connect
    def get_username(self,username):
        t = self.structure
        s = select([t.c.id]).where(t.c.username == username)
        return s

    @connect
    def edit_profile(self,username):
        """
        This only displays user's profile
        """
        t = self.structure
        s = select([t.c.id,t.c.username,t.c.email,t.c.about_me,t.c.points,t.c.date_created]).where(t.c.username == str(username))
        return s

    def parse_profile(self,username):
        result = self.edit_profile(username)
        row = result.fetchone()
        profile = dict(num=row[0],username=row[1],email=row[2],
                       about_me=row[3],points=row[4],
                       date_created=row[5])
        return profile

    def update_profile(self,username,to_insert):
        """
        Modifies the profile of a given user
        """
        t = self.structure
        upd = t.update().where(t.c.username == str(username)).values(to_insert)
        return upd
