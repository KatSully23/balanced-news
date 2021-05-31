#configuring Flask
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
        #figure out what this code does!
        open_bbc_page = requests.get(url).json()
        articles = open_bbc_page["articles"]
        results = []

        dataSet = getArticleResults(articles, category);

    except KeyError as e:
        print("you just got a key error")
        dataSet = "error: unable to fetch dataset due to key error"

    #source: https://stackoverflow.com/questions/23013220/max-retries-exceeded-with-url-in-requests
    except requests.exceptions.ConnectionError:
        requests.status_code = "Connection refused";
        dataSet = "error: unable to fetch dataset";
        print(dataSet)

    return dataSet;

def getArticleResults(file, category):

    article_results = [];

    for i in range(len(file)):

        #try:
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

        #source: https://stackoverflow.com/questions/23013220/max-retries-exceeded-with-url-in-requests
        #except requests.exceptions.ConnectionError:
            #requests.status_code = "Connection refused"
            #print("error: connection refused")

        #source: https://stackoverflow.com/questions/28377421/why-do-i-receive-a-timeout-error-from-pythons-requests-module
        #except requests.exceptions.Timeout:
            #print("Timeout occurred");

    return article_results;

def sortArticle(articleURL):
    #print("url:" + articleURL)
    #try:

    #pass article into machine learning model
    articleResult = get_sentiment(articleURL)

    #get party and confidence score
    demOrRep = articleResult[0];
    print("dem or rep: " + demOrRep)

    confidenceScore = articleResult[1];
    print("confidenceScore: " + str(confidenceScore))

    onSpectrum = getSpectrumString(demOrRep, confidenceScore);

    return [demOrRep, onSpectrum]

    #source: https://stackoverflow.com/questions/23013220/max-retries-exceeded-with-url-in-requests
    #except requests.exceptions.ConnectionError:
        #requests.status_code = "Connection refused"
        #print("error: connection refused")
        #return['n/a', 'n/a']

    #source: https://stackoverflow.com/questions/28377421/why-do-i-receive-a-timeout-error-from-pythons-requests-module
    #except requests.exceptions.Timeout:
        #print("Timeout occurred");

def getSpectrumString(demOrRep, confidenceScore):

    if confidenceScore != "n/a":

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

    return "no spectrum string found"

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
        #include laptops other than your own's user agents?
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
        config = Config()
        config.browser_user_agent = user_agent
        config.request_timeout = 10
        article = Article(url, config=config)
        article.download()
        article.parse()
        article_text = article.text
        sentiment = m.sentiment(article_text)
        print(str(sentiment))
        if len(sentiment) == 0:
            print("sentiment list is empty")
            sentiment = ['n/a', 'n/a']
        return sentiment

    except newspaper.article.ArticleException:
        return ['n/a', 'n/a']

    #except DateTimeException:
        #return ['n/a', 'n/a']

    return "error!";

    #except requests.exceptions.ConnectionError:
        #requests.status_code = "Connection refused"
        #print("error: connection refused")
        #return['n/a', 'n/a']

    #source: https://stackoverflow.com/questions/28377421/why-do-i-receive-a-timeout-error-from-pythons-requests-module
    #except requests.exceptions.Timeout:
        #print("Timeout occurred");
        #return['n/a', 'n/a']

def getCategories(categories):

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

    return [containsRight, containsLeft, containsNeutral]

# function that gets articles from a specific category fromt the database
def getCategoryArticles(category):

    cursor = mysql.connection.cursor()

    query = 'SELECT * FROM katherinesullivan_articlesA WHERE category=%s';

    queryVars = (category,);

    cursor.execute(query, queryVars);

    mysql.connection.commit();

    categoryArticles = cursor.fetchall();

    return categoryArticles;

# 2D Array with list of articles
articlesList = [[],[],[],[],[],[]];

