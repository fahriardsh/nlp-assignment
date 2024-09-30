# app.py

from flask import Flask, render_template, request, jsonify

# Import nltk for downloading the necessary NLTK resources
from nltk.corpus import words

# Import os for getting the path to the bigram model
# import os

# # Import pickle for loading the bigram model
# import pickle

# Import transformer for BERT
# from transformers import BertTokenizer, BertForMaskedLM

# Import necessary functions for the miss spelling prediction
from spelling_checker import remove_punctuation, combined_correction, format_output_as_json


app = Flask(__name__)

# Get the path to the bigram model
# bigram_model_path = os.path.join(os.path.dirname(__file__), 'data', 'bigram_model.pkl')

# print("Loading Bigram model...")
# # Open the file and load the bigram model
# with open(bigram_model_path, 'rb') as f:
#     bigram_model = pickle.load(f)

# Load the BERT model and tokenizer once during app initialization
# print("Loading BERT model...")
# tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
# model = BertForMaskedLM.from_pretrained('bert-base-uncased')
# model.eval()  # Set the model to evaluation mode since we're only doing inference

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    text = data.get('text_input', '')

    # Preprocess text and remove punctuation
    preprocessed_texts = remove_punctuation(text)

    # Load valid English words from NLTK for edit distance
    valid_words = set(words.words())

    dictionary = list(valid_words)

    corrections, results = combined_correction(preprocessed_texts, dictionary)
    json_output = format_output_as_json(text, corrections, results)

    return json_output

if __name__ == '__main__':
    app.run(debug=True)
