Recenseo.es...
===========

...is a simple application which allows writers to share their articles, drafts, books etc with others. 
More importantly it allows authors to get a review from fellow writers. 
The idea is simple, you can publish your text and get a fast review from other users. 
Reviews are not meant to be a form of promotion, they are closer to feedback that one can get in a writers club. 
The project is to be deployed at the domain [http://www.recenseo.es](recenseo.es). 

The app is written in Flask 0.9, with MySQL as the database engine. SQL Alchemy's expression language,
not ORM is used as means of communicating with db, at times however queries are written in plain mysql,
without mediation of alchemic abstraction layer. As for the front end, design involves heavily customized version of Twitter
Bootstrap 2.3. 

Architecture
------------
Loosely inspired by MVC pattern, Flask gives a lot of flexibility, it doesn't enforce any particular
design pattern, nevertheless the project conforms with MVC guidelines. 

Structure
---------
The project has following structure

    ├── run.py   # launches app 
    ├── runtest.sh # runs all tests and cleans up after them
    ├── src
    │   ├── flaskr.py # main controller
    │   ├── forms.py  # self-explanatory
    │   ├── modele.py # data representations, including schemas for each table and queries
    │   ├── static
    │   │   ├── css
    │   │   ├── img
    │   │   └── js
    │   └── templates # each folder contains templates concerning one functionality
    │       ├── review
    │       ├── reviewRequest
    │       └── users
    ├── tests # all tests are placed here
    ├── utilities # some scripts for manipulating database
    └── uwsg_config.ini # needed for deployment with nginx

License 
-------
MIT license