# function that refreshes database
def refreshDatabase():

    cursor = mysql.connection.cursor()
    query = 'SELECT * FROM katherinesullivan_articlesA'
    cursor.execute(query)
    mysql.connection.commit()
    data = list(cursor.fetchall())
    length = len(data)
    if(length>0):
        for i in data:
            cursor = mysql.connection.cursor()
            query = 'DELETE FROM katherinesullivan_articlesA ORDER BY title LIMIT 1'
            cursor.execute(query)
            print("article deleted")
            mysql.connection.commit()

    tempArray = [];
    # #store an array of top headline articles and their assigned properties
    tempArray.extend(getArticles("http://newsapi.org/v2/top-headlines?country=us&apiKey=f4767a5c003944e5bbe9b97170bb65c0", "topHeadlines"))

    # store an array of entertainment articles and their assigned properties
    tempArray.extend(getArticles("http://newsapi.org/v2/top-headlines?country=us&category=entertainment&apiKey=77ab5895b882445b8796fa78919f022d", "entertainmentArticles"))

    # store an array of sports articles and their assigned properties
    tempArray.extend(getArticles("http://newsapi.org/v2/top-headlines?country=us&category=sports&apiKey=77ab5895b882445b8796fa78919f022d", "sportsArticles"))

    # store an array of business articles and their assigned properties
    tempArray.extend(getArticles("http://newsapi.org/v2/top-headlines?country=us&category=business&apiKey=77ab5895b882445b8796fa78919f022d", "businessArticles"))

    # store an array of science articles and their assigned properties
    tempArray.extend(getArticles("http://newsapi.org/v2/top-headlines?country=us&category=science&apiKey=77ab5895b882445b8796fa78919f022d", "scienceArticles"))

    # store an array of health articles and their assigned properties
    tempArray.extend(getArticles("http://newsapi.org/v2/top-headlines?country=us&category=health&apiKey=77ab5895b882445b8796fa78919f022d", "healthArticles"))

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
        query = "INSERT INTO katherinesullivan_articlesA (title, url, imageURL, category, leaning, onSpectrum) VALUES (%s, %s, %s, %s, %s, %s);"
        queryVars = (title, url, imageURL, category, sentiment, confidence,)
        cur.execute(query, queryVars);
        mysql.connection.commit()

    # # get current letter in database
    # currentLetter = getCurrentLetter();
    #
    # # if letter == "A", run refresh on B and switch letter in database to B
    # if currentLetter == "A":
    #
    #     cursor = mysql.connection.cursor()
    #     query = 'SELECT * FROM katherinesullivan_articlesB'
    #     cursor.execute(query)
    #     mysql.connection.commit()
    #     data = list(cursor.fetchall())
    #     length = len(data)
    #     if(length>0):
    #         for i in data:
    #             cursor = mysql.connection.cursor()
    #             query = 'DELETE FROM katherinesullivan_articlesB ORDER BY title LIMIT 1'
    #             cursor.execute(query)
    #             print("article deleted")
    #             mysql.connection.commit()
    #
    #     tempArray = [];
    #     # #store an array of top headline articles and their assigned properties
    #     tempArray.extend(getArticles("http://newsapi.org/v2/top-headlines?country=us&apiKey=f4767a5c003944e5bbe9b97170bb65c0", "topHeadlines"))
    #
    #     # store an array of entertainment articles and their assigned properties
    #     tempArray.extend(getArticles("http://newsapi.org/v2/top-headlines?country=us&category=entertainment&apiKey=77ab5895b882445b8796fa78919f022d", "entertainmentArticles"))
    #
    #     # store an array of sports articles and their assigned properties
    #     tempArray.extend(getArticles("http://newsapi.org/v2/top-headlines?country=us&category=sports&apiKey=77ab5895b882445b8796fa78919f022d", "sportsArticles"))
    #
    #     # store an array of business articles and their assigned properties
    #     tempArray.extend(getArticles("http://newsapi.org/v2/top-headlines?country=us&category=business&apiKey=77ab5895b882445b8796fa78919f022d", "businessArticles"))
    #
    #     # store an array of science articles and their assigned properties
    #     tempArray.extend(getArticles("http://newsapi.org/v2/top-headlines?country=us&category=science&apiKey=77ab5895b882445b8796fa78919f022d", "scienceArticles"))
    #
    #     # store an array of health articles and their assigned properties
    #     tempArray.extend(getArticles("http://newsapi.org/v2/top-headlines?country=us&category=health&apiKey=77ab5895b882445b8796fa78919f022d", "healthArticles"))
    #
    #     articlesList = tempArray
    #     for article in tempArray:
    #         cur = mysql.connection.cursor()
    #         title = article['title']
    #         url = article['url']
    #         imageURL = article['photo_url']
    #         if imageURL is None:
    #             imageURL = "blank"
    #         sentiment = article['politicalAssignment']
    #         confidence = article['onSpectrum']
    #         category = article['category']
    #         query = "INSERT INTO katherinesullivan_articlesB (title, url, imageURL, category, leaning, onSpectrum) VALUES (%s, %s, %s, %s, %s, %s);"
    #         queryVars = (title, url, imageURL, category, sentiment, confidence,)
    #         cur.execute(query, queryVars);
    #         mysql.connection.commit()
    #
    #     # set the letter to B
    #     cursor = mysql.connection.cursor()
    #     deleteTableData = "DELETE FROM katherinesullivan_AorB"
    #     cursor.execute(deleteTableData)
    #     mysql.connection.commit();
    #
    #     letterToInsert = "B"
    #     insertNewLetter = "INSERT INTO katherinesullivan_AorB (table) VALUES (%s)"
    #     querVars = (letterToInsert,)
    #     cursor.execute(insertNewLetter, queryVars)
    #     mysql.connection.commit();
    #
    # else:
    #
    #     cursor = mysql.connection.cursor()
    #     query = 'SELECT * FROM katherinesullivan_articlesA'
    #     cursor.execute(query)
    #     mysql.connection.commit()
    #     data = list(cursor.fetchall())
    #     length = len(data)
    #     if(length>0):
    #         for i in data:
    #             cursor = mysql.connection.cursor()
    #             query = 'DELETE FROM katherinesullivan_articlesA ORDER BY title LIMIT 1'
    #             cursor.execute(query)
    #             print("article deleted")
    #             mysql.connection.commit()
    #
    #     tempArray = [];
    #     # #store an array of top headline articles and their assigned properties
    #     tempArray.extend(getArticles("http://newsapi.org/v2/top-headlines?country=us&apiKey=f4767a5c003944e5bbe9b97170bb65c0", "topHeadlines"))
    #
    #     # store an array of entertainment articles and their assigned properties
    #     tempArray.extend(getArticles("http://newsapi.org/v2/top-headlines?country=us&category=entertainment&apiKey=77ab5895b882445b8796fa78919f022d", "entertainmentArticles"))
    #
    #     # store an array of sports articles and their assigned properties
    #     tempArray.extend(getArticles("http://newsapi.org/v2/top-headlines?country=us&category=sports&apiKey=77ab5895b882445b8796fa78919f022d", "sportsArticles"))
    #
    #     # store an array of business articles and their assigned properties
    #     tempArray.extend(getArticles("http://newsapi.org/v2/top-headlines?country=us&category=business&apiKey=77ab5895b882445b8796fa78919f022d", "businessArticles"))
    #
    #     # store an array of science articles and their assigned properties
    #     tempArray.extend(getArticles("http://newsapi.org/v2/top-headlines?country=us&category=science&apiKey=77ab5895b882445b8796fa78919f022d", "scienceArticles"))
    #
    #     # store an array of health articles and their assigned properties
    #     tempArray.extend(getArticles("http://newsapi.org/v2/top-headlines?country=us&category=health&apiKey=77ab5895b882445b8796fa78919f022d", "healthArticles"))
    #
    #     articlesList = tempArray
    #     for article in tempArray:
    #         cur = mysql.connection.cursor()
    #         title = article['title']
    #         url = article['url']
    #         imageURL = article['photo_url']
    #         if imageURL is None:
    #             imageURL = "blank"
    #         sentiment = article['politicalAssignment']
    #         confidence = article['onSpectrum']
    #         category = article['category']
    #         query = "INSERT INTO katherinesullivan_articlesA (title, url, imageURL, category, leaning, onSpectrum) VALUES (%s, %s, %s, %s, %s, %s);"
    #         queryVars = (title, url, imageURL, category, sentiment, confidence,)
    #         cur.execute(query, queryVars);
    #         mysql.connection.commit()
    #
    #     # set the letter to A
    #     cursor = mysql.connection.cursor()
    #     deleteTableData = "DELETE FROM katherinesullivan_AorB"
    #     cursor.execute(deleteTableData)
    #     mysql.connection.commit();
    #
    #     letterToInsert = "A"
    #     insertNewLetter = "INSERT INTO katherinesullivan_AorB (table) VALUES (%s)"
    #     querVars = (letterToInsert,)
    #     cursor.execute(insertNewLetter, queryVars)
    #     mysql.connection.commit();

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

