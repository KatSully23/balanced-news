#configuring Flask
import flask
from flask import Flask, render_template, request
app = Flask(__name__)

@app.route('/', methods=["GET", "POST"])

#function that renders index.html
def index(methods=["GET"]):
    return render_template('index.html');

@app.route('/us', methods=["GET", "POST"])

#function that renders speakers.html
def us(methods=["GET"]):
        return render_template('us.html')

@app.route('/world', methods=["GET", "POST"])
#function that renders secretSpeakers.html
def secretSpeakers():
    return render_template('world.html');


@app.route('/business', methods=["GET", "POST"])

#function that renders contact.html
def business(methods=["POST"]):
    return render_template('business.html')

@app.route('/about', methods=["GET", "POST"])

#function that renders contact.html
def about(methods=["POST"]):
    return render_template('about.html')

@app.route('/instructions', methods=["GET", "POST"])

#function that renders contact.html
def instructions(methods=["POST"]):
    return render_template('instructions.html')

@app.route('/contact', methods=["GET", "POST"])

#function that renders contact.html
def contact(methods=["POST"]):
    return render_template('contact.html')
