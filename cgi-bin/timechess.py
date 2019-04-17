# this is the human-readable website for timechess.  Note that we also have a
# REST interface to the same databases, but that's implemented in a separate
# Flask app.
#
# Code that is common to the two - such as code to connect to the database -
# is managed in timechess_common.py



import timechess_common

from flask import Flask, request, render_template, url_for, redirect, make_response, g
app = Flask(__name__)



app.route("/")
def index():
    TODO implement me



