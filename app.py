import flask
from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
from newsapi import NewsApiClient
import pandas as pd
import requests
from bs4 import BeautifulSoup
import requests
import joblib
import betterModel as m
import numpy as np
import newspaper
from newspaper import Article
from newspaper import Config
from datetime import datetime
import string
import re
import validators
import threading

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'mysql.2021.lakeside-cs.org'
app.config['MYSQL_USER'] = 'student2021'
app.config['MYSQL_PASSWORD'] = 'm545CS42021'
app.config['MYSQL_DB'] = '2021project'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

def getArticles(url, category):

    try:
        open_bbc_page = requests.get(url).json()
        articles = open_bbc_page["articles"]
        results = []

        dataSet = getArticleResults(articles, category);

    #source: https://stackoverflow.com/questions/23013220/max-retries-exceeded-with-url-in-requests
    except requests.exceptions.ConnectionError:
        requests.status_code = "Connection refused";
        dataSet = "error: unable to fetch dataset";

    return dataSet;

def getArticleResults(file, category):

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
        article_dict['category'] = category
        article_results.append(article_dict)

    return article_results;

def sortArticle(articleURL):

    #pass article into machine learning model
    articleResult = get_sentiment(articleURL)

    #get political assignment and confidence score
    demOrRep = articleResult[0];
    print("dem or rep: " + demOrRep)

    confidenceScore = articleResult[1];
    print("confidence score: " + str(confidenceScore))

    onSpectrum = getSpectrumString(demOrRep, confidenceScore);

    return [demOrRep, onSpectrum]

def getSpectrumString(demOrRep, confidenceScore):

    if confidenceScore != "n/a":

        if confidenceScore > 0 and confidenceScore <= 0.33333333333:
            rating = "least";

        elif confidenceScore > 0.33333333333 and confidenceScore <= 0.66666666666:
            rating = "moderate"

        elif confidenceScore > 0.66666666666 and confidenceScore <= 1.0:
            rating = "far"

        elif confidenceScore == 0:
            rating = "neutral";

        if demOrRep == "right" and confidenceScore == 0:
            return rating;
        elif demOrRep == "left" and confidenceScore == 0:
            return rating;
        elif demOrRep == "right":
            return rating + "Right";
        elif demOrRep == "left":
            return rating + "Left";

    return "neutral";

def assignCheckedBooleans(containsRight, containsLeft, containsNeutral):

    checkedBooleans = ["True", "True", "True"];

    assignString(checkedBooleans, containsRight, 0)
    assignString(checkedBooleans, containsLeft, 1)
    assignString(checkedBooleans, containsNeutral, 2)

    return checkedBooleans;

def assignString(boxesCheckedArray, containsBoolean, index):

    if not containsBoolean:
        boxesCheckedArray[index] = "False";

def get_sentiment(url):

    try:
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
        config = Config()
        config.browser_user_agent = user_agent
        config.request_timeout = 10
        article = Article(url, config=config)
        article.download()
        article.parse()
        article_text = article.text
        sentiment = m.sentiment(article_text)
        if len(sentiment) == 0:
            sentiment = ['n/a', 'n/a']
        return sentiment

    except newspaper.article.ArticleException:
        return ['n/a', 'n/a']

    return "error!";

def getCategories(categories):

    #if filter form hasn't been filled out yet
    if len(categories) == 0:
        containsRight = "True";
        containsLeft = "True";
        containsNeutral = "True";

    #if filter form has been filled out by user
    else:
        #source: https://stackoverflow.com/questions/7571635/fastest-way-to-check-if-a-value-exists-in-a-list
        containsRight = "Right" in categories;
        containsLeft = "Left" in categories;
        containsNeutral = "Neutral" in categories;

    return [containsRight, containsLeft, containsNeutral]

