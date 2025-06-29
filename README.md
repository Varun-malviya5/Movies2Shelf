# 🎥📚 Movies2Shelf

**Movies2Shelf** is a simple **Movie ➜ Book Recommender**.  
Give it a movie name — it maps the movie’s genre and plot to books you might love!

---

## 🚀 Features

- 📽️ Input any movie title  
- 🎯 Maps movie genres to book genres  
- 🔍 Uses movie plot to match similar books with TF-IDF  
- 🖼️ Fetches real-time book cover images from Google Books API  
- 📚 Returns top 10 recommended books with descriptions

---

## 🛠️ Tech Stack

- **Python**
- **Streamlit**
- **Pandas**
- **Scikit-Learn** (TF-IDF & cosine similarity)
- **Google Books API**

---

## 📂 How to Run

1️⃣ Install requirements:  
```bash
pip install -r requirements.txt
2️⃣ Run the app:

bash
Copy
Edit
streamlit run app.py
3️⃣ Open in your browser:
http://localhost:8501

🌐 Data
🎞️ tmdb-movies.csv — movie titles, genres, and overviews

📚 books.csv — book titles, genres, descriptions

✅ Future Ideas
Deploy to Streamlit Cloud

Add user ratings for recommendations

Save reading lists

Add Goodreads or Open Library integration

📜 License
MIT License — do whatever you want, just give credit. 🤝

Made with ❤️ for movie and book lovers.