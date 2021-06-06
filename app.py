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

# setting up connection to MySQL database
app = Flask(__name__)
app.config['MYSQL_HOST'] = 'mysql.2021.lakeside-cs.org'
app.config['MYSQL_USER'] = 'student2021'
app.config['MYSQL_PASSWORD'] = 'm545CS42021'
app.config['MYSQL_DB'] = '2021project'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

# function that gets all articles under a specific category from NewsApi
# parameter 'url': url that NewsApi uses to retrieve articles in category
# parameter 'category': category of articles being retrieved
# return 'dataSet': list of articles from specific NewsApi category
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

# function that assigns properties to NewsApi articles from a specific category
# parameter 'data': array with data from NewsApi for a specific article category
# parameter 'category': category of articles being assigned with properties
# return 'article_results': list of articles with full set of assigned properties
def getArticleResults(data, category):

    article_results = [];

    for i in range(len(data)):

        article_dict = {}
        article_dict['title'] = data[i]['title']
        article_dict['author'] = data[i]['author']
        article_dict['source'] = data[i]['source']
        article_dict['description'] = data[i]['description']
        article_dict['content'] = data[i]['content']
        article_dict['pub_date'] = data[i]['publishedAt']
        article_dict['url'] = data[i]['url']
        article_dict['photo_url'] = data[i]['urlToImage']
        sortedByModel = sortArticle(data[i]['url'])
        article_dict['politicalAssignment'] = sortedByModel[0]
        article_dict['onSpectrum'] = sortedByModel[1]
        article_dict['category'] = category
        article_results.append(article_dict)

    return article_results;

# function that determines an article's political assignment
# parameter 'articleURL': url to article that is being classified
# return: array containing a string with the political assignment of an article
# (left or right) and a string indicating where it falls on the political spectrum
def sortArticle(articleURL):

    #pass article into machine learning model
    articleResult = get_sentiment(articleURL)

    #get political assignment and confidence score
    demOrRep = articleResult[0];
    confidenceScore = articleResult[1];
    onSpectrum = getSpectrumString(demOrRep, confidenceScore);

    return [demOrRep, onSpectrum]

# function that constructs a string indicating where an article falls on
# the political spectrum
# parameter 'demOrRep': an article's political assignment (left or right)
# parameter 'confidenceScore': integer indicating certitude of
# machine learning algorithm about political assignment of article
# return: string indicating where an article falls on the political spectrum
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

# function that creates an array indicating whether user wants to filter
# by Right, Left, or Neutral political classifications
# parameter 'containsRight': boolean indicating whether or not user has checked 'Right' in filter form
# parameter 'containsLeft': boolean indicating whether or not user has checked 'Left' in filter form
# parameter 'containsNeutral': boolean indicating whether or not user has checked 'Neutral' in filter form
# return 'checkedBooleans': array of strings indicating whether or not user wants
# to filter by right-leaning, left-leaning, or neutral political classifications
def assignCheckedBooleans(containsRight, containsLeft, containsNeutral):

    checkedBooleans = ["True", "True", "True"];

    assignString(checkedBooleans, containsRight, 0)
    assignString(checkedBooleans, containsLeft, 1)
    assignString(checkedBooleans, containsNeutral, 2)

    return checkedBooleans;

# function that changes values in an array based on boolean passed in
# parameter 'boxesCheckedArray': array storing boxes checked in website filter form
# parameter 'containsBoolean': boolean indicating whether or not a
# box has been checked in website filter form
# parameter 'index': index of array to be altered
# returns: none
def assignString(boxesCheckedArray, containsBoolean, index):

    if not containsBoolean:
        boxesCheckedArray[index] = "False";

# function that creates an array that indicates which categories the user
# has checked off in the website filter form
# parameter 'categories': array with categories checked off by user
# return: array of booleans that indicates which categories the user
# has checked off in the website filter form
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

# function that determines political classification and location of an article
# on the political spectrum using an imported machine learning algorithm
# parameter 'url': url of article being classified
# return: array containing string with political classification of article and
# string with an integer value representing where article falls on political spectrum
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

# function that gets articles under a specific NewsApi category from MySQL database
# parameter 'category': category of articles being retrieved from database
# return: array with articles from chosen category currently in database
def getCategoryArticles(category):

    currentLetter = getCurrentLetter();
    cursor = mysql.connection.cursor()
    query = 'SELECT * FROM katherinesullivan_articles' + currentLetter + ' WHERE category=%s';
    queryVars = (category,);
    cursor.execute(query, queryVars);
    mysql.connection.commit();
    categoryArticles = cursor.fetchall();

    return categoryArticles;

# 2D Array with list of articles from each NewsApi category
articlesList = [[],[],[],[],[],[]];

# function that populates project MySQL database tables with fresh
# NewsApi article data when appropriate conditions are met
# parameters: none
# returns: none
def refreshDatabase():

    currentlyRefreshing = getCurrentlyRefreshing();

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

    # check if currentlyRefreshing value equals no
    if currentlyRefreshing == "No" and refreshTime == True:

        # if it does, set currentlyRefreshing value to yes
        setCurrentlyRefreshing("Yes")
        firstLetter = getCurrentLetter();
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

        tempArray = [];

        # store an array of top headline articles and their assigned properties
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
        setLastRefresh();

# function that switches MySQL database table that user interface is reading data from
# parameter 'currentLetter': current letter representing table user interface is reading data from
# returns: none
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

@app.route('/articleRefresh', methods=['POST'])

# function that is called by AJAX javascript function to trigger database refresh
# parameters: none
# returns: empty string
def articleRefresh():
    refreshDatabase();
    return "";

# function that reads MySQl database and gets current letter representing
# which MySQL database table user interface is reading to display articles
# parameters: none
# return: string with letter representing which table of data user interface is displaying
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

