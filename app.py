from flask import Flask, request, render_template
import pickle
import requests
import pandas as pd

movies = pickle.load(open('model/movies_list.pkl', 'rb'))
similarity = pickle.load(open('model/similarity.pkl', 'rb'))

def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=d6cca4afbf34de24987bdd2239bcb8c9&language=en-US".format(movie_id)
    data = requests.get(url)
    data = data.json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommend_movies_name = []
    recommend_movies_poster = []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommend_movies_poster.append(fetch_poster(movie_id))
        recommend_movies_name.append(movies.iloc[i[0]].title)
    return recommend_movies_name, recommend_movies_poster

app = Flask(__name__)

@app.route("/mrs_app")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/recommendation", methods=['GET', 'POST'])
def recommendation():
    movie_list = movies['title'].values
    status = False
    selected_movie = None

    if request.method == "POST":
        try:
            if 'movies' in request.form:
                selected_movie = request.form['movies']
                recommend_movies_name, recommend_movies_poster = recommend(selected_movie)
                status = True

                return render_template("prediction.html", movies_name=recommend_movies_name, poster=recommend_movies_poster, movie_list=movie_list, status=status, selected_movie=selected_movie)

        except Exception as e:
            error = {'error': e}
            return render_template("prediction.html", error=error, movie_list=movie_list, status=status)

    else:
        return render_template("prediction.html", movie_list=movie_list, status=status)

if __name__ == '__main__':
    app.debug = True
    app.run()