def getCurrentTable(letter):

    if letter == "A":
        return "katherinesullivan_articlesA";
    elif letter == "B":
        return "katherinesullivan_articlesB";

    return "invalid letter input"

@app.route('/articleRefresh', methods=['POST'])

def databaseRefresh():

    refreshDatabase()
    return("Done")

@app.route('/', methods=["GET", "POST"])

#function that renders index.html
def index(methods=["GET", "POST"]):

    currentLetter = getCurrentLetter();
    #currentTable = getCurrentTable(currentLetter);

    if currentLetter == "A":
        results = indexCodeA();

    else:
        results = indexCodeB();

    return render_template('index.html', searchResults=results[0], printEmptySearch=results[1], clearMainRow=results[2], articles=results[3], rightFilter=results[4], leftFilter=results[5], neutralFilter=results[6], arrayBools=results[7]);

def indexCodeA():

        category = "topHeadlines";
        cursor = mysql.connection.cursor();
        query = "SELECT * FROM katherinesullivan_articlesA WHERE category=%s";
        queryVars = (category,);
        cursor.execute(query, queryVars);
        mysql.connection.commit();
        topHeadlinesData = cursor.fetchall();
        topHeadlineArticles = topHeadlinesData;

        #get list of checked categories in filter menu
        #source: https://www.reddit.com/r/flask/comments/bz376w/how_do_i_get_checked_checkboxes_into_flask/
        categories = request.form.getlist('party')
        filters = getCategories(categories);

        searchBoxInput = request.form.get('searchText');
        clearMainRow = 'False';
        printEmptySearch = 'False';
        searchResults = [];

        if searchBoxInput is not None:

            print("searchInputBox '" + searchBoxInput + "'")
            clearMainRow = 'True';

            #source: https://www.tutorialspoint.com/How-to-convert-a-string-to-a-list-of-words-in-python
            searchBoxInputWords = searchBoxInput.split();

            counter = 0;
            for i in searchBoxInputWords:
                counter += 1;
                print("#" + str(counter) + " word in search query: " + i)

            if searchBoxInput == '':
                printEmptySearch = 'True';

            # empty out array with search results
            searchResults = [];

            cursor = mysql.connection.cursor()
            query = 'SELECT * FROM katherinesullivan_articlesA'
            cursor.execute(query);
            mysql.connection.commit();
            articlesData = cursor.fetchall();

            # for every article
            for article in articlesData:

                # for every word in search query
                for word in searchBoxInputWords:
                    # get the article title (lowercase)
                    # source: https://www.programiz.com/python-programming/methods/string/lower
                    title = article['title'].lower();

                    # if title contains search word (lowercase)
                    if word.lower() in title:
                        notDuplicate = True;

                        # if search results already exist
                        if len(searchResults) != 0:
                            # loop through all search results
                            for result in searchResults:
                                # make sure that title of current article does
                                # not match title in search result
                                if result['title'] == article['title']:
                                    notDuplicate = False;

                        if notDuplicate:
                            # append the article to search results
                            searchResults.append(article);

        checkedBooleans = assignCheckedBooleans(filters[0], filters[1], filters[2]);

        return [searchResults, printEmptySearch, clearMainRow, topHeadlineArticles, checkedBooleans[0], checkedBooleans[1], checkedBooleans[2], checkedBooleans]

