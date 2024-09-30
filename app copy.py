from flask import Flask, request, jsonify, render_template
import re
import nltk
nltk.download('punkt')

# Initialize Flask app
app = Flask(__name__)

# Define the preprocess function
def preprocess(text):
    text = text.lower()  # Convert to lowercase
    text = re.sub(r'[^a-z\s]', '', text)  # Remove non-alphabetical characters
    return text

# Route for the form
@app.route('/')
def form():
    return render_template('form.html')

# Route to handle form submission
@app.route('/submit', methods=['POST'])
def submit():
    user_input = request.form['text_input']  # Get the input from the form
    processed_text = preprocess(user_input)  # Apply the preprocess function
    return jsonify({'processed_text': processed_text})  # Return the processed text as JSON


# @app.route('/')
# def home():
#     return render_template('index.html')

# @app.route('/about')
# def about():
#     return 'This is the About page!'

# # Route for the form

# @app.route('/form', methods=['GET', 'POST'])
# def form():
#     if request.method == 'POST':
#         # Static response as per your requirement
#         response_data = {
#             "message": "My Nama is Fahri",
#             "parts": [
#                 {"text": "my", "status": 0},
#                 {"text": "nama", "status": 1},
#                 {"text": "is", "status": 0},
#                 {"text": "Fahri", "status": 0}
#             ]
#         }
#         return jsonify(response_data)
#     return render_template('form.html')

# Route for the home
@app.route('/home')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)