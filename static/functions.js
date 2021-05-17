
var articlesWithImages = "all";

function changeArticlesWithImages() {
  articlesWithImages = "not all";
}

function getArticlesWithImages() {
  return articlesWithImages;
}

/* creates code for specific card and store it in array using javascript function */
/* pass in spectrumImagePath as a parameter  */
function getCardCode(imageURL, newsArticleURL, newsArticleName, spectrumImagePath) {

  /*console.log("hello");*/

 let cardCode = "<div class='col-lg-3 mb-3'>" +
                    "<div class='card h-100'>" +

                      "<img class='card-img-top' src='url' >" +

                      "<div class='card-body'>" +

                      "<div class='tooltip-wrap'>" +
                      "<h5 class='card-title'>" +
                      "<a href='linkToArticle'>nameOfArticle</a></h5>" +
                      "<div class='tooltip-content'>" +
                        "<img class='spectrumImage' src='path' alt='spectrum' />" +
                      "</div>" +
                    "</div>" +

                      "</div>" +

                      "</div>"  +

                    "</div>" +
                  "</div>"

  /* change variable names to something more informative */
  let cardParameter1 = cardCode.replace("url", imageURL);
  let cardParameter2 = cardParameter1.replace("linkToArticle", newsArticleURL);
  let cardParameter3 = cardParameter2.replace("nameOfArticle", newsArticleName);
  let cardParameter4 = cardParameter3.replace("path", spectrumImagePath);

  return cardParameter4;

}

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

function appendNoImageArticle(articleURL, articleName, spectrumImage) {

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