def indexCodeB():

            category = "topHeadlines";
            cursor = mysql.connection.cursor();
            query = "SELECT * FROM katherinesullivan_articlesB WHERE category=%s";
            queryVars = (category,);
            cursor.execute(query, queryVars);
            mysql.connection.commit();
            topHeadlinesData = cursor.fetchall();
            topHeadlineArticles = topHeadlinesData;

            #get list of checked categories in filter menu
            #source: https://www.reddit.com/r/flask/comments/bz376w/how_do_i_get_checked_checkboxes_into_flask/
            categories = request.form.getlist('party')
            filters = getCategories(categories);

            searchBoxInput = request.form.get('searchText');
            clearMainRow = 'False';
            printEmptySearch = 'False';
            searchResults = [];

            if searchBoxInput is not None:

                print("searchInputBox '" + searchBoxInput + "'")
                clearMainRow = 'True';

                #source: https://www.tutorialspoint.com/How-to-convert-a-string-to-a-list-of-words-in-python
                searchBoxInputWords = searchBoxInput.split();

                counter = 0;
                for i in searchBoxInputWords:
                    counter += 1;
                    print("#" + str(counter) + " word in search query: " + i)

                if searchBoxInput == '':
                    printEmptySearch = 'True';

                # empty out array with search results
                searchResults = [];

                cursor = mysql.connection.cursor()
                query = 'SELECT * FROM katherinesullivan_articlesB'
                cursor.execute(query);
                mysql.connection.commit();
                articlesData = cursor.fetchall();

                # for every article
                for article in articlesData:

                    # for every word in search query
                    for word in searchBoxInputWords:

                        # get the article title (lowercase)
                        # source: https://www.programiz.com/python-programming/methods/string/lower
                        title = article['title'].lower();

                        # if title contains search word (lowercase)
                        if word.lower() in title:

                            notDuplicate = True;

                            # if search results already exist
                            if len(searchResults) != 0:
                                # loop through all search results
                                for result in searchResults:
                                    # make sure that title of current article does
                                    # not match title in search result
                                    if result['title'] == article['title']:
                                        notDuplicate = False;

                            if notDuplicate:
                                # append the article to search results
                                searchResults.append(article);

            checkedBooleans = assignCheckedBooleans(filters[0], filters[1], filters[2]);

            return [searchResults, printEmptySearch, clearMainRow, topHeadlineArticles, checkedBooleans[0], checkedBooleans[1], checkedBooleans[2], checkedBooleans]

