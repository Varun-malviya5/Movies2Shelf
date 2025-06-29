import streamlit as st
import pandas as pd
import re
import ast
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# -----------------------------
# Load your data
# -----------------------------
@st.cache_data
def load_data():
    movies_df = pd.read_csv('tmdb-movies.csv')
    books_df = pd.read_csv('books.csv')
    return movies_df, books_df

movies_df, books_df = load_data()

# -----------------------------
# Preprocessing
# -----------------------------

def clean_title(title):
    return re.sub(r'\s*\(\d{4}\)$', '', title).strip()

movies_df['clean_title'] = movies_df['original_title'].apply(clean_title)

def clean_book_genre(value):
    try:
        if isinstance(value, str) and value.startswith('[') and value.endswith(']'):
            parsed = ast.literal_eval(value)
            if isinstance(parsed, list):
                return parsed
        elif isinstance(value, str) and value.strip():
            return [value.strip()]
        else:
            return []
    except:
        return []

books_df['Genres_list'] = books_df['Genres'].apply(clean_book_genre)

movie_to_book_mapping = {
    'Drama': ['Fiction', 'Literature', 'Historical Fiction'],
    'Comedy': ['Humor'],
    'Thriller': ['Thriller', 'Mystery Thriller', 'Crime', 'Suspense'],
    'Romance': ['Romance'],
    'Action': ['Adventure', 'Thriller'],
    'Horror': ['Horror'],
    'Documentary': ['Nonfiction', 'Biography', 'Memoir', 'History'],
    'Crime': ['Crime', 'Mystery', 'Thriller'],
    'Adventure': ['Adventure', 'Fantasy', 'Science Fiction'],
    'Science Fiction': ['Science Fiction'],
    'Children': ['Childrens', 'Middle Grade'],
    'Animation': ['Childrens', 'Fantasy'],
    'Mystery': ['Mystery', 'Crime', 'Thriller'],
    'Fantasy': ['Fantasy', 'Science Fiction Fantasy'],
    'War': ['Historical Fiction', 'War', 'History'],
    'Western': ['Historical Fiction', 'Adventure'],
    'Musical': ['Fiction'],
    'Film-Noir': ['Mystery', 'Crime'],
    '(no genres listed)': ['Fiction'],
}

def matches_any(book_genres, mapped_genres):
    return any(bg.lower() in [g.lower() for g in book_genres] for bg in mapped_genres)

# -----------------------------
# Streamlit UI
# -----------------------------
def get_book_cover_url(title, author=None):
    query = f"intitle:{title}"
    if author:
        query += f"+inauthor:{author}"
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        items = data.get('items')
        if items:
            volume_info = items[0]['volumeInfo']
            image_links = volume_info.get('imageLinks')
            if image_links and 'thumbnail' in image_links:
                return image_links['thumbnail']
    return None

st.title("🎥📚 Movie to Book Recommender")

movie_name = st.text_input("Enter a movie name:")

if movie_name:
    cleaned_input = clean_title(movie_name)
    movie_row = movies_df[movies_df['clean_title'].str.lower() == cleaned_input.lower()]
    
    if movie_row.empty:
        st.warning(f"Movie '{movie_name}' not found in your dataset.")
    else:
        movie_genres = movie_row['genres'].values[0]
        movie_genre = movie_genres.split('|')[0] if '|' in movie_genres else movie_genres
        mapped_book_genres = movie_to_book_mapping.get(movie_genre)

        st.markdown(f"**Movie genres:** {movie_genres}")
        st.markdown(f"**Using first movie genre:** {movie_genre}")
        st.markdown(f"**Mapped book genres:** {mapped_book_genres}")

        if not mapped_book_genres:
            st.warning(f"No mapped book genres for '{movie_genre}'.")
        else:
            filtered_books = books_df[
                books_df['Genres_list'].apply(lambda x: matches_any(x, mapped_book_genres))
            ]
            if filtered_books.empty:
                st.warning("No books found for mapped genres.")
            else:
                movie_plot = movie_row['overview'].values[0]
                if pd.isna(movie_plot) or not movie_plot.strip():
                    st.warning("No plot summary found for this movie.")
                else:
                    plots = [movie_plot] + filtered_books['Description'].fillna('').tolist()
                    vectorizer = TfidfVectorizer(stop_words='english')
                    tfidf_matrix = vectorizer.fit_transform(plots)
                    cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
                    
                    filtered_books = filtered_books.copy()
                    filtered_books['similarity'] = cosine_sim
                    top_books = filtered_books.sort_values(by='similarity', ascending=False).head(10)

                    st.subheader(f"📚 Top {len(top_books)} book recommendations for '{movie_name}':")
                    for idx, row in top_books.iterrows():
                        title = row['Book']
                        author = row['Author'] if 'Author' in row else None
                        description = row['Description']
    
                        cover_url = get_book_cover_url(title, author)
    
                        if cover_url:
                        # ✅ Make two columns: image | text
                            col1, col2 = st.columns([1, 4])
                            with col1:
                                st.image(cover_url, width=100)
                            with col2:
                                st.markdown(f"**📖 Title:** {title}")
                                st.markdown(f"**📝 Description:** {description}\n")
                        else:
                            # ✅ Just text full width
                            st.markdown(f"**📖 Title:** {title}")
                            st.markdown(f"**📝 Description:** {description}\n")
    
                        st.markdown("---")