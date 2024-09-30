from transformers import AlbertTokenizer, AlbertForMaskedLM # type: ignore
import torch

from gramformer import Gramformer # type: ignore

# Import os for getting the path to the bigram model
import os
# Import pickle for loading the bigram model
import pickle

import nltk
from nltk.metrics import edit_distance
from nltk import bigrams, FreqDist
from nltk.tokenize import RegexpTokenizer

import json

# Load ALBERT model and tokenizer
print("Loading ALBERT ...")
# Load fine-tuned ALBERT model and tokenizer
tokenizer = AlbertTokenizer.from_pretrained('data/fine_tuned_albert')
model = AlbertForMaskedLM.from_pretrained('data/fine_tuned_albert')

# Load Gramformer
print("Loading Gramformer ...")
# Initialize the Gramformer model (ensure internet connection to download the model)
gf = Gramformer(models=1)  # 1 indicates grammar error correction model

# Load Bigram
print("Loading Bigram ...")
# Get the path to the bigram model
bigram_model_path = os.path.join(os.path.dirname(__file__), 'data', 'bigram_model.pkl')
# Open the file and load the bigram model
with open(bigram_model_path, 'rb') as f:
    bigram_model = pickle.load(f)



# Function to calculate similarity percentage using edit distance
def calculate_similarity(word1, word2):
    max_len = max(len(word1), len(word2))
    distance = edit_distance(word1, word2)
    similarity_percentage = 100 * (1 - (distance / max_len))
    return round(similarity_percentage, 2)

# Function to extract the relevant word from Gramformer's suggestion
def extract_gramformer_word(original_word, sentence_suggestion):
    words_in_suggestion = sentence_suggestion.split()
    for word in words_in_suggestion:
        # Check if a word in the suggestion is similar to the original word
        if word.lower().startswith(original_word[0].lower()):  # Simple heuristic
            return word
    return original_word  # Fallback to the original word if no match

# Function to remove punctuation using NLTK
def remove_punctuation(text):
    tokenizer = RegexpTokenizer(r'\w+')
    return ' '.join(tokenizer.tokenize(text))

# Function to provide NLTK-based suggestions using edit distance
def suggest_corrections_nltk(word, dictionary, n=3):
    suggestions = []

    # Convert the input word to a string (just in case)
    word = str(word)

    # Calculate edit distance and similarity percentage for each word in the dictionary
    for dict_word in dictionary:
        # Make sure the dictionary word is a string
        if isinstance(dict_word, str):
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

# Train the bigram model using a corpus
# bigram_freq = FreqDist(bigrams(corpus))

# Function to check if a bigram is common based on its frequency
def check_bigram_context(prev_word, word):
    return bigram_model[(prev_word, word)] > 0  # True if the bigram occurs in the corpus

# Function to use fine-tuned ALBERT for predicting a masked word
def predict_with_albert(text, word_to_check):
    # Replace the word to check with [MASK]
    masked_text = text.replace(word_to_check, '[MASK]', 1)
    
    inputs = tokenizer.encode(masked_text, return_tensors='pt')  # Tokenize the input text
    mask_token_index = torch.where(inputs == tokenizer.mask_token_id)[1]  # Find the [MASK] position
    
    with torch.no_grad():
        outputs = model(inputs)
        logits = outputs.logits
    
    # Get the predicted token at the [MASK] position
    predicted_token_id = torch.argmax(logits[0, mask_token_index, :], dim=-1)
    predicted_word = tokenizer.decode(predicted_token_id)

    return predicted_word.strip()  # Return the predicted word without spaces

# Function to combine all necessary technique to predict and suggest word
def combined_correction(text, dictionary, corpus):
    text = remove_punctuation(text)  # Remove punctuation
    tokens = nltk.word_tokenize(text.lower())
    corrections = {}
    results = []

    for i, token in enumerate(tokens):
        if token not in corpus:
            prev_word = tokens[i-1] if i > 0 else '<sos>'
            # next_word = tokens[i+1] if i < len(tokens) - 1 else '<eos>'

            # Step 1: Check if ALBERT predicts the word correctly based on context
            predicted_word = predict_with_albert(text, token)
            is_error = (predicted_word != token)

            # Step 2: Use bigram model to verify context
            if i > 0 and check_bigram_context(prev_word, predicted_word) == False:
                is_error = True

            # Step 3: Use Gramformer for grammar correction
            gf_correction = list(gf.correct(text))
            gf_suggestions = gf_correction[0] if len(gf_correction) > 0 else [text]

            print(gf_correction)
            print(gf_suggestions)

            if is_error:
                # Step 4: Extract relevant word from Gramformer’s suggestion
                relevant_word = extract_gramformer_word(token, gf_suggestions)

                # Step 5: Use NLTK-based suggestions for edit distance suggestions
                suggestions = suggest_corrections_nltk(token, dictionary)

                # Step 6: Add Gramformer’s word to the corrections if it's not already present
                if relevant_word not in [s['word'] for s in suggestions]:
                    similarity = calculate_similarity(token, relevant_word)
                    suggestions.append({
                        "word": relevant_word,
                        "similarity": similarity
                    })

                # Step 7: Filter out suggestions with similarity below 60%
                filtered_suggestions = [s for s in suggestions if 50.0 <= s["similarity"] < 100.0]

                corrections[token] = filtered_suggestions
                results.append({
                    "word": token,
                    "label": 1,  # Error detected
                    # "albert_suggestion": predicted_word,
                    "bigram_check": check_bigram_context(prev_word, predicted_word),
                    # "gramformer_suggestions": gf_suggestions
                })
            else:
                results.append({
                    "word": token,
                    "label": 0,  # No error detected
                    # "albert_suggestion": predicted_word,
                    "bigram_check": True,
                    # "gramformer_suggestions": gf_suggestions
                })
        else:
            results.append({
                "word": token,
                "label": 0,
                # "albert_suggestion": token,
                "bigram_check": True,
                # "gramformer_suggestions": [token]
            })

    return corrections, results

# Function to format the output as JSON
def format_output_as_json(original_text, corrections, results):

    # Use Gramformer for grammar correction
    gf_correction = list(gf.correct(original_text))
    gf_suggestion = gf_correction[0] if gf_correction else original_text  # Get the first suggestion from Gramformer

    output = {
        "input_text": original_text,
        "gf_suggestion": gf_suggestion,
        "corrections": corrections,
        "results": results
    }
    return json.dumps(output, indent=4)  # Converts the dictionary into a formatted JSON string