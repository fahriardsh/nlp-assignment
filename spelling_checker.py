# Import flask for jsonify
from flask import jsonify

# Import nltk for downloading the necessary NLTK resources
import nltk

from nltk.tokenize import word_tokenize, RegexpTokenizer
from nltk.corpus import words

# Import os for getting the path to the bigram model
import os
# Import pickle for loading the bigram model
import pickle

from transformers import BertTokenizer, BertForMaskedLM
import torch

print("Loading BERT model...")
# Load BERT model and tokenizer once
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertForMaskedLM.from_pretrained('bert-base-uncased')
model.eval()  # Set the model to evaluation mode since we are only doing inference

# Get the path to the bigram model
bigram_model_path = os.path.join(os.path.dirname(__file__), 'data', 'bigram_model.pkl')

print("Loading Bigram model...")
# Open the file and load the bigram model
with open(bigram_model_path, 'rb') as f:
    bigram_model = pickle.load(f)

# Function to remove punctuation using NLTK
def remove_punctuation(text):
    tokenizer = RegexpTokenizer(r'\w+')
    return ' '.join(tokenizer.tokenize(text))

def suggest_corrections_nltk(word, dictionary, n=3):
    suggestions = []

    # Calculate edit distance and similarity percentage for each word in the dictionary
    for dict_word in dictionary:
        distance = nltk.edit_distance(word, dict_word)
        max_len = max(len(word), len(dict_word))
        similarity_percentage = 100 * (1 - (distance / max_len))

        # Append suggestion with similarity percentage
        suggestions.append({
            "word": dict_word,
            "similarity": round(similarity_percentage, 2)
        })

    # Sort suggestions by highest similarity percentage
    suggestions.sort(key=lambda x: x["similarity"], reverse=True)

    # Return top n suggestions
    return suggestions[:n]

# Function to check bigram context
def check_bigram_context(word, prev_word, next_word):
    # Get bigram frequencies
    bigram = (prev_word, word, next_word)
    return bigram_model[bigram] > 0

# Function to use BERT for predicting a masked word
def predict_with_bert(text, word_to_check):
    masked_text = text.replace(word_to_check, '[MASK]', 1)  # Replace the word to check with [MASK]
    
    inputs = tokenizer.encode(masked_text, return_tensors='pt')  # Tokenize the input text
    mask_token_index = torch.where(inputs == tokenizer.mask_token_id)[1]  # Find the [MASK] position
    
    with torch.no_grad():
        outputs = model(inputs)
        logits = outputs.logits
    
    predicted_token_id = torch.argmax(logits[0, mask_token_index, :], dim=-1)
    predicted_word = tokenizer.decode(predicted_token_id)

    return predicted_word.strip()  # Return the predicted word without spaces

# Combined correction function with bigram context and BERT
def combined_correction(text, dictionary):
    text = remove_punctuation(text)  # Remove punctuation
    tokens = nltk.word_tokenize(text.lower())
    corrections = {}
    results = []

    for i, token in enumerate(tokens):
        # Skip known words to focus on potential errors
        if token not in set(words.words()):
            prev_word = tokens[i-1] if i > 0 else '<sos>'
            next_word = tokens[i+1] if i < len(tokens) - 1 else '<eos>'

            # Check if BERT predicts the word correctly based on context
            predicted_word = predict_with_bert(text, token)
            is_error = (predicted_word != token)  # If BERT predicts something different, it's likely an error

            if is_error:
                # Use NLTK-based suggestions if BERT indicates an error
                suggestions = suggest_corrections_nltk(token, dictionary)
                if suggestions:
                    corrections[token] = suggestions
                results.append({
                    "word": token,
                    "label": 1,
                    "bert_suggestion": predicted_word
                })
            else:
                results.append({
                    "word": token,
                    "label": 0,
                    "bert_suggestion": predicted_word
                })
        else:
            results.append({
                "word": token,
                "label": 0,
                "bert_suggestion": token  # If BERT doesn't think it's wrong, assume it's correct
            })

    return corrections, results

# Combined correction function with bigram context
# def combined_correction(text, dictionary):
#     text = remove_punctuation(text)  # Remove punctuation
#     tokens = nltk.word_tokenize(text.lower())
#     corrections = {}
#     results = []

#     for i, token in enumerate(tokens):
#         # Skip known words to focus on potential errors
#         if token not in set(words.words()):
#             prev_word = tokens[i-1] if i > 0 else '<sos>'
#             next_word = tokens[i+1] if i < len(tokens) - 1 else '<eos>'

#             is_error = not check_bigram_context(token, prev_word, next_word)
#             if is_error:
#                 suggestions = suggest_corrections_nltk(token, dictionary)
#                 # suggestions = suggest_corrections(token, dictionary)
#                 if suggestions:
#                     corrections[token] = suggestions
#                 results.append({
#                     "word": token,
#                     "label": 1
#                 })
#         else:
#             results.append({
#                 "word": token,
#                 "label": 0
#             })

#     return corrections, results

def format_output_as_json(original_text, corrections, results):

    # Use Gramformer for grammar correction
    gf_correction = list(gf.correct(sample_text))
    gf_suggestion = gf_correction[:3] if gf_correction else sample_text  # Get the first suggestion from Gramformer

    # Remove duplicates based on 'word' key
    seen_words = set()
    unique_data = []
    for item in results:
        word = item['word']
        if word not in seen_words:
            unique_data.append(item)
            seen_words.add(word)

    # Sort the list alphabetically by 'word' key
    sorted_data = sorted(unique_data, key=lambda x: x['word'].lower())

    output = {
        "original": original_text,
        "dictionary": sorted_data,
        "suggestion": corrections
    }

    return jsonify(output)