@app.route('/entertainment', methods=["GET", "POST"])

#function that renders entertainment.html
def entertainment(methods=["GET"]):

    currentLetter = getCurrentLetter();
    #currentTable = getCurrentTable(currentLetter);

    if currentLetter == "A":
        results = entertainmentCodeA();

    else:
        results = entertainmentCodeB();

    return render_template('category.html', pageTitle = "ENTERTAINMENT", articles=results[0], rightFilter = results[1], leftFilter = results[2], neutralFilter = results[3], arrayBools = results[4]);

def entertainmentCodeA():
    category = "entertainmentArticles";
    cursor = mysql.connection.cursor();
    query = 'SELECT * FROM katherinesullivan_articlesA WHERE category=%s';
    queryVars = (category,);
    cursor.execute(query, queryVars);
    mysql.connection.commit();
    entertainmentData = cursor.fetchall();
    entertainmentArticles = entertainmentData;
    categories = request.form.getlist('party')
    filters = getCategories(categories);
    checkedBooleans = assignCheckedBooleans(filters[0], filters[1], filters[2]);

    return [entertainmentArticles, checkedBooleans[0], checkedBooleans[1], checkedBooleans[2], checkedBooleans];

def entertainmentCodeB():
    category = "entertainmentArticles";
    cursor = mysql.connection.cursor();
    query = 'SELECT * FROM katherinesullivan_articlesB WHERE category=%s';
    queryVars = (category,);
    cursor.execute(query, queryVars);
    mysql.connection.commit();
    entertainmentData = cursor.fetchall();
    entertainmentArticles = entertainmentData;
    categories = request.form.getlist('party')
    filters = getCategories(categories);
    checkedBooleans = assignCheckedBooleans(filters[0], filters[1], filters[2]);

    return [entertainmentArticles, checkedBooleans[0], checkedBooleans[1], checkedBooleans[2], checkedBooleans];

