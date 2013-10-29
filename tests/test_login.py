import os,sys
sys.path.insert(1,os.path.dirname(os.path.dirname(os.path.abspath(__name__))))
import os
from src import flaskr
from utilities import manipulate_db
import unittest
import tempfile
from contextlib import closing
import time
import logging

#logging.basicConfig(filename="test_logs.log",level=logging.DEBUG,format='%(asctime)s \n %(message)s')

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
        return self.app.get(url,follow_redirects=True)

    @unittest.skip("skipped")
    def testUnauthorized(self):
        urls = ['/req/1','/display_user_requests','/display_user_reviews','/responses']
        for url in urls:
            rv = self.unauthorized(url)
            self.assertIn("You are not authorized to view this page, please register first",rv.data)

    def test_login_logout(self):
        rv = self.login("admin", "default")
        self.assertEqual(rv.status_code,200)
        self.logout()
        rv = self.login("Hugo","secret")
        self.assertIn("Logged in as Hugo",rv.data)
        self.logout()
        rv = self.login('evilDoer', 'evilgenius')
        self.assertIn(" in our database", rv.data)
        rv = self.login("Hugo","Makarena")
        self.assertIn("Invalid username or password",rv.data)

    def add_user(self,username,password,confirm,email,oAuth):
        return self.app.post("/add_user", data=dict(newUsername=username,
                newPassword=password, confirm=confirm,email=email,oAuth=oAuth), follow_redirects=True)

    def testAddUser(self):
        rv = self.add_user("Zubizareta", "default123",'default123', "with_new_database@o2.pl",0)
        self.assertEqual(rv.status_code,200)
        self.assertIn("Hello Zubizareta, please login here",rv.data)
        rv = self.add_user("Robbi", "diogenes123",'diogenes123', "pedro@o2.pl",0)
        self.assertIn("Hello Robbi, please login here",rv.data)
        rv = self.add_user("admin","default1234",'default1234', "with_new_database@o2.pl",0)
        self.assertIn("username taken", rv.data)


    def testoAuth(self):
        rv = self.add_user('Pawel_Miech','diogenes12','diogenes12','pawelmhm@gmail.com',1)
        self.assertIn('Hello Pawel_Miech, ', rv.data)
        rv = self.login('Pawel_Miech','')
        self.assertIn('field is required',rv.data)
        rv = self.login('Pawel_Miech', 'a')
        self.assertIn('Invalid username or password',rv.data)
        rv = self.login('Pawel_Miech','"null')
        self.assertIn('Invalid username or password',rv.data)

if __name__ == '__main__':
    unittest.main()
