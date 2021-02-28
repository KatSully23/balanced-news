#configuring Flask
import flask
from flask import Flask, render_template, request
from newsapi import NewsApiClient
import requests


app = Flask(__name__)

@app.route('/', methods=["GET", "POST"])

#function that renders index.html
def index(methods=["GET"]):
    return render_template('index.html');

@app.route('/us', methods=["GET", "POST"])

#function that renders speakers.html
def us(methods=["GET"]):
    url = "http://newsapi.org/v2/top-headlines?country=us&apiKey=f4767a5c003944e5bbe9b97170bb65c0"
    return render_template('us.html', articles=getArticles(url));

@app.route('/world', methods=["GET", "POST"])
#function that renders secretSpeakers.html
def world():
    url = "http://newsapi.org/v2/top-headlines?apiKey=50b2c8ff5033428fb2ee50645ced43c9"
    return render_template('world.html', articles=getArticles(url));

@app.route('/business', methods=["GET", "POST"])

#function that renders contact.html
def business(methods=["GET"]):
    url = "http://newsapi.org/v2/top-headlines?country=us&category=business&apiKey=77ab5895b882445b8796fa78919f022d"
    return render_template('business.html', articles=getArticles(url));


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

def getArticles(url):
    open_bbc_page = requests.get(url).json()
    articles = open_bbc_page["articles"]
    results = []

    dataSet = get_articles(articles);

    for i in range(len(dataSet)):
        print("")
        print("***********************")
        print(i + 1, dataSet[i])

    imgURL = dataSet[15]['photo_url'];
    articleName = dataSet[15]['title'];
    articleAuthor = dataSet[15]['author'];
    articleContent = dataSet[15]['content'];
    articleURL = dataSet[15]['url'];

    return dataSet;

def get_articles(file):

    article_results = [];

    for i in range(len(file)):
        article_dict = {}
        article_dict['title'] = file[i]['title']
        article_dict['author'] = file[i]['author']
        article_dict['source'] = file[i]['source']
        article_dict['description'] = file[i]['description']
        article_dict['content'] = file[i]['content']
        article_dict['pub_date'] = file[i]['publishedAt']
        article_dict['url'] = file[i]['url']
        article_dict['photo_url'] = file[i]['urlToImage']

        article_results.append(article_dict)

    return article_results;
