
var articlesWithImages = "all";
var articlesOnDisplay = 0;

/*
function that resets value of articlesWithImages variable to
indicate that all articles read from database have images
parameters: none
returns: none
*/
function changeBackArticlesWithImages() {
  articlesWithImages = "all";
}

/*
function that resets value of articlesWithImages variable
to indicate that not all articles read from database have images
parameters: none
returns: none
*/
function changeArticlesWithImages() {
  articlesWithImages = "not all";
}

/*
function that returns value of articleWithImages variable
to determine whether or not all articles have images
parameters: none
returns: articlesWithImages variable
*/
function getArticlesWithImages() {
  return articlesWithImages;
}

/*
function that resets value of articlesOnDisplay variable
to indicate that no articles are currently
being displayed on the user interface
parameters: none
returns: none
*/
function resetArticlesOnDisplay() {
  articlesOnDisplay = 0;
}

/*
function that increments value of articlesOnDisplay variable
to indicate that an article has been added
to the user interface display
parameters: none
returns: none
*/
function incrementArticlesOnDisplay() {
  articlesOnDisplay += 1;
}

/*
function that returns value of articlesOnDisplay variable
to determine how many articles are currently
being displayed on the user interface
parameters: none
returns: number of articles being displayed on user interface
*/
function getArticlesOnDisplay() {
  return articlesOnDisplay;
}

/*
function that generates html code for a Boostrap card that will display an article
parameter 'imageURL': url to image associated with article
parameter 'newsArticleURL': url to article
parameter 'newsArticleName': name of article
parameter 'spectrumImagePath': name of image associated with article's
location on political spectrum
return: string with html code for article being displayed on user interface
*/
function getCardCode(imageURL, newsArticleURL, newsArticleName, spectrumImagePath) {

 let cardCode = "<div class='col-lg-3 mb-3'>" +
                    "<div class='card h-100'>" +

                      "<img class='card-img-top' src='url' >" +

                      "<div class='card-body'>" +

                      "<div class='tooltip-wrap'>" +
                      "<h5 class='card-title'>" +
                      "<a href='linkToArticle'>nameOfArticle</a></h5>" +
                      "<div class='tooltip-content'>" +
                        "<img class='spectrumImage' src='kimagePath' alt='spectrum' />" +
                      "</div>" +
                    "</div>" +

                      "</div>" +

                      "</div>"  +

                    "</div>" +
                  "</div>"

  let cardCode1 = cardCode.replace("url", imageURL);
  let cardCode2 = cardCode1.replace("linkToArticle", newsArticleURL);
  let cardCode3 = cardCode2.replace("nameOfArticle", newsArticleName);
  let cardCode4 = cardCode3.replace("kimagePath", spectrumImagePath);

  return cardCode4;

}

/*
function that generates html code for a card where articles
without an associated image are placed
parameter 'moreFromString': string representing title of 'no image articles' card
return: string with html code for 'no image articles' card
*/
function createNoImageCard(moreFromString) {

  /* card with headlines that don't have image s*/
  let otherArticles = "<div id='noImageCard' class='col-lg-3 mb-3'>" +
                        "<div class='card h-100'>" +
                        "<div class='card-header'>" +
                          "Title" +
                        "</div>" +
                        "<ul id='list' class='list-group list-group-flush'>" +
                        "</ul>" +
                      "</div>" +
                      "</div" +
                      "<br><br>"

    return otherArticles.replace('Title', moreFromString);

}

/*
function that generates html code for an article without an associated
image and adds it to the 'no image articles' card on the user interface
parameter 'articleURL': url to article
parameter 'articleName': name of article
parameter 'spectrumImage': name of image associated with article's
location on political spectrum
returns: none
*/
function appendNoImageArticle(articleURL, articleName, spectrumImage) {

  /* source for 'border-0': https://stackoverflow.com/questions/32322775/how-to-remove-a-list-item-border-in-bootstrap-list-group/32322811 */
  $(document).ready(function(){

    articleCode = "<div class='tooltip-wrap'>" +
                  "<li class='list-group-item border-0'>" +
                  "<a href='articleURL'>articleName</a>" +
                  "</li>" +
                  "<div class='tooltip-content'>" +
                    "<img class='spectrumImage' src='path' alt='spectrum' />" +
                  "</div>" +
                  "</div>"

    articleCode2 = articleCode.replace("articleURL", articleURL);
    articleCode3 = articleCode2.replace("articleName", articleName);
    articleCodeFinal = articleCode3.replace("path", spectrumImage)
    $("#list").append(articleCodeFinal);

  });

}

/*
function that clears content of a specified element and replaces it with a string
that tells the user they have entered an empty search query or that
there are no results for their search query
parameter 'elementId': element whose content is being cleared
parameter 'printEmptySearch': boolean indicating whether or not to print a messsage
that will alert the user of the fact that they have entered an empty search query
parameter 'printNoResults': boolean indicating whether or not to print a messsage
that will alert the user of the fact that their search query has no results
returns: none

source: https://stackoverflow.com/questions/3450593/how-do-i-clear-the-content-of-a-div-using-javascript */
function clearBox(elementID, printEmptySearch, printNoResults)
{
    document.getElementById(elementID).innerHTML = " ";

    if (printEmptySearch) {

      emptyStringHTML = "<br>" +
                        "<div class='container-fluid'>" +
                          "<p class='instructionsText'> Oops! You entered an empty string. Please try again :)</p>" +
                        "</div>" +
                        "<br>" +
                        "<br>"

      document.getElementById(elementID).innerHTML = emptyStringHTML;

    }

    if (printNoResults) {

      emptyStringHTML = "<br>" +
                        "<div class='container-fluid'>" +
                          "<p class='instructionsText'> Looks like there are no results for your search! Please search for something else or refresh the page :) </p>" +
                        "</div>" +
                        "<br>" +
                        "<br>"

      document.getElementById(elementID).innerHTML = emptyStringHTML;

    }

}

/*
function that clears main site content and replaces it with a string that tells
the user that there are no articles that fall under the filters they have selected
parameters: none
returns: none
*/
function noFilterResults() {

  document.getElementById("mainRow").innerHTML = " ";

  emptyStringHTML = "<br>" +
                    "<div class='container-fluid'>" +
                      "<p class='instructionsText'> Looks like there are no articles with the political classification(s) you selected! Please try another filter or refresh the page :)</p>" +
                    "</div>" +
                    "<br>" +
                    "<br>"

  document.getElementById("mainRow").innerHTML = emptyStringHTML;

}

/* function that triggers process of refreshing MySQL database tables
from which user interface data is read
parameters: none
returns: none
*/
function databaseRefresh(){

  //Sets up the AJAX object
  var xhttp = new XMLHttpRequest();

  //function will be called AFTER the POST request returns
  xhttp.onreadystatechange = function() {

    //if we're actually done successfully
    if (this.readyState == 4 && this.status == 200) {

      console.log("checking for new article data...")

    }

  }

  //Tells JS which webpage to go to and
  //how to go to it
  xhttp.open("POST", "articleRefresh", true);
  xhttp.send();

}
