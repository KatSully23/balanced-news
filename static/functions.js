
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

function createNoImageCard() {

  /*card with headlines that don't have images*/
  let otherArticles = "<div class='col-lg-3 mb-3'>" +
                        "<div class='card h-100'>" +
                        "<div class='card-header'>" +
                          "More from US Headlines" +
                        "</div>" +
                        "<ul id='list' class='list-group list-group-flush'>" +
                        "</ul>" +
                      "</div>" +
                      "</div" +
                      "<br><br>"

  var element = document.getElementById("mainRow");
  element.innerHTML += "<br>";
  element.innerHTML += otherArticles;

}

function appendNoImageArticle(noImageCount) {

  $(document).ready(function(){
    $("#list").append('<li class="list-group-item"><a href="{{articleURL}}">{{articleName}}</a></li>');
  });

  if (noImageCount == "1") {
    createNoImageCard();
  }

}
