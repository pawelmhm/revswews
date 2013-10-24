"""
A script to identify and reproduce
SQL server gone error
"""

from sqlalchemy import create_engine
from sqlalchemy import exc
from help_connect import ping_connection

e = create_engine("mysql://root:diogenes@localhost/flask")
c1 = e.connect()
c2 = e.connect()
c3 = e.connect()

c1.close()
c2.close()
c3.close()

print "Restart server now"
what = raw_input()
for i in xrange(10):
    c = e.connect()
    try:
        c.execute("SELECT * FROM users where username='admin'").fetchone()
        #print "ok"
    except Exception as exp:
         print "Exception raised {e}, connection number {n}".format(e=type(exp),n=i)
    c.close()