# function that gets articles from a specific category fromt the database
def getCategoryArticles(category):

    currentLetter = getCurrentLetter();
    print("current letter: " + currentLetter);
    cursor = mysql.connection.cursor()
    query = 'SELECT * FROM katherinesullivan_articles' + currentLetter + ' WHERE category=%s';
    queryVars = (category,);
    cursor.execute(query, queryVars);
    mysql.connection.commit();
    categoryArticles = cursor.fetchall();

    return categoryArticles;

# 2D Array with list of articles
articlesList = [[],[],[],[],[],[]];

# function that refreshes database
def refreshDatabase():

    currentlyRefreshing = getCurrentlyRefreshing();
    print("currently refreshing: " + currentlyRefreshing);

    now = getCurrentDateTime();
    month = now[0];
    date = now[1];
    hour = now[2];

    lastRefresh = getLastRefresh();
    lastRefreshMonth = lastRefresh[0];
    lastRefreshDate = lastRefresh[1];
    lastRefreshHour = lastRefresh[2];

    refreshTime = False;

    if month != lastRefreshMonth or date != lastRefreshDate or hour != lastRefreshHour:
        refreshTime = True;
        print("time to refresh the database!")

    # check if currentlyRefreshing value equals no
    if currentlyRefreshing == "No" and refreshTime == True:

        # if it does, set currentlyRefreshing value to yes
        setCurrentlyRefreshing("Yes")
        print("set currently refreshing to yes");

        firstLetter = getCurrentLetter();
        print("current letter: " + firstLetter);
        currentLetter = "";

        if firstLetter == "A":
            currentLetter = "B";
        else:
            currentLetter = "A";

        cursor = mysql.connection.cursor()
        query = 'SELECT * FROM katherinesullivan_articles' + currentLetter;
        cursor.execute(query)
        mysql.connection.commit()
        data = list(cursor.fetchall())
        length = len(data)
        if(length>0):
            for i in data:
                cursor = mysql.connection.cursor()
                query = 'DELETE FROM katherinesullivan_articles' + currentLetter + ' ORDER BY title LIMIT 1';
                cursor.execute(query)
                mysql.connection.commit()
                print("article deleted")

        tempArray = [];

        # #store an array of top headline articles and their assigned properties
        tempArray.extend(getArticles("http://newsapi.org/v2/top-headlines?country=us&apiKey=f4767a5c003944e5bbe9b97170bb65c0", "topHeadlines"))

        # store an array of entertainment articles and their assigned properties
        tempArray.extend(getArticles("http://newsapi.org/v2/top-headlines?country=us&category=entertainment&apiKey=f4767a5c003944e5bbe9b97170bb65c0", "entertainmentArticles"))

        # store an array of sports articles and their assigned properties
        tempArray.extend(getArticles("http://newsapi.org/v2/top-headlines?country=us&category=sports&apiKey=f4767a5c003944e5bbe9b97170bb65c0", "sportsArticles"))

        # store an array of business articles and their assigned properties
        tempArray.extend(getArticles("http://newsapi.org/v2/top-headlines?country=us&category=business&apiKey=f4767a5c003944e5bbe9b97170bb65c0", "businessArticles"))

        # store an array of science articles and their assigned properties
        tempArray.extend(getArticles("http://newsapi.org/v2/top-headlines?country=us&category=science&apiKey=f4767a5c003944e5bbe9b97170bb65c0", "scienceArticles"))

        # store an array of health articles and their assigned properties
        tempArray.extend(getArticles("http://newsapi.org/v2/top-headlines?country=us&category=health&apiKey=f4767a5c003944e5bbe9b97170bb65c0", "healthArticles"))

        articlesList = tempArray
        for article in tempArray:
            cur = mysql.connection.cursor()
            title = article['title']
            url = article['url']
            imageURL = article['photo_url']
            if imageURL is None:
                imageURL = "blank"
            sentiment = article['politicalAssignment']
            confidence = article['onSpectrum']
            category = article['category']
            query = 'INSERT INTO katherinesullivan_articles' + currentLetter + ' (title, url, imageURL, category, leaning, onSpectrum) VALUES (%s, %s, %s, %s, %s, %s)';
            queryVars = (title, url, imageURL, category, sentiment, confidence,)
            cur.execute(query, queryVars);
            mysql.connection.commit()

        switchLetter(firstLetter);
        setCurrentlyRefreshing("No")
        print("set currently refreshing to no");
        setLastRefresh();

