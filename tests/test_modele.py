"""
Runs script responsible for communication with db
in isolation from view functions.
"""
from src.modele import User,ReviewRequestModel,Review,connect_and_get
from src.modele import connect_and_get as con_get
from src.hashing_ import hash_password,check_password
from sqlalchemy.exc import ProgrammingError
import datetime
import time
import unittest
import logging
logging.basicConfig(level=logging.DEBUG)

class TestConnection(unittest.TestCase):
	def test_connection_ok(self):
		query = "SELECT * FROM users"
		response = connect_and_get(query)
		self.assertTrue(response)

	@unittest.skip("we want to see some real not provoked errors")
	def test_connection_not_ok(self):
		# pawel types wrong query will his break the app?
		query = "SELECT ** FROM users" 
		response = connect_and_get(query)
		self.assertFalse(response)
		#self.assertRaises(ProgrammingError,connect_and_get,query)

class UserTestSelects(unittest.TestCase):
	user = User()
	
	def test_get_pass(self):
		"""
		Tests if query returns right password for 
		right people.
		"""
		
		# Hugo logs in with valid pass
		attempt = self.user.check_pass("Hugo","secret")
		self.assertTrue(attempt)

		# Hugo makes a mistake, logs in with invalid pass
		attempt = self.user.check_pass("Hugo","secret1")
		self.assertFalse(attempt)

		# Someone who is not registered tries to login
		attempt = self.user.check_pass("Marco","secret")
		self.assertFalse(attempt)

	def test_get_profile(self):
		attempt = self.user.get_profile("Hugo")
		self.assertIsInstance(attempt,dict)
		self.assertEqual(6,len(attempt))
		self.assertIn(u'Hugo',attempt["username"])
		self.assertIn(u'I love cats',attempt["about_me"])

		# David does not exist but tries to get his profile
		attempt = self.user.get_profile("David")
		self.assertFalse(attempt)

	def test_update_profile(self):
		# Hugo wants to change about_me to 'loves dogs'
		attempt = self.user.update_profile('Hugo', about_me="I love dogs not cats")
		
		#but then he changes his mind and changes it again to something else
		attempt = self.user.update_profile('Hugo', about_me="I love cats")
		check_it = self.user.get_profile("Hugo")
		self.assertIn("I love cats",check_it["about_me"])

class TestReviewRequest(unittest.TestCase):
	req = ReviewRequestModel()
	
	def test_select_user_requests(self):
		# Hugo wants to see his requests
		attempt = self.req.select_user_requests("Hugo")

		# he gets a list of dictionaries...
		self.assertIsInstance(attempt,list)
		self.assertIsInstance(attempt[0],dict)

		# where first item has some title
		self.assertIn("Faith and free market",attempt[0]["title"])

		# Jurek doesn't exist but wants to see his requests
		attempt = self.req.select_user_requests("Frank")
		self.assertFalse(attempt)

	def test_parse_all(self):
		# John wants to see all requests
		attempt = self.req.parse_all(0)
		self.assertIsInstance(attempt,list)
		self.assertEqual(len(attempt),5)	
		self.assertIsInstance(attempt[0],dict)
		self.assertEqual(len(attempt[0].keys()),9)
		self.assertIn(attempt[0]["username"],'Hugo')

		# Mary clicks on page two, she needs result with
		# offset 5 TO DO

	def test_get_request_review(self):
		attempt = self.req.get_request_review(102)

		#logging.info(attempt)
		self.assertIsInstance(attempt,dict)
		self.assertIn("abook on love",attempt["title"])
		#logging.info("Alice feels fine")

		attempt = self.req.get_request_review(1)
		self.assertFalse(attempt)

	def test_update_review_request(self):
		timestamp = datetime.datetime.fromtimestamp(time.time())
		attempt = self.req.update_review_request(101,"new title",
			"new content","erotic",timestamp)
		self.assertTrue(attempt)

		check_attempt = self.req.get_request_review(101)
		
		self.assertIn("new title",check_attempt["title"])
		self.req.update_review_request(101,"Faith and free market", \
			 "need a review of a fragment of my article on faith","academic",timestamp)

	def test_rate_req_rev(self):
		value_before = self.req.get_request_review(101)["rate_req"]
		attempt = self.req.rate_req_rev(101)
		value_after = self.req.get_request_review(101)["rate_req"]
		self.assertEqual(value_before+1,value_after)

		#request doesn't exist
		attempt = self.req.rate_req_rev(190)
		self.assertFalse(attempt)

	def test_rate_req_rev_minus(self):
		value_before = self.req.get_request_review(101)["rate_req"]
		attempt = self.req.rate_req_rev_minus(101)
		value_after = self.req.get_request_review(101)["rate_req"]
		self.assertEqual(value_before-1,value_after)

class TestReviewObject(unittest.TestCase):
	rev = Review()

	def test_get_review(self):
		attempt = self.rev.get_review(201)
		self.assertIsInstance(attempt,dict)
		self.assertIsInstance(attempt.get('revid'),long)
		self.assertEqual(attempt["revid"], 201)
		self.assertIn("Alice", attempt["reviewer"])
		self.assertIn("Hugo", attempt["requesting"])
		self.assertIn("title", attempt.keys())

	def test_get_users_reviews(self):
		#Alice wants to see again her review of Hugo
		attempt = self.rev.get_users_reviews("Alice")
		
		self.assertIsInstance(attempt,list)
		#... she sees Hugo's name in username field
		#self.assertIn(attempt["review_text"],"Well how")
		self.assertIn(attempt[0]["title"],'Faith and free market')
		self.assertIn(attempt[0]["reviewed"],"Hugo")
		self.assertEqual(len(attempt[0]),6)

		# she sees her review text
		self.assertIn("Well how do I begin",attempt[0]["review_text"])

		# Hugo wants to see his reviews but he doesn't
		# have any
		attempt = self.rev.get_users_reviews("Hugo")
		
		self.assertFalse(attempt)

	def test_get_reviews_of_user(self):
		# Hugo wants to see who wrote a review of his draft
		attempt = self.rev.get_reviews_of_user("Hugo")
		self.assertIsInstance(attempt,list) #returns a list of responses
		self.assertIn("Alice",attempt[0]["reviewer"])
		self.assertIn("Faith",attempt[0]['title'])
		self.assertIn("Well how do I",attempt[0]['review_text'])

		# Don wants to see who reviewed his draft but no one did
		attempt = self.rev.get_reviews_of_user("Don")
		self.assertFalse(attempt)

	def test_get_best_reviews(self):
		attempt = self.rev.get_best_reviews()
		self.assertIsInstance(attempt,list)
		self.assertIn("Alice",attempt[0]['reviewer'])

		# reviews with offset and limit
		attempt = self.rev.get_best_reviews(2,2)
		self.assertIsInstance(attempt,list)
		self.assertEqual(2,len(attempt))

	def test_rate_review(self):
		before = self.rev.get_review(201).get("rate_review")
		do_update = self.rev.rate_review(201)
		after = self.rev.get_review(201)["rate_review"]
		self.assertEqual(before+1,after)

	def test_rate_review_minus(self):
		before = self.rev.get_review(201)["rate_review"]
		do_update = self.rev.rate_review_minus(201)
		after = self.rev.get_review(201)["rate_review"]
		self.assertEqual(before-1,after)

if __name__ == "__main__":
	unittest.main()