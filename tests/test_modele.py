"""
Runs script responsible for communication with db
in isolation from view functions.
"""
from src.modele import User,ReviewRequestModel,ReviewX
from src.modele import connect_and_get as con_get
from src.hashing_ import hash_password,check_password
import datetime
import time
import unittest
import logging
logging.basicConfig(level=logging.DEBUG)

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
		attempt = self.req.select_user_requests(1)
		self.assertIsInstance(attempt,dict)
		self.assertIn("Faith and free market",attempt["title"])

		# Jurek doesn't exist but wants to see his requests
		attempt = self.req.select_user_requests(11)
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
	
if __name__ == "__main__":
	unittest.main()