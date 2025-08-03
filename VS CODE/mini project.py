# File: main.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from flask import Flask, request, render_template
import os

# Data Ingestion Module
def load_and_preprocess_data(file_path):
    df = pd.read_csv(file_path)
    # Handle missing values
    df = df.dropna(subset=['vote_average', 'genre', 'country'])
    # Convert ratings to numeric
    df['vote_average'] = pd.to_numeric(df['vote_average'], errors='coerce')
    # Standardize country names (example: map variations of 'United States' to 'USA')
    df['country'] = df['country'].replace({'United States': 'USA', 'United Kingdom': 'UK'})
    return df

# Data Analysis Module
def analyze_ratings(df):
    # Average ratings by genre
    genre_ratings = df.groupby('genre')['vote_average'].mean().sort_values(ascending=False)
    # Average ratings by country
    country_ratings = df.groupby('country')['vote_average'].mean().sort_values(ascending=False)
    # Cross-tabulation of ratings by genre and country
    genre_country_ratings = df.pivot_table(values='vote_average', index='genre', columns='country', aggfunc='mean')
    return genre_ratings, country_ratings, genre_country_ratings

# Visualization Module
def generate_plots(df, output_dir='static'):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Bar plot for genre ratings
    genre_ratings = df.groupby('genre')['vote_average'].mean().sort_values(ascending=False)
    plt.figure(figsize=(10, 6))
    sns.barplot(x=genre_ratings.values, y=genre_ratings.index)
    plt.title('Average Movie Ratings by Genre')
    plt.xlabel('Average Rating')
    plt.ylabel('Genre')
    plt.savefig(os.path.join(output_dir, 'genre_ratings.png'))
    plt.close()
    
    # Heatmap for genre-country ratings
    genre_country_ratings = df.pivot_table(values='vote_average', index='genre', columns='country', aggfunc='mean')
    plt.figure(figsize=(12, 8))
    sns.heatmap(genre_country_ratings, annot=True, cmap='YlGnBu')
    plt.title('Average Ratings by Genre and Country')
    plt.savefig(os.path.join(output_dir, 'genre_country_heatmap.png'))
    plt.close()
    
    # Box plot for rating distribution by genre
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='genre', y='vote_average', data=df)
    plt.title('Rating Distribution by Genre')
    plt.xticks(rotation=45)
    plt.savefig(os.path.join(output_dir, 'genre_boxplot.png'))
    plt.close()

# Flask Web Application
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    genre = request.form.get('genre')
    country = request.form.get('country')
    df = load_and_preprocess_data('path/to/imdb_dataset.csv')  # Update with actual path
    generate_plots(df)
    
    # Filter data based on user input
    filtered_df = df
    if genre:
        filtered_df = filtered_df[filtered_df['genre'] == genre]
    if country:
        filtered_df = filtered_df[filtered_df['country'] == country]
    
    genre_ratings, country_ratings, genre_country_ratings = analyze_ratings(filtered_df)
    
    return render_template(
        'results.html',
        genre_ratings=genre_ratings.to_dict(),
        country_ratings=country_ratings.to_dict(),
        genre_country_ratings=genre_country_ratings.to_dict(),
        genre_plot='static/genre_ratings.png',
        heatmap_plot='static/genre_country_heatmap.png',
        boxplot_plot='static/genre_boxplot.png'
    )

if __name__ == '__main__':
    df = load_and_preprocess_data('path/to/imdb_dataset.csv')  # Update with actual path
    generate_plots(df)
    app.run(debug=True)

# File: templates/index.html
"""
<!DOCTYPE html>
<html>
<head>
    <title>IMDB Movie Ratings Analysis</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
</head>
<body class="bg-gray-100">
    <div class="container mx-auto p-4">
        <h1 class="text-2xl font-bold mb-4">IMDB Movie Ratings Analysis</h1>
        <form action="/analyze" method="post" class="mb-4">
            <div class="mb-4">
                <label for="genre" class="block text-sm font-medium">Genre:</label>
                <input type="text" id="genre" name="genre" class="border p-2 w-full" placeholder="e.g., Drama">
            </div>
            <div class="mb-4">
                <label for="country" class="block text-sm font-medium">Country:</label>
                <input type="text" id="country" name="country" class="border p-2 w-full" placeholder="e.g., USA">
            </div>
            <button type="submit" class="bg-blue-500 text-white p-2 rounded">Analyze</button>
        </form>
    </div>
</body>
</html>
"""

# File: templates/results.html
"""
<!DOCTYPE html>
<html>
<head>
    <title>Analysis Results</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
</head>
<body class="bg-gray-100">
    <div class="container mx-auto p-4">
        <h1 class="text-2xl font-bold mb-4">Analysis Results</h1>
        <h2 class="text-xl mb-2">Genre Ratings</h2>
        <ul>
            {% for genre, rating in genre_ratings.items() %}
                <li>{{ genre }}: {{ rating | round(2) }}</li>
            {% endfor %}
        </ul>
        <h2 class="text-xl mb-2">Country Ratings</h2>
        <ul>
            {% for country, rating in country_ratings.items() %}
                <li>{{ country }}: {{ rating | round(2) }}</li>
            {% endfor %}
        </ul>
        <h2 class="text-xl mb-2">Visualizations</h2>
        <img src="{{ genre_plot }}" alt="Genre Ratings" class="mb-4">
        <img src="{{ heatmap_plot }}" alt="Genre-Country Heatmap" class="mb-4">
        <img src="{{ boxplot_plot }}" alt="Genre Boxplot" class="mb-4">
        <a href="/" class="text-blue-500">Back to Home</a>
    </div>
</body>
</html>
"""

# File: requirements.txt
"""
pandas==1.5.3
matplotlib==3.7.1
seaborn==0.12.2
flask==2.2.2
gunicorn==20.1.0
"""

# File: .ebextensions/01_python.config
"""
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: main:app
"""

# File: README.md
"""
# IMDB Movie Ratings Analysis
This project analyzes movie ratings from the IMDB Movies Dataset to understand variations across genres and countries. It includes a Flask web app for interactive analysis and is deployed on AWS Elastic Beanstalk.

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Update `main.py` with the path to the IMDB dataset.
3. Run locally: `python main.py`
4. Deploy to AWS Elastic Beanstalk: `eb deploy`

## Directory Structure
- `main.py`: Core script for data processing and Flask app.
- `templates/`: HTML templates for the web interface.
- `static/`: Output directory for generated plots.
- `requirements.txt`: Project dependencies.
- `.ebextensions/`: AWS Elastic Beanstalk configuration.

## Dataset
The IMDB Movies Dataset should include columns: `vote_average`, `genre`, `country`.
""".
