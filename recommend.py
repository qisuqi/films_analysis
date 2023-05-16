import pandas as pd
import ast

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.stem.porter import PorterStemmer

import pickle

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

movies = pd.read_csv('tmdb_5000_movies.csv')
credits = pd.read_csv('tmdb_5000_credits.csv')

merged = movies.merge(credits, on='title')
merged = merged[['id', 'title', 'overview', 'genres', 'keywords', 'cast', 'crew']]
merged.dropna(inplace=True)


def convert(obj):
    L = []
    for i in ast.literal_eval(obj):
        L.append(i['name'])
    return L


def convert3(obj):
    L = []
    c = 0
    for i in ast.literal_eval(obj):
        if c != 3:
            L.append(i['name'])
            c += 1
        else:
            break
    return L


def fetchDirector(obj):
    L = []
    for i in ast.literal_eval(obj):
        if i['job'] == 'Director':
            L.append(i['name'])
            break
    return L


def stem(text):
    y = []
    for i in text.split():
        y.append(ps.stem(i))
    return " ".join(y)


merged['genres'] = merged['genres'].apply(convert)
merged['keywords'] = merged['keywords'].apply(convert)
merged['cast'] = merged['cast'].apply(convert3)
merged['crew'] = merged['crew'].apply(fetchDirector)
merged['overview'] = merged['overview'].apply(lambda x: x.split())

merged['genres'] = merged['genres'].apply(lambda x: [i.replace(" ", "") for i in x])
merged['keywords'] = merged['keywords'].apply(lambda x: [i.replace(" ", "") for i in x])
merged['cast'] = merged['cast'].apply(lambda x: [i.replace(" ", "") for i in x])
merged['crew'] = merged['crew'].apply(lambda x: [i.replace(" ", "") for i in x])

merged['tags'] = merged['overview'] + merged['genres'] + merged['cast'] + merged['crew']

new_df = merged[['id', 'title', 'tags']]

new_df['tags'] = new_df['tags'].apply(lambda x: " ".join(x))
new_df['tags'] = new_df['tags'].apply(lambda x: x.lower())

cv = CountVectorizer(max_features=5000, stop_words='english')
vectors = cv.fit_transform(new_df['tags']).toarray()

ps = PorterStemmer()
new_df['tags'] = new_df['tags'].apply(stem)

cosine_similarity(vectors)
similarity = cosine_similarity(vectors).shape

movie_index = new_df[new_df['title'] == merged].index[0]


def recommend(movie):
    # find the index of the movies
    movie_index = new_df[new_df['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    # to fetch movies from indeces
    for i in movies_list:
        print(new_df.iloc[i[0]].title)


pickle.dump(new_df.to_dict(), open('movies.pkl','wb'))
pickle.dump(similarity, open('similarity.pkl', 'wb'))