def switchLetter(currentLetter):

    newLetter = "";

    if currentLetter == "A":
        newLetter = "B";
    else:
        newLetter = "A";

    cursor = mysql.connection.cursor()
    # source: https://stackoverflow.com/questions/21258250/sql-how-to-update-only-first-row
    switchCurrentLetter = 'UPDATE katherinesullivan_AorB SET tableLetter=%s'
    queryVars = (newLetter,)
    cursor.execute(switchCurrentLetter, queryVars)
    mysql.connection.commit();

    return "";

@app.route('/articleRefresh', methods=['POST'])

def articleRefresh():

    refreshDatabase()
    return "Done";

def getCurrentLetter():

        cursor = mysql.connection.cursor()
        # source: https://stackoverflow.com/questions/3217217/grabbing-first-row-in-a-mysql-query-only
        getCurrentLetter = 'SELECT * FROM katherinesullivan_AorB LIMIT 1'
        cursor.execute(getCurrentLetter)
        mysql.connection.commit();
        currentLetter = cursor.fetchall();

        if len(currentLetter) != 0:
            if currentLetter[0]['tableLetter'] == "A":
                return "A";

        return "B";

def getLastRefresh():

        cursor = mysql.connection.cursor()
        # source: https://stackoverflow.com/questions/3217217/grabbing-first-row-in-a-mysql-query-only
        getCurrentlyRefreshing = 'SELECT * FROM katherinesullivan_refreshTime LIMIT 1'
        cursor.execute(getCurrentlyRefreshing)
        mysql.connection.commit();
        currentlyRefreshing = cursor.fetchall();

        if len(currentlyRefreshing) != 0:
            month = currentlyRefreshing[0]['month']
            day = currentlyRefreshing[0]['day']
            hour = currentlyRefreshing[0]['hour']
            return [month, day, hour];

        return ['1', '1', '1']

def getCurrentDateTime():
    # source: https://www.programiz.com/python-programming/datetime/current-datetime
    now = datetime.now()
    month = now.strftime("%m")
    date = now.strftime("%d")
    hour = now.strftime("%H")

    return [month, date, hour];


def setLastRefresh():

    now = getCurrentDateTime();
    month = now[0];
    date = now[1];
    hour = now[2];

    cursor = mysql.connection.cursor()
    # source: https://stackoverflow.com/questions/21258250/sql-how-to-update-only-first-row
    setLastRefresh = 'UPDATE katherinesullivan_refreshTime SET month=%s, day=%s, hour=%s'
    queryVars = (month, date, hour,)
    cursor.execute(setLastRefresh, queryVars)
    mysql.connection.commit();

    return "";


def getCurrentlyRefreshing():

        cursor = mysql.connection.cursor()
        # source: https://stackoverflow.com/questions/3217217/grabbing-first-row-in-a-mysql-query-only
        getCurrentlyRefreshing = 'SELECT * FROM katherinesullivan_isRefreshing LIMIT 1'
        cursor.execute(getCurrentlyRefreshing)
        mysql.connection.commit();
        currentlyRefreshing = cursor.fetchall();

        if len(currentlyRefreshing) != 0:
            if currentlyRefreshing[0]['currentlyRefreshing'] == "Yes":
                return "Yes";
            else:
                return "No";

def setCurrentlyRefreshing(currentlyRefreshing):
    cursor = mysql.connection.cursor()
    # source: https://stackoverflow.com/questions/21258250/sql-how-to-update-only-first-row
    setCurrentlyRefreshing = 'UPDATE katherinesullivan_isRefreshing SET currentlyRefreshing=%s'
    queryVars = (currentlyRefreshing,)
    cursor.execute(setCurrentlyRefreshing, queryVars)
    mysql.connection.commit();

    return "";

