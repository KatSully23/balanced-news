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
    # Init
    #newsapi = NewsApiClient(api_key='50b2c8ff5033428fb2ee50645ced43c9')

    # /v2/top-headlines
    #top_headlines = newsapi.get_top_headlines(q='bitcoin',
                                              #sources='bbc-news,the-verge, fox',
                                              #category='business',
                                              #language='en')
    #print(top_headlines);


    #tutorial: https://www.youtube.com/watch?v=iFHE-0gZuZE

    main_url = "https://newsapi.org/v2/top-headlines?country=us&apiKey=50b2c8ff5033428fb2ee50645ced43c9"
    #main_url = "https://newsapi.org/v2/sources?apiKey=50b2c8ff5033428fb2ee50645ced43c9"
    #main_url = "https://newsapi.org/v2/sources?category=businessapiKey=50b2c8ff5033428fb2ee50645ced43c9"

    open_bbc_page = requests.get(main_url).json()
    articles = open_bbc_page["articles"]
    results = []

    dataSet = get_articles(articles);

    #for i in articles:
        #for i in articles:
            #print(results.append(i["title"]));
            #print(f''' author: {i['author']}
                       #title: {i['title']}
                       #description: {i['description']}
                       #url: {i['url']} ''')


    for i in range(len(dataSet)):
        print("")
        print("***********************")
        print(i + 1, dataSet[i])

        #print("url: " + articles[i]['url']);
        #print("author: " + articles[i]['author']);
        #print("description: " + articles[i]['description']);

    #print("")
    #print("****************HELLO*************")
    #print("title: " + articles[0]['title']);
    #print("author: " + articles[0]['author']);
    #print("description: " + articles[0]['description']);
    #print("")

    #dataSet = get_articles(results);
    #dataSet = 1;

    imgURL = dataSet[15]['photo_url'];
    articleName = dataSet[15]['title'];
    articleAuthor = dataSet[15]['author'];
    articleContent = dataSet[15]['content'];
    articleURL = dataSet[15]['url'];

    # imgURL = "https://pypi.org/static/images/twitter.90915068.jpg"
    return render_template('us.html', articles=dataSet);
    #return render_template('index.html', img=imgURL, title=articleName, author=articleAuthor, content=articleContent, link=articleURL)
    #, news=articles[1].items())


@app.route('/machineTutorial')

def machineTutorial():
    return render_template('machineTutorial.html')

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

#function to get all the results for articles
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