# function that reads MySQl database and gets last time at which data tables
# containing NewsApi data were cleared and repopulated
# parameters: none
# return: array containing last month, day, and hour at which data
# tables containing NewsApi data were cleared and repopulated
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

# function that gets current month, date, and hour
# parameters: none
# return: array containing strings representing current month, day, and hour
def getCurrentDateTime():
    # source: https://www.programiz.com/python-programming/datetime/current-datetime
    now = datetime.now()
    month = now.strftime("%m")
    date = now.strftime("%d")
    hour = now.strftime("%H")

    return [month, date, hour];

# function that sets last table refresh time as current time in MySQL database
# parameters: none
# returns: none
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

# function that reads MySQL database to determine if tables with
# article data are currently being cleared and repopulated to prevent interruptions
# parameters: none
# return: string indicating whether or not article data is currently
# being cleared or repopulated
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

# function that sets value in MySQL database that indicates if tables with article data
# are currently being cleared and repopulated to prevent interruptions in this process
# parameters: string value to be put in database
# returns: none
def setCurrentlyRefreshing(currentlyRefreshing):
    cursor = mysql.connection.cursor()
    # source: https://stackoverflow.com/questions/21258250/sql-how-to-update-only-first-row
    setCurrentlyRefreshing = 'UPDATE katherinesullivan_isRefreshing SET currentlyRefreshing=%s'
    queryVars = (currentlyRefreshing,)
    cursor.execute(setCurrentlyRefreshing, queryVars)
    mysql.connection.commit();

# function that determines which MySQL table the user interface
# should read from to display articles
# parameter 'letter': letter representing which table user interface
# should read from to display articles
# return: string with name of table the user interface
# should read from to display articles
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

    topHeadlineArticles = getCategoryArticles("topHeadlines")

    #get list of checked categories in filter menu
    #source: https://www.reddit.com/r/flask/comments/bz376w/how_do_i_get_checked_checkboxes_into_flask/
    categories = request.form.getlist('party')
    filters = getCategories(categories);

    searchBoxInput = request.form.get('searchText');
    clearMainRow = 'False';
    printEmptySearch = 'False';
    noSearchResults = 'False';
    searchResults = [];

    # if search box has input from the user
    if searchBoxInput is not None:

        currentLetter = getCurrentLetter();
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

        if len(searchResults) == 0:
            noSearchResults = 'True';

    checkedBooleans = assignCheckedBooleans(filters[0], filters[1], filters[2]);

    return render_template('index.html', noSearchResults=noSearchResults, searchResults=searchResults, printEmptySearch=printEmptySearch, clearMainRow=clearMainRow, articles=topHeadlineArticles, rightFilter = checkedBooleans[0], leftFilter = checkedBooleans[1], neutralFilter = checkedBooleans[2], arrayBools = checkedBooleans);

@app.route('/entertainment', methods=["GET", "POST"])

#function that renders entertainment.html
def entertainment(methods=["GET"]):

    entertainmentArticles = getCategoryArticles("entertainmentArticles")
    categories = request.form.getlist('party')
    filters = getCategories(categories);

    checkedBooleans = assignCheckedBooleans(filters[0], filters[1], filters[2]);

    return render_template('category.html', pageTitle = "ENTERTAINMENT", articles=entertainmentArticles, rightFilter = checkedBooleans[0], leftFilter = checkedBooleans[1], neutralFilter = checkedBooleans[2], arrayBools = checkedBooleans);

@app.route('/sports', methods=["GET", "POST"])

#function that renders sports.html
def sports(methods=["GET"]):

    sportsArticles = getCategoryArticles("sportsArticles")
    categories = request.form.getlist('party')
    filters = getCategories(categories);

    checkedBooleans = assignCheckedBooleans(filters[0], filters[1], filters[2]);

    return render_template('category.html', pageTitle = "SPORTS", articles=sportsArticles, rightFilter = checkedBooleans[0], leftFilter = checkedBooleans[1], neutralFilter = checkedBooleans[2], arrayBools = checkedBooleans);


@app.route('/science', methods=["GET", "POST"])

#function that renders science.html
def science(methods=["GET"]):

    scienceArticles = getCategoryArticles("scienceArticles")
    categories = request.form.getlist('party')
    filters = getCategories(categories);

    checkedBooleans = assignCheckedBooleans(filters[0], filters[1], filters[2]);

    return render_template('category.html', pageTitle = "SCIENCE", articles=scienceArticles, rightFilter = checkedBooleans[0], leftFilter = checkedBooleans[1], neutralFilter = checkedBooleans[2], arrayBools = checkedBooleans);


@app.route('/business', methods=["GET", "POST"])

#function that renders business.html
def business(methods=["GET"]):

    businessArticles = getCategoryArticles("businessArticles")
    categories = request.form.getlist('party')
    filters = getCategories(categories);

    checkedBooleans = assignCheckedBooleans(filters[0], filters[1], filters[2]);

    return render_template('category.html', pageTitle = "BUSINESS",  articles=businessArticles, rightFilter = checkedBooleans[0], leftFilter = checkedBooleans[1], neutralFilter = checkedBooleans[2], arrayBools = checkedBooleans);


@app.route('/health', methods=["GET", "POST"])

#function that renders health.html
def health(methods=["GET"]):

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

        #check whether or not user input is a valid url
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

# function that cleans up formatting in article text content
# parameter 'article': text content of article being cleaned
# return: string with cleaned text content of an article
def clean(article):

    cleaned_article = re.sub('[\n\t,]', ' ', article)
    cleaned_article = cleaned_article.replace('Advertisement', ' ')
    return cleaned_article

# function that gets text content of an article
# parameter 'url': url to article whose text content is being retrieved
# return: string with text content of article
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
