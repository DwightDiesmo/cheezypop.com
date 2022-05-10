from flask import Flask, render_template, request, flash, url_for, redirect, session
import mysql.connector
import decimal

selectMovies = 'SELECT * FROM movies'
selectReviews = 'SELECT * FROM reviews'
app = Flask(__name__);
app.secret_key = "super secret key"

class User:
  def __init__(self, isLoggedIn, name, email):
    self.isLoggedIn = isLoggedIn
    self.name = name
    self.email = email

class MaxSizeList(object):

    ls = []

    def __init__(self,mx):
        self.val = mx


    def push(self,st):
        self.ls.append(st)



    def get_list(self):
        while len(self.ls) != self.val:
            self.ls.pop(0)
        return self.ls

user = User(False, '', '');

def byRating(elem):
    return elem[-1]

@app.route("/")
def home():
    connection = mysql.connector.connect(host="localhost", port="3306", user="root", database="cheezypop")
    cursor = connection.cursor()
    cursor.execute(selectMovies + ' ORDER BY movies.release_date DESC LIMIT 4;')
    newMovies = cursor.fetchall()
    print(newMovies[0][0])
    cursor.execute(selectMovies)
    movieList = cursor.fetchall()
    print(f"Number of Movies {cursor.rowcount}")

    selectReviews = f"SELECT moviename, AVG(rating) FROM reviews GROUP BY moviename"
    cursor.execute(selectReviews)
    reviewList = cursor.fetchall()
    print(f"Number of Reviews {cursor.rowcount}")

    movieRecords = list()
    for movie in movieList:
        for review in reviewList:
            if movie[0].replace('\r\n', '') == review[0].replace('\r\n', ''):
                movie += (round(review[1], 1),)
        if not isinstance(movie[-1], decimal.Decimal):
            movie += (decimal.Decimal('0.0'),)
        movieRecords.append(movie)
    print(type(movieRecords))
    movieRecords.sort(reverse=True, key=byRating)
    print(movieRecords)
    featuredMovies = list()
    for i in range(0,4):
        featuredMovies.append(movieRecords[i])

    print(featuredMovies)
    print(user.name)
    cursor.execute(f"SELECT * FROM reviews WHERE username LIKE '{user.name}' ORDER BY rating DESC")
    userReviewHistory = cursor.fetchall()
    print(userReviewHistory)

    if userReviewHistory == None:
        print("None Here")

    cursor.execute("SELECT * FROM movies")
    movieList = cursor.fetchall()

    reviewRecord = list()
    for movie in movieList:
        for review in userReviewHistory:
            if movie[0] == review[0]:
                print(movie[0])
                movie += (review[2],)
                reviewRecord.append(movie)
    print(reviewRecord)

    genreList = list()
    for movie in reviewRecord:
        if movie[1] not in genreList:
            print(movie[1])
            genreList.append(movie[1])

    print(genreList)
    print(len(genreList))

    print("User Reviewed Movies")
    for i in range(0, len(reviewRecord)):
        reviewRecord[i][0].replace('\r\n', '')
        print(reviewRecord[i][0].replace('\r\n', ''))

    matchingGenreQuery = f"SELECT * FROM movies WHERE idmoviename NOT LIKE '{reviewRecord[0][0]}'"
    for i in range(1, len(reviewRecord)):
        matchingGenreQuery += f" AND idmoviename NOT LIKE '{reviewRecord[i][0]}'"
    matchingGenreQuery += f" AND genre LIKE '{genreList[0]}'"
    for i in range(1, len(genreList)):
        matchingGenreQuery += f" OR genre LIKE '{genreList[i]}'"
    for i in range(0, len(reviewRecord)):
        matchingGenreQuery += f" AND idmoviename NOT LIKE '{reviewRecord[i][0]}'"

    print(matchingGenreQuery)
    cursor.execute(matchingGenreQuery)
    matchingGenreList = cursor.fetchall()
    print(matchingGenreList)

    recommendedMovies = matchingGenreList
    print(recommendedMovies)
    return render_template("index.html", newMovies=newMovies, featuredMovies=featuredMovies, recommendedMovies=recommendedMovies, user=user);

@app.route("/submission/", methods=["POST", "GET"])
def submission():
    if request.method == "POST":
        connection = mysql.connector.connect(host="localhost", port="3306", user="root", database="cheezypop")
        cursor = connection.cursor()
        movieName = request.form["movieName"] + '\r\n'
        movieDescription = request.form["movieDescription"]
        movieRating = request.form["movieRating"]
        movieGenre = request.form["movieGenre"]
        movieCompany = request.form["movieCompany"]
        movieDirector = request.form["movieDirector"]
        movieLink = request.form["movieLink"].replace('watch?v=','embed/')
        moviePoster = request.form["moviePoster"]
        movieDurationHours = request.form["movieDurationHours"]
        movieDurationMinutes = request.form["movieDurationMinutes"]
        movieRelease = request.form["movieRelease"]
        insertSyntax = (
            "INSERT INTO `movies` (`idmoviename`, `genre`, `rating`, `description`, `production_company`, `director`, `trailer_link`, `image_link`, `duration_hours`, `duration_minutes`, `release_date`)"
            " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
        )
        insertData = (
            movieName,
            movieGenre,
            movieRating,
            movieDescription,
            movieCompany,
            movieDirector,
            movieLink,
            moviePoster,
            movieDurationHours,
            movieDurationMinutes,
            movieRelease
        )
        cursor.execute(insertSyntax,insertData)
        cursor.execute("COMMIT;")
        cursor.close()
        connection.close()
        flash("You have added a new movie!")
        return redirect(url_for("movies"))
    else:
        return render_template("submission.html", user=user);

