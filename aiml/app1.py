import os
import pickle
import requests
from concurrent.futures import ThreadPoolExecutor

# This script is adapted to work without Streamlit when it's unavailable.
# If Streamlit is present, enable UI; otherwise, fallback to console display.
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ModuleNotFoundError:
    STREAMLIT_AVAILABLE = False

# Load movie data and similarity matrix with error handling
try:
    with open("movies_list.pkl", 'rb') as f:
        movies = pickle.load(f)
    with open("similarity.pkl", 'rb') as f:
        similarity = pickle.load(f)
except FileNotFoundError as e:
    raise FileNotFoundError("Required pickle files 'movies_list.pkl' or 'similarity.pkl' are missing.") from e

movies_list = movies['title'].values

# TMDB API key (replace with your actual key)
TMDB_API_KEY = "582563c15b66d26da51d171fc43f4013"  # Replace with your valid key

# Fetch poster using title (search endpoint)
def fetch_poster_by_title(title):
    search_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={title}"
    try:
        response = requests.get(search_url, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data['results']:
            poster_path = data['results'][0].get('poster_path')
            if poster_path:
                return f"https://image.tmdb.org/t/p/w500{poster_path}"
        return "https://via.placeholder.com/150?text=No+Image"
    except Exception as e:
        print(f"Error fetching poster for '{title}': {e}")
        return "https://via.placeholder.com/150?text=No+Image"

# Define recommend function
def recommend(movie):
    if movie not in movies['title'].values:
        raise ValueError(f"Movie '{movie}' not found in the dataset.")

    index = movies[movies['title'] == movie].index[0]
    distance = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda vector: vector[1])
    recommend_movie = []
    for i in distance[1:6]:
        recommend_movie.append(movies.iloc[i[0]].title)

    with ThreadPoolExecutor() as executor:
        recommend_posters = list(executor.map(fetch_poster_by_title, recommend_movie))

    return recommend_movie, recommend_posters

# Streamlit or console app
if STREAMLIT_AVAILABLE:
    st.title("🎬 Movie Recommender System")
    selectvalue = st.selectbox("Select a movie to get recommendations", movies_list)

    if st.button("Show Recommendations"):
        try:
            movie_names, poster_urls = recommend(selectvalue)

            st.subheader("Recommended Movies:")
            cols = st.columns(5)
            for i in range(5):
                with cols[i]:
                    st.image(poster_urls[i], caption=movie_names[i], use_column_width=True)
        except Exception as e:
            st.error(f"Error: {e}")
else:
    print("\nMovie Recommender System (Console Mode)")
    print("-------------------------------------")
    print("Sample movie list:")
    for i, title in enumerate(movies_list[:10]):
        print(f"{i + 1}. {title}")
    movie_input = input("\nType a movie name from above list (or full title): ")

    try:
        movie_names, poster_urls = recommend(movie_input)
        print("\nRecommended Movies:")
        for i in range(5):
            print(f"{movie_names[i]} - Poster URL: {poster_urls[i]}")
    except Exception as e:
        print(f"Error: {e}")

