from flask import Flask, render_template, request
from flask_mysqldb import MySQL

app = Flask(__name__)


app.config['MYSQL_HOST'] = 'mysql.2021.lakeside-cs.org'
app.config['MYSQL_USER'] = 'student2021'
app.config['MYSQL_PASSWORD'] = 'm545CS42021'
app.config['MYSQL_DB'] = '2021project'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

#splits the tuple in the queries that find the latest addition into a string
def tupleToString(tuple):
    splits = tuple.split('\'')
    if(len(splits)==9):
        return str(splits[3] +" " + splits[7])
    return("none")


#checks if someone with this id has already registered for one of the two teams
def dupeID(id):
    cur = mysql.connection.cursor()
    query = "SELECT * FROM lukeli_girlsteam WHERE studentid=%s;"
    queryVars = (id,)
    cur.execute(query, queryVars);
    mysql.connection.commit()
    data = list(cur.fetchall())
    if(len(data)!= 0):
        return False
    cur = mysql.connection.cursor()
    query = "SELECT * FROM lukeli_boysteam WHERE studentid=%s;"
    queryVars = (id,)
    cur.execute(query, queryVars);
    mysql.connection.commit()
    data = list(cur.fetchall())
    if(len(data)!= 0):
        return False
    return True

#checks if the studentid is a 6-digit or 5-digit int
def studentid(id):
        if(id.isdigit()):
            if(len(str(id)) == 6 or len(str(id)) == 5):
                return True
        return False

#checks if the year the user selected is within the available range
def yearChecker(year):
    if(year.isdigit()):
        if(year!="2024"):
            if(year!="2023"):
                if(year!="2022"):
                    if(year!="2021"):
                        return False
        return True
#checks if all inputs are empty
def inputCheck(first, last, id, year) :
    if(len(first)!= 0):
        if(len(last)!= 0):
                if(studentid(id)):
                    if(len(year)!= 0):
                        if(yearChecker(year)):
                            return True
    return False
@app.route('/')
def home() :
    return render_template('index.html')

@app.route('/boystryouts', methods = ['GET', 'POST'])
def boys() :
    if(request.method == 'POST'):
        FirstName = request.values.get("firstName")
        LastName = request.values.get("lastName")
        Studentid = request.values.get("student-id")
        Class = request.values.get("class")

        if(inputCheck(FirstName, LastName, Studentid, Class)):
            if(dupeID(Studentid)):
                cur = mysql.connection.cursor()
                query = "INSERT INTO lukeli_boysteam (firstname, lastname, studentid, class) VALUES (%s, %s, %s, %s);"
                queryVars = (FirstName, LastName,Studentid, Class,)
                cur.execute(query, queryVars);
                mysql.connection.commit()
                return render_template('results.html', firstname = FirstName, lastname = LastName)
            else:
                return render_template('duplicateID.html')
        else:
            return render_template('boysfailure.html')
    else:
        return render_template('boysform.html')
@app.route('/registeredboys')
def boysview():
    cursor = mysql.connection.cursor()
    query = 'SELECT firstname, lastname, class FROM lukeli_boysteam'
    cursor.execute(query)
    mysql.connection.commit()
    data = cursor.fetchall()
    length = len(list(data))
    return render_template('athletes.html', rows = data, buffer = length)

#returns length of boys database, used to see if anyone new has registered
@app.route('/boyCounter', methods=['POST'])
def boyCounter():
    cursor = mysql.connection.cursor()
    query = 'SELECT * FROM lukeli_boysteam'
    cursor.execute(query)
    mysql.connection.commit()
    data = cursor.fetchall()
    length = len(list(data))
    return str(length)

#retrieves the name of the boy who last registered
@app.route('/recentBoy', methods=['POST'])
def recentBoy():
    cursor = mysql.connection.cursor()
    query = 'SELECT firstname, lastname FROM lukeli_boysteam ORDER BY orderadded DESC LIMIT 1'
    cursor.execute(query)
    mysql.connection.commit()
    data = cursor.fetchall()
    print("recent")
    return tupleToString(str(data)) + " just registered for boys basketball!"


@app.route('/girlstryouts', methods = ['GET', 'POST'])
def girls() :
    if(request.method == 'POST'):
        FirstName = request.values.get("firstName")
        LastName = request.values.get("lastName")
        Studentid = request.values.get("student-id")
        Class = request.values.get("class")

        if(inputCheck(FirstName, LastName, Studentid, Class)):
            if(dupeID(Studentid)):
                cur = mysql.connection.cursor()
                query = "INSERT INTO lukeli_girlsteam (firstname, lastname, studentid, class) VALUES (%s, %s, %s, %s);"
                queryVars = (FirstName, LastName,Studentid, Class,)
                cur.execute(query, queryVars);
                mysql.connection.commit()
                return render_template('results.html', firstname = FirstName, lastname = LastName)
            else:
                return render_template('duplicateID.html')
        else:
            return render_template('girlsfailure.html')
    else:
        return render_template('girlsform.html')
@app.route('/registeredgirls')
def girlsview():
    cursor = mysql.connection.cursor()
    query = 'SELECT firstname, lastname, class FROM lukeli_girlsteam'
    cursor.execute(query)
    mysql.connection.commit()
    data = cursor.fetchall()
    length = len(list(data))
    return render_template('girlsathletes.html', rows = data, buffer = length)

#returns length of girls database, used to see if anyone new has registered
@app.route('/girlCounter', methods=['POST'])
def girlCounter():
    cursor = mysql.connection.cursor()
    query = 'SELECT * FROM lukeli_girlsteam'
    cursor.execute(query)
    mysql.connection.commit()
    data = cursor.fetchall()
    length = len(list(data))

    return str(length)

#retrieves the name of the girl who last registered
@app.route('/recentGirl', methods=['POST'])
def recentGirl():
    cursor = mysql.connection.cursor()
    query = 'SELECT firstname, lastname FROM lukeli_girlsteam ORDER BY orderadded DESC LIMIT 1'
    cursor.execute(query)
    mysql.connection.commit()
    data = cursor.fetchall()
    return tupleToString(str(data)) + " just registered for girls basketball!"

@app.route('/news')
def news():
    return render_template('news.html')