def getCurrentTable(letter):

    if letter == "A":
        return "katherinesullivan_articlesA";
    elif letter == "B":
        return "katherinesullivan_articlesB";

    return "invalid letter input"

## @app.route functions start here ##

@app.route('/', methods=["GET", "POST"])

#function that renders index.html
def index(methods=["GET", "POST"]):

    currentLetter = getCurrentLetter();
    print("current letter: " + currentLetter);

    topHeadlineArticles = getCategoryArticles("topHeadlines")

    #get list of checked categories in filter menu
    #source: https://www.reddit.com/r/flask/comments/bz376w/how_do_i_get_checked_checkboxes_into_flask/
    categories = request.form.getlist('party')
    filters = getCategories(categories);

    searchBoxInput = request.form.get('searchText');
    clearMainRow = 'False';
    printEmptySearch = 'False';
    searchResults = [];

    if searchBoxInput is not None:

        clearMainRow = 'True';

        #source: https://www.tutorialspoint.com/How-to-convert-a-string-to-a-list-of-words-in-python
        searchBoxInputWords = searchBoxInput.split();

        counter = 0;
        for i in searchBoxInputWords:
            counter += 1;

        if searchBoxInput == '':
            printEmptySearch = 'True';

        # empty out array with search results
        searchResults = [];

        cursor = mysql.connection.cursor()
        query = 'SELECT * FROM katherinesullivan_articles' + currentLetter;
        cursor.execute(query);
        mysql.connection.commit();
        articlesData = cursor.fetchall();

        for article in articlesData:

            for word in searchBoxInputWords:

                # get the article title (lowercase)
                # source: https://www.programiz.com/python-programming/methods/string/lower
                title = article['title'].lower();

                # if title contains search word (lowercase)
                if word.lower() in title:

                    notDuplicate = True;

                    # if search results already exist
                    if len(searchResults) != 0:
                        for result in searchResults:
                            # make sure that title of current article does
                            # not match any titles currently in searchResults
                            if result['title'] == article['title']:
                                notDuplicate = False;

                    if notDuplicate:
                        searchResults.append(article);

    checkedBooleans = assignCheckedBooleans(filters[0], filters[1], filters[2]);

    return render_template('index.html', searchResults=searchResults, printEmptySearch=printEmptySearch, clearMainRow=clearMainRow, articles=topHeadlineArticles, rightFilter = checkedBooleans[0], leftFilter = checkedBooleans[1], neutralFilter = checkedBooleans[2], arrayBools = checkedBooleans);

@app.route('/entertainment', methods=["GET", "POST"])

#function that renders entertainment.html
def entertainment(methods=["GET"]):

    currentLetter = getCurrentLetter();
    print("current letter: " + currentLetter);

    entertainmentArticles = getCategoryArticles("entertainmentArticles")
    categories = request.form.getlist('party')
    filters = getCategories(categories);

    checkedBooleans = assignCheckedBooleans(filters[0], filters[1], filters[2]);

    return render_template('category.html', pageTitle = "ENTERTAINMENT", articles=entertainmentArticles, rightFilter = checkedBooleans[0], leftFilter = checkedBooleans[1], neutralFilter = checkedBooleans[2], arrayBools = checkedBooleans);

@app.route('/sports', methods=["GET", "POST"])

#function that renders sports.html
def sports(methods=["GET"]):

    currentLetter = getCurrentLetter();
    print("current letter: " + currentLetter);

    sportsArticles = getCategoryArticles("sportsArticles")
    categories = request.form.getlist('party')
    filters = getCategories(categories);

    checkedBooleans = assignCheckedBooleans(filters[0], filters[1], filters[2]);

    return render_template('category.html', pageTitle = "SPORTS", articles=sportsArticles, rightFilter = checkedBooleans[0], leftFilter = checkedBooleans[1], neutralFilter = checkedBooleans[2], arrayBools = checkedBooleans);