@app.route("/movies/", methods=["POST", "GET"])
def movies():
    # user = [userIsLogged, userName, userEmail]
    connection = mysql.connector.connect(host="localhost", port="3306", user="root", database="cheezypop")
    cursor = connection.cursor()
    selectMovies = f"SELECT * FROM movies"
    cursor.execute(selectMovies)
    movieList = cursor.fetchall()
    print(movieList)
    print(f"Number of Movies {cursor.rowcount}")

    selectReviews = f"SELECT moviename, AVG(rating) FROM reviews GROUP BY moviename"
    cursor.execute(selectReviews)
    reviewList = cursor.fetchall()
    print(f"Number of Reviews {cursor.rowcount}")

    movieRecords = list()
    for movie in movieList:
        for review in reviewList:
            if movie[0].replace('\r\n', '') == review[0].replace('\r\n', ''):
                movie += (round(review[1], 1),)
        if not isinstance(movie[-1], decimal.Decimal):
            movie += (decimal.Decimal('0.0'),)
        movieRecords.append(movie)

    if request.method == 'POST':
        searchedMovie = request.form['searchedMovie']
        print(f"Searched Movie = {searchedMovie}")
        for movie in movieList:
            if searchedMovie == movie[0].replace('\r\n', ''):
               print(True)
               return redirect(url_for('moviePage', movie=movie[0]))
            else:
               print(False)
    else:
        return render_template("movies.html", movieRecords=movieRecords, user=user);

@app.route("/<movie>/", methods=["GET", "POST"])
def moviePage(movie):
    print(user.name)
    connection = mysql.connector.connect(host="localhost", port="3306", user="root", database="cheezypop")
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM movies WHERE movies.idmoviename='{movie}'")
    movie = cursor.fetchone()
    cursor.execute(f"SELECT * FROM reviews WHERE reviews.moviename='{movie[0]}'")
    reviews = cursor.fetchall()
    cursor.execute(f"SELECT AVG(rating) FROM reviews WHERE reviews.moviename='{movie[0]}'")
    rating = cursor.fetchone()
    rating = 'N/A' if rating[0]==None else round(rating[0], 1)
    if request.method == 'POST':
        userRating = request.form["userRating"]
        userReview = request.form["userReview"]
        insertSyntax = (
            "INSERT INTO `reviews` (`moviename`, `comments`, `rating`, `username`)"
            " VALUES (%s, %s, %s, %s);"
        )
        insertData = (
            movie[0],
            userReview,
            userRating,
            user.name
        )
        cursor.execute(insertSyntax, insertData)
        cursor.execute('COMMIT;')
        return redirect(url_for("moviePage", movie=movie[0]));
    else:
        return render_template("movie-page.html", movie=movie, reviews=reviews, rating=rating, user=user);

@app.route("/signup/",  methods=["GET", "POST"])
def signup():
    # user = [userIsLogged, userName, userEmail]
    connection = mysql.connector.connect(host="localhost", port="3306", user="root", database="cheezypop")
    cursor = connection.cursor()
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        insertSyntax = (
            "INSERT INTO `users` (`idusername`, `email`, `password`)"
            " VALUES (%s, %s, %s);"
        )
        insertData = (username, email, password)
        cursor.execute(insertSyntax, insertData)
        print(cursor.statement)
        cursor.execute('COMMIT;')
        cursor.close()
        flash("You have signed up!")
        return redirect(url_for("login"))
    else:
        return render_template("signup.html", user=user);

@app.route("/login/", methods=["GET", "POST"])
def login():
    # user = [userIsLogged, userName, userEmail]
    connection = mysql.connector.connect(host="localhost", port="3306", user="root", database="cheezypop")
    cursor = connection.cursor()
    if request.method=='POST':
        email = request.form['email']
        password = request.form['password']
        cursor.execute('SELECT * FROM users WHERE email=%s AND password=%s', (email, password))
        record = cursor.fetchone()
        if record:
            user.isLoggedIn = True
            user.email = record[1]
            user.name= record[0]
            flash("You have logged in!", "info")
            return redirect(url_for('movies'))
        else:
            print("false")
            return redirect(url_for('signup'))
    return render_template("login.html", user=user);

@app.route("/logout/")
def logout():
    user.isLoggedIn = False
    user.name = ''
    user.email = ''
    flash("You have logged out!")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
