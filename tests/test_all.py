"""
Integration tests for the app.
"""
import os,sys
import unittest
from contextlib import closing
from datetime import datetime
import time
import StringIO
import logging

from flask import url_for

from src import flaskr
from src import modele
from src.config import TestConfig
from utilities import manipulate_db
from tests import test_login

timestamp = datetime.fromtimestamp(time.time())
logging.basicConfig(level=logging.DEBUG) 
logger = logging.getLogger(__name__)

class BaseTestCase(unittest.TestCase):
    def setUp(self):
        """Before each test, set up a blank database"""
        self.app = flaskr.app.test_client()
        self.login("Hugo", "secret")

    def tearDown(self):
        self.logout()
    
    def login(self,username,password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password), follow_redirects=True)

    def logout (self):
        return self.app.get('/logout', follow_redirects=True)

class GeneralTestCase(BaseTestCase):
    
    def edit_profile(self):
        return self.app.get("/edit_profile", follow_redirects=True)

    def test_edit_profile(self):
        rv = self.edit_profile()
        self.assertIn("Edit your profile Hugo", rv.data)

    def update_profile(self, email,about_me):
        return self.app.post("/edit_profile", data=dict(email=email,
            about_me=about_me), follow_redirects=True)

    def test_update_profile(self):
        rv = self.update_profile("maniana", "Curious explorer of new lands")
        self.assertIn("Your profile has been updated", rv.data)

    def request_review(self):
        return self.app.get("/request_review", follow_redirects=True)

    def make_review_request(self,title,content,category,deadline):
        return self.app.post("/post_request_review", data=dict(
            title=title,
            content=content,
            category=category,
            deadline=deadline), follow_redirects=True)

    def test_request_review(self):
        rv = self.request_review()
        self.assertEqual(200,rv.status_code)
    
    @unittest.skip("make review request tested with files")
    def test_make_review_request(self):
        rv = self.make_review_request("title", "In this wos of so much importance to literature.", "academic",
            "09/12/2012")
        self.assertEqual(200,rv.status_code)    
	
    def main_thread(self):
        return self.app.get('/', follow_redirects=True)

    def test_main_thread(self):
        rv = self.main_thread()
        self.assertEqual(200, rv.status_code)

    def click_reviews(self,id):
        url = "/req/" + str(id)
        return self.app.get(url, follow_redirects=True)

    def test_click_reviews(self):
        rv = self.click_reviews(1)
        #logging.info(rv.data)
        self.assertEqual(200, rv.status_code)

    def display_user_requests(self):
        return self.app.get('/display_user_requests', follow_redirects=True)

    def test_display_user_request(self):
        rv = self.display_user_requests()
        assert "Hugo" in rv.data

    def review_this(self,review_text,rating,request_id):
        url = '/req/post/' + str(request_id)
        return self.app.post(url, data=dict(
            review_text=review_text,
            rating=rating),
        follow_redirects=True)

    def test_review_this(self):
        # invalid request
        response = self.review_this("good work",99,102)
        self.assertIn("errors",response.data)
        
        rv = self.review_this(
            "nice work this is amazing", 5, 101)
        self.assertEqual(rv.status_code,200)
        self.assertIn("has been added",rv.data)

    def display_user_reviews(self):
        return self.app.get("/display_user_reviews", follow_redirects=True)

    def test_display_user_reviews(self):
        rv = self.display_user_reviews()
        assert "All reviews written by you" in rv.data

    def show_responses(self,id):
        return self.app.get('/responses')

    def test_show_responses(self):
        rv = self.show_responses(1)
        self.assertEqual(200,rv.status_code)

    def test_update_possible(self):
        url = "/req/" + str(101)
        rv = self.app.get(url)
        self.assertIn("Update Request", rv.data)

        url = "/req/" + str(3)
        rv = self.app.get(url)
        self.assertNotIn("Update Request", rv.data)

    def update_post(self,id,title,content,category,deadline):
        url = "/req/update/" + str(id)
        return self.app.post(url,data=dict(
            title=title,
            content=content,
            category=category,
            deadline=deadline), follow_redirects=True)

    #@unittest.skip("not implemented yet")
    def test_update_post(self):
        # what if update is not allowed? Hugo's article has id 101, he tries
        # to update 102
        rv = self.update_post(102,"new title","new content with long soom",\
            "academic",timestamp)
        self.assertEqual(200,rv.status_code)
        self.assertIn("invalid", rv.data)

        # now a valid request
        rv = self.update_post(101,"new title","new content with a lot of blah", \
            "academic",timestamp)
        self.assertIn("ok",rv.data)

class TestPostRequest(BaseTestCase):
    data = {'title':'Lewiathanus livus',
        'content':'A book by Hobbes is always worth reading',
        'category':'academic', 'deadline':str(timestamp)}
    
    rather_not = ['sh', 'ps1','ghost','exe']    
    
    def do_post(self, data):
        return self.app.post('/request_review', data=data, 
            follow_redirects=True)

    def upload_something(self, extension, message):
        """ 
        Message, expected messaged in flash.
        """
        data = self.data.copy()
        filename = 'file.%s' % extension
        data["file"] = (StringIO.StringIO('new file'), filename)
        response = self.do_post(data)
        self.assertEqual(response.status_code,200)
        self.assertIn(message,response.data)

    def test_upload_allowed_formats(self):
        # valid formats
        for ext in TestConfig.ALLOWED_EXTENSIONS:
            self.upload_something(ext,'review request sucessfuly')
        
    def test_upload_invalid_data(self):
        # Invalid extensions
        # we expect a message informing about it
        message = "following formats are allowed:"
        for ext in self.rather_not:
            self.upload_something(ext, message)

    def test_no_file(self):
        rv = self.do_post(self.data)
        self.assertEqual(rv.status_code,200)
        self.assertIn("No file added",rv.data)

    def test_invalid_form(self):
        data = self.data.copy()
        data["content"] = ""
        rv = self.do_post(data)
        self.assertEqual(rv.status_code,200)
        self.assertIn("Invalid form.",rv.data)

if __name__ == '__main__':
    manipulate_db.populateDb(TestConfig.DATABASE)
    unittest.main()