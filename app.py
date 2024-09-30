# app.py

from flask import Flask, render_template, request, jsonify
import pandas as pd

# Import nltk for downloading the necessary NLTK resources
from nltk.corpus import words

# Import os for getting the path to the bigram model
# import os

# # Import pickle for loading the bigram model
# import pickle

# Import transformer for BERT
# from transformers import BertTokenizer, BertForMaskedLM

# Import necessary functions for the miss spelling prediction
from checker import combined_correction, format_output_as_json

app = Flask(__name__)

# Load the Corpus File
file_path = 'data/corpus.csv'
df_corpus = pd.read_csv(file_path)

# Convert to list of corpus
corpus_list = df_corpus['word'].tolist()

# Convert to set of corpus
corpus = set(df_corpus['word'])

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    text = data.get('text_input', '')

    dictionary = corpus_list

    # Apply the combined correction function
    corrections, results = combined_correction(text, dictionary, corpus)
    # Format the output as JSON
    json_output = format_output_as_json(text, corrections, results)

    # # Preprocess text and remove punctuation
    # preprocessed_texts = remove_punctuation(text)

    # # Load valid English words from NLTK for edit distance
    # valid_words = set(words.words())

    # dictionary = list(valid_words)

    # corrections, results = combined_correction(preprocessed_texts, dictionary)
    # json_output = format_output_as_json(text, corrections, results)

    return json_output

if __name__ == '__main__':
    app.run(debug=True)