@app.route('/sports', methods=["GET", "POST"])

#function that renders sports.html
def sports(methods=["GET"]):

    currentLetter = getCurrentLetter();
    #currentTable = getCurrentTable(currentLetter);

    if currentLetter == "A":
        results = sportsCodeA();

    else:
        results = sportsCodeB();

    return render_template('category.html', pageTitle = "SPORTS", articles=results[0], rightFilter = results[1], leftFilter = results[2], neutralFilter = results[3], arrayBools = results[4]);

def sportsCodeA():
    category = "sportsArticles";
    cursor = mysql.connection.cursor();
    query = 'SELECT * FROM katherinesullivan_articlesA WHERE category=%s';
    queryVars = (category,);
    cursor.execute(query, queryVars);
    mysql.connection.commit();
    sportsData = cursor.fetchall();
    sportsArticles = sportsData;
    categories = request.form.getlist('party')
    filters = getCategories(categories);
    checkedBooleans = assignCheckedBooleans(filters[0], filters[1], filters[2]);

    return [sportsArticles, checkedBooleans[0], checkedBooleans[1], checkedBooleans[2], checkedBooleans];

def sportsCodeB():
    category = "sportsArticles";
    cursor = mysql.connection.cursor();
    query = 'SELECT * FROM katherinesullivan_articlesB WHERE category=%s';
    queryVars = (category,);
    cursor.execute(query, queryVars);
    mysql.connection.commit();
    sportsData = cursor.fetchall();
    sportsArticles = sportsData;
    categories = request.form.getlist('party')
    filters = getCategories(categories);
    checkedBooleans = assignCheckedBooleans(filters[0], filters[1], filters[2]);

    return [sportsArticles, checkedBooleans[0], checkedBooleans[1], checkedBooleans[2], checkedBooleans];

@app.route('/science', methods=["GET", "POST"])

#function that renders science.html
def science(methods=["GET"]):

    currentLetter = getCurrentLetter();
    #currentTable = getCurrentTable(currentLetter);

    if currentLetter == "A":
        results = scienceCodeA();

    else:
        results = scienceCodeB();

    return render_template('category.html', pageTitle = "SCIENCE", articles=results[0], rightFilter = results[1], leftFilter = results[2], neutralFilter = results[3], arrayBools = results[4]);

def scienceCodeA():
    category = "scienceArticles";
    cursor = mysql.connection.cursor();
    query = 'SELECT * FROM katherinesullivan_articlesA WHERE category=%s';
    queryVars = (category,);
    cursor.execute(query, queryVars);
    mysql.connection.commit();
    scienceData = cursor.fetchall();
    scienceArticles = scienceData;
    categories = request.form.getlist('party')
    filters = getCategories(categories);
    checkedBooleans = assignCheckedBooleans(filters[0], filters[1], filters[2]);

    return [scienceArticles, checkedBooleans[0], checkedBooleans[1], checkedBooleans[2], checkedBooleans];

