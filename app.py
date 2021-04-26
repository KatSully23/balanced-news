#configuring Flask
import flask
from flask import Flask, render_template, request, redirect, url_for
from newsapi import NewsApiClient
import pandas as pd
import requests
from bs4 import BeautifulSoup
import requests
import joblib
import nltkModel as m
import numpy as np
from newspaper import Article
from newspaper import Config
import string
import re

app = Flask(__name__)

@app.route('/', methods=["GET", "POST"])

#function that renders index.html
def index(methods=["GET", "POST"]):

    url = "http://newsapi.org/v2/top-headlines?country=us&apiKey=f4767a5c003944e5bbe9b97170bb65c0"

    #get list of checked categories in filter menu
    #source: https://www.reddit.com/r/flask/comments/bz376w/how_do_i_get_checked_checkboxes_into_flask/
    categories = request.form.getlist('party')
    print('******************')
    print(categories)

    #if form hasn't been filled out yet
    if len(categories) == 0:
        containsRight = "True";
        containsLeft = "True";
        containsNeutral = "True";
    #if form has been filled out by user
    else:
        #source: https://stackoverflow.com/questions/7571635/fastest-way-to-check-if-a-value-exists-in-a-list
        containsRight = "Right" in categories;
        containsLeft = "Left" in categories;
        containsNeutral = "Neutral" in categories;

    checkedBooleans = assignCheckedBooleans(containsRight, containsLeft, containsNeutral);

    return render_template('index.html', articles=getArticles(url), rightFilter = checkedBooleans[0], leftFilter = checkedBooleans[1], neutralFilter = checkedBooleans[2], arrayBools = checkedBooleans);

@app.route('/entertainment', methods=["GET", "POST"])

#function that renders entertainment.html
def entertainment(methods=["GET"]):
    url = "http://newsapi.org/v2/top-headlines?country=us&category=entertainment&apiKey=77ab5895b882445b8796fa78919f022d"
    return render_template('entertainment.html', articles=getArticles(url));

@app.route('/sports', methods=["GET", "POST"])

#function that renders sports.html
def sports(methods=["GET"]):
    url = "http://newsapi.org/v2/top-headlines?country=us&category=sports&apiKey=77ab5895b882445b8796fa78919f022d"
    return render_template('sports.html', articles=getArticles(url));

@app.route('/science', methods=["GET", "POST"])

#function that renders science.html
def science(methods=["GET"]):
    url = "http://newsapi.org/v2/top-headlines?country=us&category=science&apiKey=77ab5895b882445b8796fa78919f022d"
    return render_template('science.html', articles=getArticles(url));

@app.route('/business', methods=["GET", "POST"])

#function that renders contact.html
def business(methods=["GET"]):
    url = "http://newsapi.org/v2/top-headlines?country=us&category=business&apiKey=77ab5895b882445b8796fa78919f022d"
    return render_template('business.html', articles=getArticles(url));

@app.route('/health', methods=["GET", "POST"])

#function that renders contact.html
def health(methods=["GET"]):
    url = "http://newsapi.org/v2/top-headlines?country=us&category=health&apiKey=77ab5895b882445b8796fa78919f022d"
    return render_template('health.html', articles=getArticles(url));

@app.route('/mldemo', methods=["GET", "POST"])

#temporary
def mldemo():
    if request.method == 'GET':
        prediction = request.args.get('prediction')
        return render_template('machinelearningdemo.html', prediction=prediction)
    else:
        title = request.values.get("title")
        model = joblib.load('demo_model.joblib')
        target_names = ['CNN', 'Breitbart', 'New York Times']
        prediction = target_names[model.predict([title])[0]]
        return redirect(url_for('mldemo', prediction=prediction))


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

    try:
        open_bbc_page = requests.get(url).json()
        articles = open_bbc_page["articles"]
        results = []

        dataSet = get_articles(articles);

        #for i in range(len(dataSet)):
            #print("")
            #print("***********************")
            #print(i + 1, dataSet[i])

        imgURL = dataSet[15]['photo_url'];
        articleName = dataSet[15]['title'];
        articleAuthor = dataSet[15]['author'];
        articleContent = dataSet[15]['content'];
        articleURL = dataSet[15]['url'];

    #source: https://stackoverflow.com/questions/23013220/max-retries-exceeded-with-url-in-requests
    except requests.exceptions.ConnectionError:
        requests.status_code = "Connection refused";
        dataSet = "error: unable to fetch dataset";
        print(dataSet)

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

        sortedByModel = sortArticle(file[i]['url'])
        article_dict['politicalAssignment'] = sortedByModel[0]
        article_dict['onSpectrum'] = sortedByModel[1]

        article_results.append(article_dict)

    return article_results;

