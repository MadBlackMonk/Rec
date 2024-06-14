#RECORDING PROJECT
#
#IMPORTS
#
#import flask to python project
from flask import Flask, render_template
#
###################################################
#
#Create flask instance
rec = Flask(__name__)
#
###################################################
#
#ROUTES AND FUCTIONS
@rec.route('/home')
#1 : localhost:5000/home
def home():
	return render_template("home.html")
###################################################
#
@rec.route('/signin')
#2 :localhost:5000/signin
def signin():
	return render_template("signin.html")
###################################################
#
@rec.route('/signup')
#3 :localhost:5000/signup
def signup():
	return render_template("signup.html") 
###################################################
#
@rec.route('/dash')
#4 :localhost:5000/dash
def dash():
	return render_template("dash.html") 
###################################################
###################################################
#CREATE ERROR PAGES
#INVALID URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404
#
#INTERNAL SERVER ERROR
@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500
###################################################
###################################################