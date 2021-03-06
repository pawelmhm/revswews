# -*- coding: utf-8 -*-
import os,sys
#sys.path.insert(1,os.path.dirname(os.path.dirname(os.path.abspath(__name__))))
import os
from src import flaskr
from utilities import manipulate_db
import unittest
import tempfile
from contextlib import closing
import time
import logging
from src.config import TestConfig
from utilities import manipulate_db
from bs4 import BeautifulSoup

def findElem(content,elem,id):
    soup = BeautifulSoup(content)
    return soup.find(elem,id=id)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class LoginTestCase(unittest.TestCase):
    def setUp(self):
        """Before each test, set up a blank database"""
        self.app = flaskr.app.test_client()

    def tearDown(self):
        pass

    def login(self,username,password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password), follow_redirects=True)

    def logout (self):
        return self.app.get('/logout', follow_redirects=True)

    def unauthorized(self,url):
        return self.app.get(url)

    def testUnauthorized(self):
        urls = ['/display_user_requests/9','/reviews_by_user/9','/reviews_of_user/9']
        for url in urls:
            rv = self.unauthorized(url)
            self.assertEqual(302,rv.status_code)

    def test_login_logout(self):
        rv = self.login("admin", "default")
        self.assertEqual(rv.status_code,200)
        self.logout()
        rv = self.login("Hugo","secret")
        self.assertIn("Logged in as Hugo",rv.data, )
        self.logout()
        rv = self.login('evilDoer', 'evilgenius')
        self.assertIn("Invalid username or password", rv.data)
        rv = self.login("Hugo","Makarena")
        self.assertIn("Invalid username or password",rv.data)

    def add_user(self,username,password,confirm,email,oAuth):
        return self.app.post("/add_user", data=dict(username=username,
                password=password, confirm=confirm,email=email,oAuth=oAuth), follow_redirects=True)

    def testAddUser(self):
        rv = self.add_user("admin","default1234",'default1234', "with_new_database@o2.pl",0)
        self.assertIn("username taken", rv.data)

        rv = self.add_user("Zubizareta", "default123",'default123', "with_new_database@o2.pl",0)
        self.assertEqual(rv.status_code,200)
        self.assertIn("Hello Zubizareta, please login here",rv.data)

        rv = self.add_user("Robbi", "diogenes123",'diogenes123', "pedro@o2.pl",0)
        self.assertIn("Hello Robbi, please login here",rv.data)

        rv = self.login("Robbi","diogenes123")
        self.assertIn('Logged in as Robbi',rv.data)

        rv = self.add_user('Miąższ','diodor99','diodor99','diodor@o2.pl',0)
        self.assertEqual(rv.status_code,200)
        self.assertIn("password and username must be in ascii",rv.data)

    def testRegisterUser(self):
        fakeUser = {"username":"Gerard", "email":"gerard@pique.com","password":"BarcelonaFC"}
        rv = flaskr.register_user(fakeUser)

    def testoAuth(self):
        rv = self.add_user('Pawel_Miech','diogenes12','diogenes12','pawelmhm@gmail.com',1)
        self.assertIn('Hello Pawel_Miech, ', rv.data, findElem(rv.data,'input','username'))
        rv = self.login('Pawel_Miech','')
        self.assertIn('field is required',rv.data,findElem(rv.data,'form','login'))
        rv = self.login('Pawel_Miech', 'a')
        self.assertIn('Invalid username or password',rv.data)
        rv = self.login('Pawel_Miech','"null')
        self.assertIn('Invalid username or password',rv.data)

if __name__ == '__main__':
    manipulate_db.populateDb(TestConfig.DATABASE)
    unittest.main()
