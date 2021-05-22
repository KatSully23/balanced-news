
var intervalIDGirls = window.setInterval(girlsUpdate, 2000);
var intervalIDBoys = window.setInterval(boysUpdate, 2000);

function alerts(){
	alert("hello");
}
function girlsUpdate()
{

	var xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
		   var totalGirls = document.getElementById("total-girls");
			 if(this.responseText!=totalGirls.innerHTML){
		   	totalGirls.innerHTML = this.responseText;
			 	girlsRecent();
		 }
		}
    };
		xhttp.open("POST", "girlCounter", true);
    xhttp.send();
}

function girlsRecent()
{

	var xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
      alert(this.responseText);
			window.location.reload();
   }
    };
		xhttp.open("POST", "recentGirl", true);
    xhttp.send(); //asynchronous request
}

function boysUpdate()
{

	var xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
		   var totalBoys = document.getElementById("total-boys");
			 if(this.responseText!=totalBoys.innerHTML){
		   	totalBoys.innerHTML = this.responseText;
			 	boyRecent();
		 }
		}
    };
		xhttp.open("POST", "boyCounter", true);
    xhttp.send();
}

function boyRecent()
{

	var xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
      alert(this.responseText);
			window.location.reload();
   }
    };
		xhttp.open("POST", "recentBoy", true);
    xhttp.send(); //asynchronous request
}