def sortArticle(articleURL):

        try:

            #BEAUTIFUL SOUP WEB SCRAPING CODE
            #getting HTML content
            #r1 = requests.get(articleURL)
            #saving HTML content to variable
            #content = r1.content
            #set up soup variable to keep executing
            #soup1 = BeautifulSoup(content, 'html5lib')
            #find all occurrences of paragraph tag
            #articleParagraphs = soup1.find_all('p')
            #print("repLength: " + str(len(republicanParagraphs)))
            #print(republicanParagraphs)
            #articleText = "";
            #add the filtered text to a republicanText string
            #for p in articleParagraphs:
                #articleText += p.get_text();

            #pass article into machine learning model
            articleResult = get_sentiment(articleURL)

            #get party and confidence score
            demOrRep = articleResult[0];
            print("dem or rep: " + demOrRep)

            confidenceScore = articleResult[1];
            print("confidenceScore: " + str(confidenceScore))

            #demOrRep = "rep";
            #confidenceScore = 0.0;

            onSpectrum = getSpectrumString(demOrRep, confidenceScore);

        #source: https://stackoverflow.com/questions/23013220/max-retries-exceeded-with-url-in-requests
        except requests.exceptions.ConnectionError:
            requests.status_code = "Connection refused"
            print("error: connection refused")
            return['n/a', 'n/a']

        return [demOrRep, onSpectrum]

def getSpectrumString(demOrRep, confidenceScore):

    if confidenceScore >= 0 and confidenceScore <= 0.33333333333:
        rating = "least";

    elif confidenceScore > 0.33333333333 and confidenceScore <= 0.66666666666:
        rating = "moderate"

    elif confidenceScore > 0.66666666666 and confidenceScore <= 1.0:
        rating = "far"

    elif confidenceScore == 0:
        rating = "neutral";

    else:
        print("error: confidence score out of range");

    if demOrRep == "right":
        return rating + "Right";

    elif demOrRep == "left":
        return rating + "Left";

    return "neutral";

def assignCheckedBooleans(containsRight, containsLeft, containsNeutral):

    checkedBooleans = ["True", "True", "True"];

    assignString(checkedBooleans, containsRight, 0)
    assignString(checkedBooleans, containsLeft, 1)
    assignString(checkedBooleans, containsNeutral, 2)

    print("checked booleans array" + str(checkedBooleans));
    return checkedBooleans;


def assignString(boxesCheckedArray, containsBoolean, index):

    if not containsBoolean:
        boxesCheckedArray[index] = "False";

#web scraping code

def get_sentiment(url):

    try:
        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
        config = Config()
        config.browser_user_agent = user_agent
        article = Article(url, config=config)
        article.download()
        article.parse()
        article_text = article.text
        return m.sentiment(article_text)

    except requests.exceptions.ConnectionError:
        requests.status_code = "Connection refused"
        print("error: connection refused")
        return['n/a', 'n/a']

def clean(article):

    cleaned_article = re.sub('[\n\t,]', ' ', article)
    cleaned_article = cleaned_article.replace('Advertisement', ' ')
    return cleaned_article

def get_text(url):

    article_text = ''
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36 Edg/89.0.774.77'
    config = Config()
    config.browser_user_agent = user_agent
    article = Article(url, config=config)
    article.download()
    article.parse()
    article_text = article.text

    if article_text == '':
        print("Could not locate article body")
        #raise Exception("Could not locate article body")
    else:
        print("Got the article body!")

    cleaned_article_text = clean(article_text)
    return cleaned_article_text
