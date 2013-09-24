# -*- coding: utf-8 -*-
from sqlalchemy import *
from functools import wraps
from contextlib import closing
from src import app

def connect_and_get(query):
    eng = create_engine(app.config["DATABASE"])
    try:
        with closing(eng.connect()) as con:
            result = con.execute(query)
        return result
    except:
        if not con.closed:
            con.close()
        return False

def zip_results(columns,results):
    """
    Zip columns of a given table
    with a set of results obtained
    by running a query on a table.
    => columns accepts sql collection of columns,
    => results a list of tuples obtained by running fetchall method on cursor object
    DO NOT PASS CURSOR, PASS ONLY A LIST OBTAINED BY CURSOR.FETCHALL()
    returns a dictionary
    """
    cols = [str(col).split(".")[1] for col in columns]
    return [dict(zip(cols,row)) for row in results]
 
class Model(object):
    def create_db(self,name):
        query = connect_and_get("CREATE DATABASE " + name + " IF not exist")    
        return query

    def create_tables(self,tab1,tab2,tab3,eng):
        tab1.structure.create(eng)
        tab2.structure.create(eng)
        tab3.structure.create(eng)
        
    def get_results(self):
        """
        takes table name and returns a query on the table
        """
        s = connect_and_get(select([self.structure]))
        return s

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

class ReviewX(Model):
    metadata = MetaData()
    structure = Table("reviews", metadata,
                               Column("id",Integer,primary_key=True),
                               Column("title",VARCHAR(64)),
                               Column("review",TEXT),
                               Column("rating",VARCHAR(4)),
                               Column("date_written",DATETIME),
                               Column("reviewer",VARCHAR(90)),
                               Column("reviewed",VARCHAR(90)),
                               Column("request_id",Integer))

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
        else:
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
        else:
            return False
    
class ReviewRequestModel(Model):
    metadata = MetaData()
    structure = Table("reviewRequests", metadata,
                               Column("id",Integer,primary_key=True),
                               Column("title",VARCHAR(64)),
                               Column("content",TEXT),
                               Column("category",VARCHAR(98)),
                               Column("date_requested",DATETIME),
                               Column("deadline",VARCHAR(90)),
                               Column("username_id",VARCHAR(90)),
                               Column("username",VARCHAR(90)),
                               Column("articleURL",TEXT))

    def select_user_requests(self,username):
        """
        
        """
        s = select([self.structure]).where(self.structure.c.username == username)
        result = connect_and_get(s).fetchall()
        if result:
            return zip_results(self.structure.columns,result)
        return False
    
    def parse_all(self):
        s = select([self.structure]).order_by(desc("date_requested"))
        result = connect_and_get(s)
        if result:
            allRequests = [dict(id=row[0],title=row[1],content=row[2],
                      category=row[3],date_requested=row[4],
                      deadline=row[5],username=row[7],articleURL=row[8]) for row in result.fetchall()]
            return allRequests
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
                             username_id=row[6],username=row[7],articleURL=row[8])
            result.close()
            return singleRR
        return False
              
class User_(Model):
    metadata = MetaData()
    structure = Table("users", metadata,
                               Column("id",Integer,primary_key=True),
                               Column("username",VARCHAR(64)),
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
            else:
                return False
        else:
            return False

    def inDb(self,username):
        t = self.structure
        s = select([t.c.username]).where(t.c.username == username)
        result = connect_and_get(s)
        if result:
            row = result.fetchone()
            if row == None:
                return False
            else:
                return True
    
    def get_username(self,username):
        t = self.structure
        s = select([t.c.id]).where(t.c.username == username)
        result = connect_and_get(s)
        return result

    def get_profile(self,username):
        """
        This only displays user's profile
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
        Modifies the profile of a given user
        """
        t = self.structure
        upd = t.update().where(t.c.username == str(username)).values(to_insert)
        return upd
#print "hello world"
#a = ReviewRequestModel()
#print a.select_user_requests("Alice")
#print a.display_request_review(2)
#b = User_()
#c = ReviewX()
#print c.get_reviews_of_user("Alice")
#print c.get_reviews_by_user("Bob")
