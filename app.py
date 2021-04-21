#configuring Flask
import flask
from flask import Flask, render_template, request, redirect, url_for
from newsapi import NewsApiClient
import pandas as pd
import requests
from bs4 import BeautifulSoup
import requests
import joblib
#import classificationModel as m


app = Flask(__name__)

@app.route('/', methods=["GET", "POST"])

#function that renders index.html
def index(methods=["GET", "POST"]):

    url = "http://newsapi.org/v2/top-headlines?country=us&apiKey=f4767a5c003944e5bbe9b97170bb65c0"

    #get list of checked categories in filter menu
    categories = request.form.getlist('party')
    print('******************')
    print(categories)

    #if form hasn't been filled out yet
    if len(categories) == 0:
        right = True;
        left = True;
        neutral = True;

    #if user has checked boxes and submitted form
    if 'Right' in categories:
        right = True;

    if 'Left' in categories:
        left = True;

    if 'Neutral' in categories:
        neutral = True;

    return render_template('index.html', articles=getArticles(url), rightFilter = right, leftFilter = left, neutralFilter = neutral);

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

            #getting HTML content
            r1 = requests.get(articleURL)

            #saving HTML content to variable
            content = r1.content

            #set up soup variable to keep executing
            soup1 = BeautifulSoup(content, 'html5lib')

            #find all occurrences of paragraph tag
            articleParagraphs = soup1.find_all('p')
            #print("repLength: " + str(len(republicanParagraphs)))
            #print(republicanParagraphs)

            articleText = "";

            #add the filtered text to a republicanText string
            for p in articleParagraphs:
                articleText += p.get_text();

            #pass text into machine learning model
            #print(m.sentiment(articleText))

            #fix this syntax later!

            demOrRep = "rep";
            confidenceScore = 0.0;

            onSpectrum = getSpectrumString(demOrRep, confidenceScore);

            #demOrRep = m.sentiment[0]
            #confidenceScore = m.sentiment[1]

        except requests.exceptions.ConnectionError:
            requests.status_code = "Connection refused"
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

    if demOrRep == "rep":
        return rating + "Left";

    elif demOrRep == "dem":
        return rating + "Right";

    return "neutral";
