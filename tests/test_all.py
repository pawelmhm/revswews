import os,sys
sys.path.insert(1,os.path.dirname(os.path.dirname(os.path.abspath(__name__))))
from src import flaskr
from src import populateDb
import unittest
import tempfile
from contextlib import closing
import time
import test_login
from datetime import datetime
from src import modele

timestamp = datetime.fromtimestamp(time.time())

class BaseTestCase(unittest.TestCase):
    def setUp(self):
        """Before each test, set up a blank database"""
        self.app = flaskr.app.test_client()
        flaskr.remove_db()
        flaskr.init_db()
        flaskr.populateDb()
        self.login("Hugo","secret")

    def tearDown(self):
        self.logout()
        flaskr.remove_db()
    
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
        assert "Edit your profile Hugo" in rv.data

    def update_profile(self, email,about_me):
        return self.app.post("/edit_profile", data=dict(email=email,
            about_me=about_me), follow_redirects=True)

    def test_update_profile(self):
        rv = self.update_profile("maniana", "Curious explorer of new lands")
        assert "Your profile has been updated" in rv.data

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

    def review_this(self,title,content,rating,date_written, reviewed,request_id):
        url = '/req/' + str(request_id)
        return self.app.post(url, data=dict(
            title=title,
            content=content,
            rating=rating,
            date_written=date_written,
            reviewed=reviewed,request_id=request_id),
        follow_redirects=True)

    def test_review_this(self):
        timestamp = datetime.fromtimestamp(time.time())
        rv = self.review_this("hello world",
            "nice work this is amazing", "good",
                timestamp,"carlos",2)
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
        url = "/req/" + str(1)
        rv = self.app.get(url)
        self.assertIn("Update Request",rv.data)

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
        # what if update is not allowed? Hugo's article has id 1, he tries
        # to update 3
        rv = self.update_post(3,"new title","new content","academic",timestamp)
        self.assertEqual(200,rv.status_code)
        self.assertIn("error inside an application", rv.data)

        rv = self.update_post(1,"new title","new content","academic",timestamp)
        self.assertIn("Request updated",rv.data)
        #self.assertIn("request updated",rv.data)

    def test_update_query(self):
        # tests only the model without making request to flask
        rev_req = modele.ReviewRequestModel()
        rev_req.update_post(1,"new title","new content","new category", timestamp)
        re = rev_req.get_request_review(1)
        self.assertEqual(re["title"],"new title")

if __name__ == '__main__':
    unittest.main()