@app.route('/science', methods=["GET", "POST"])

#function that renders science.html
def science(methods=["GET"]):

    currentLetter = getCurrentLetter();
    print("current letter: " + currentLetter);

    scienceArticles = getCategoryArticles("scienceArticles")
    categories = request.form.getlist('party')
    filters = getCategories(categories);

    checkedBooleans = assignCheckedBooleans(filters[0], filters[1], filters[2]);

    return render_template('category.html', pageTitle = "SCIENCE", articles=scienceArticles, rightFilter = checkedBooleans[0], leftFilter = checkedBooleans[1], neutralFilter = checkedBooleans[2], arrayBools = checkedBooleans);


@app.route('/business', methods=["GET", "POST"])

#function that renders business.html
def business(methods=["GET"]):

    currentLetter = getCurrentLetter();
    print("current letter: " + currentLetter);

    businessArticles = getCategoryArticles("businessArticles")
    categories = request.form.getlist('party')
    filters = getCategories(categories);

    checkedBooleans = assignCheckedBooleans(filters[0], filters[1], filters[2]);

    return render_template('category.html', pageTitle = "BUSINESS",  articles=businessArticles, rightFilter = checkedBooleans[0], leftFilter = checkedBooleans[1], neutralFilter = checkedBooleans[2], arrayBools = checkedBooleans);


@app.route('/health', methods=["GET", "POST"])

#function that renders health.html
def health(methods=["GET"]):

    currentLetter = getCurrentLetter();
    print("current letter: " + currentLetter);

    healthArticles = getCategoryArticles("healthArticles")
    categories = request.form.getlist('party')
    filters = getCategories(categories);

    checkedBooleans = assignCheckedBooleans(filters[0], filters[1], filters[2]);

    return render_template('category.html', pageTitle = "HEALTH",  articles=healthArticles, rightFilter = checkedBooleans[0], leftFilter = checkedBooleans[1], neutralFilter = checkedBooleans[2], arrayBools = checkedBooleans);

@app.route('/classify', methods=["GET", "POST"])

#function that renders classify.html
def classify(methods=["GET", "POST"]):

    articleURLInput = request.form.get('url')
    spectrumImagePath = "empty";
    politicalAssignment = "none";
    inputValid = "no";

    if articleURLInput is not None:

        #check whether it is a valid url
        #source: https://www.codespeedy.com/check-if-a-string-is-a-valid-url-or-not-in-python/#:~:text=To%20check%20whether%20the%20string,%E2%80%A6)%20if%20URL%20is%20invalid.
        validURL = validators.url(articleURLInput)

        if validURL == True:
            inputValid = "yes";
            articleResults = sortArticle(articleURLInput);
            spectrumImagePath = articleResults[1];
            politicalAssignment = articleResults[0];

    return render_template('classify.html', inputValid=inputValid, spectrumImagePath=spectrumImagePath, politicalAssignment=politicalAssignment);

@app.route('/instructions', methods=["GET", "POST"])

#function that renders instructions.html
def instructions(methods=["POST"]):
    return render_template('instructions.html')

@app.route('/contact', methods=["GET", "POST"])

#function that renders contact.html
def contact(methods=["POST"]):
    return render_template('contact.html')

def clean(article):

    cleaned_article = re.sub('[\n\t,]', ' ', article)
    cleaned_article = cleaned_article.replace('Advertisement', ' ')
    return cleaned_article

def get_text(url):

    article_text = ''
    #source: https://stackoverflow.com/questions/56678732/how-to-fix-newspaper3k-403-client-error-for-certain-urls
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36 Edg/89.0.774.77'
    config = Config()
    config.browser_user_agent = user_agent
    article = Article(url, config=config)
    article.download()
    article.parse()
    article_text = article.text

    if article_text == '':
        print("Could not locate article body")
    else:
        print("Got the article body!")

    cleaned_article_text = clean(article_text)

    return cleaned_article_text