def scienceCodeB():
    category = "scienceArticles";
    cursor = mysql.connection.cursor();
    query = 'SELECT * FROM katherinesullivan_articlesB WHERE category=%s';
    queryVars = (category,);
    cursor.execute(query, queryVars);
    mysql.connection.commit();
    scienceData = cursor.fetchall();
    scienceArticles = scienceData;
    categories = request.form.getlist('party')
    filters = getCategories(categories);
    checkedBooleans = assignCheckedBooleans(filters[0], filters[1], filters[2]);

    return [scienceArticles, checkedBooleans[0], checkedBooleans[1], checkedBooleans[2], checkedBooleans];

@app.route('/business', methods=["GET", "POST"])

#function that renders business.html
def business(methods=["GET"]):

    currentLetter = getCurrentLetter();
    #currentTable = getCurrentTable(currentLetter);

    if currentLetter == "A":
        results = businessCodeA();

    else:
        results = businessCodeB();

    return render_template('category.html', pageTitle = "BUSINESS", articles=results[0], rightFilter = results[1], leftFilter = results[2], neutralFilter = results[3], arrayBools = results[4]);

def businessCodeA():
    category = "businessArticles";
    cursor = mysql.connection.cursor();
    query = 'SELECT * FROM katherinesullivan_articlesA WHERE category=%s';
    queryVars = (category,);
    cursor.execute(query, queryVars);
    mysql.connection.commit();
    businessData = cursor.fetchall();
    businessArticles = businessData;
    categories = request.form.getlist('party')
    filters = getCategories(categories);
    checkedBooleans = assignCheckedBooleans(filters[0], filters[1], filters[2]);

    return [businessArticles, checkedBooleans[0], checkedBooleans[1], checkedBooleans[2], checkedBooleans];

def businessCodeB():
    category = "businessArticles";
    cursor = mysql.connection.cursor();
    query = 'SELECT * FROM katherinesullivan_articlesB WHERE category=%s';
    queryVars = (category,);
    cursor.execute(query, queryVars);
    mysql.connection.commit();
    businessData = cursor.fetchall();
    businessArticles = businessData;
    categories = request.form.getlist('party')
    filters = getCategories(categories);
    checkedBooleans = assignCheckedBooleans(filters[0], filters[1], filters[2]);

    return [businessArticles, checkedBooleans[0], checkedBooleans[1], checkedBooleans[2], checkedBooleans];

@app.route('/health', methods=["GET", "POST"])

#function that renders health.html
def health(methods=["GET"]):

    currentLetter = getCurrentLetter();
    #currentTable = getCurrentTable(currentLetter);

    if currentLetter == "A":
        results = healthCodeA();

    else:
        results = healthCodeB();

    return render_template('category.html', pageTitle = "HEALTH", articles=results[0], rightFilter = results[1], leftFilter = results[2], neutralFilter = results[3], arrayBools = results[4]);

def healthCodeA():
    category = "healthArticles";
    cursor = mysql.connection.cursor();
    query = 'SELECT * FROM katherinesullivan_articlesA WHERE category=%s';
    queryVars = (category,);
    cursor.execute(query, queryVars);
    mysql.connection.commit();
    healthData = cursor.fetchall();
    healthArticles = healthData;
    categories = request.form.getlist('party')
    filters = getCategories(categories);
    checkedBooleans = assignCheckedBooleans(filters[0], filters[1], filters[2]);

    return [healthArticles, checkedBooleans[0], checkedBooleans[1], checkedBooleans[2], checkedBooleans];

def healthCodeB():
    category = "healthArticles";
    cursor = mysql.connection.cursor();
    query = 'SELECT * FROM katherinesullivan_articlesB WHERE category=%s';
    queryVars = (category,);
    cursor.execute(query, queryVars);
    mysql.connection.commit();
    healthData = cursor.fetchall();
    healthArticles = healthData;
    categories = request.form.getlist('party')
    filters = getCategories(categories);
    checkedBooleans = assignCheckedBooleans(filters[0], filters[1], filters[2]);

    return [healthArticles, checkedBooleans[0], checkedBooleans[1], checkedBooleans[2], checkedBooleans];

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
        #raise Exception("Could not locate article body")
    else:
        print("Got the article body!")

    cleaned_article_text = clean(article_text)

    return cleaned_article_text
