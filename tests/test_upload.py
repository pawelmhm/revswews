#from test_all import BaseTestCase
import unittest
import requests
from datetime import datetime
import time
import os,sys
sys.path.insert(1,os.path.dirname(os.path.dirname(os.path.abspath(__name__))))
from src import flaskr
timestamp = datetime.fromtimestamp(time.time())

dataF = {'title':'Lewiathanus livus','content':'A book by Hobbes is always worth reading',
         'category':'academic','date_requested':str(timestamp),'deadline':str(timestamp),'username':'admin'}
         
url = 'http://localhost:5000/post_request_review'

class UploadTestCase(unittest.TestCase):
    def setUp(self):
        pass
        #flaskr.init_db()
        #flaskr.populateDb()

    def tearDown(self):
        pass
        #flaskr.remove_db()
        
    def getSession(self):
        data = {'username':'admin','password':'default'}
        url = 'http://localhost:5000/login'
        re = requests.post(url,data)
        cookies = re.cookies
        return cookies
        
    def upload_it(self):
        #http://stackoverflow.com/a/688193/1757620
        cookies = self.getSession()
        files = {'file':open('sampleUploads//tekst1.txt')}
        r = requests.post(url,data=dataF,files=files,cookies=cookies)
        return r

    def test_upload_txt(self):
        rv = self.upload_it()
        self.assertIn('File uploaded', rv.content)

    def not_allowed(self):
        cookies = self.getSession()
        files = {'file': open('sampleUploads//hello.ps1')}
        r = requests.post(url,data=dataF,files=files,cookies=cookies)
        return r

    def test_not_allowed(self):
        rv = self.not_allowed()
        self.assertIn('For security reasons the file can be only in .doc .pdf or .txt formats', rv.content)

    def too_big(self):
        cookies = self.getSession()
        files = {'file': open('sampleUploads//toobig.pdf')}
        r = requests.post(url,data=dataF,files=files,cookies=cookies)
        return r

    def test_too_big(self):
        rv = self.too_big()
        self.assertIn('It cannot be bigger then 1 megabyte',rv.content)

    def doc(self):
        cookies = self.getSession()
        files = {'file': open('sampleUploads//Dora.docx')}
        #headers = {'content-type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'}
        r = requests.post(url,data=dataF,files=files,cookies=cookies)
        return r

    def test_upload_doc(self):
        rv = self.doc()
        self.assertIn('File uploaded', rv.content)

if __name__ == '__main__':
    unittest.main()
