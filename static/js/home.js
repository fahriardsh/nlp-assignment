// script.js

// Wait until the DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    const textForm = document.getElementById('textForm');
    const textInput = document.getElementById('text_input');
    const highlightedResult = document.getElementById('highlightedResult');
    const highlightedText = document.getElementById('highlightedText');
    const suggestedText = document.getElementById('suggestedText');
    const dictionarySection = document.getElementById('dictionarySection');
    const dictionaryResult = document.getElementById('dictionaryResult');
    const searchInput = document.getElementById('searchInput');
    const suggestionResult = document.getElementById('suggestionResult');
    let dictionaryData = [];
    let suggestionData = [];
    // let suggestionData = {};

    // Event listener for form submission
    textForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const text = getTextInput();
        if (text) {
            fetchData(text);
        }
    });

    // Event listener for search input
    searchInput.addEventListener('input', () => {
        const query = searchInput.value.trim().toLowerCase();
        displayDictionary(filterDictionary(query), suggestionData);
    });

    // Get text input from the form
    function getTextInput() {
        const text = textInput.value.trim();
        if (text.length === 0) {
            alert('Please enter some text before submitting.');
            return null;
        }
        return text;
    }

    // Fetch data from the server
    function fetchData(text) {

        // Hide all sections
        document.getElementById('highlightedResult').style.display = 'none';
        document.getElementById('dictionarySection').style.display = 'none';
        document.getElementById('suggestionSection').style.display = 'none';

        // Clear previous suggestion results
        suggestionResult.innerHTML = '';

        // Show loading spinner
        document.getElementById('loadingSpinner').style.display = 'block';

        fetch('/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text_input: text })
        })
        .then(response => response.json())
        .then(data => {

            console.log(data);
            
            dictionaryData = data.results;
            suggestionData = data.corrections;
            displayHighlightedText(data.input_text, dictionaryData);
            displaySuggestedText(data.gf_suggestion)
            displayDictionary(dictionaryData, suggestionData);
            highlightedResult.classList.remove('hidden');
            dictionarySection.classList.remove('hidden');
            searchInput.value = '';

            // Hide loading spinner
            document.getElementById('loadingSpinner').style.display = 'none';

            // // Show sections
            document.getElementById('highlightedResult').style.display = 'block';
            document.getElementById('dictionarySection').style.display = 'block';
            document.getElementById('suggestionSection').style.display = 'block';

        })
        .catch(error => {
            console.error('Error fetching data:', error);
            alert('An error occurred while processing your request.');
        });
    }

    // Display highlighted text
    function displayHighlightedText(text, dictionary) {
        const words = text.split(/\s+/);
        const wordMap = createWordMap(dictionary);

        const processedText = words.map(word => {
            const cleanWord = word.replace(/[^\w]/g, '').toLowerCase();
            if (wordMap[cleanWord] === 1) {
                return `<span class="highlight">${word}</span>`;
            }
            return word;
        }).join(' ');

        highlightedText.innerHTML = processedText;
    }

    // Display suggested text
    function displaySuggestedText(text) {
        
        if (text.length === 0) {
            suggestedText.innerHTML = '';
            return;
        } else (text = 'Did you mean: ' + `<div style="color: grey; font-style: italic;">${text}</div>`) 

        suggestedText.innerHTML = text;

    }

    // Create a map from words to labels
    function createWordMap(dictionary) {
        const map = {};
        dictionary.forEach(item => {
            map[item.word.toLowerCase()] = item.label;
        });
        return map;
    }

    // Display dictionary words
    function displayDictionary(dictionary, suggestions) {
        dictionaryResult.innerHTML = '';
        if (dictionary.length === 0) {
            dictionaryResult.innerHTML = '<div class="item">No words found.</div>';
            return;
        }

        dictionary.forEach(item => {
            const div = document.createElement('div');
            div.classList.add('item');
            if (item.label === 1) {
                div.classList.add('clickable');
                div.addEventListener('click', () => {
                    displaySuggestions(item.word, suggestions);
                });
            }
            div.textContent = item.word;
            dictionaryResult.appendChild(div);
        });
    }

    // Display suggestions based on clicked word
    function displaySuggestions(word, suggestions) {
        suggestionResult.innerHTML = ''; // Clear previous suggestions
        const suggestionList = suggestions[word] || [];

        if (suggestionList.length === 0) {
            suggestionResult.innerHTML = '<div class="item">No suggestions available.</div>';
        } else {
            suggestionList.forEach(suggestion => {
                const div = document.createElement('div');
                div.classList.add('item');
                
                // Create a span to display the word and attach a popup with the similarity value
                const wordSpan = document.createElement('span');
                wordSpan.textContent = suggestion.word;
                wordSpan.classList.add('ui', 'popup-trigger');  // Class to activate the popup
                
                // Add the Semantic UI popup with the similarity
                $(wordSpan).attr('data-content', `Similarity: ${suggestion.similarity}%`);
                $(wordSpan).popup();  // Activate the popup
            
                // Append the wordSpan to the div
                div.appendChild(wordSpan);
            
                // Append the div to the suggestionResult container
                suggestionResult.appendChild(div);
            });
        }
    }

    // Filter dictionary based on search query
    function filterDictionary(query) {
        if (!query) return dictionaryData;
        return dictionaryData.filter(item => item.word.toLowerCase().includes(query));
    }
});
