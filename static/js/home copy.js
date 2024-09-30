// script.js

// Wait until the DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    const textForm = document.getElementById('textForm');
    const textInput = document.getElementById('text_input');
    const highlightedResult = document.getElementById('highlightedResult');
    const highlightedText = document.getElementById('highlightedText');
    const dictionarySection = document.getElementById('dictionarySection');
    const dictionaryResult = document.getElementById('dictionaryResult');
    const searchInput = document.getElementById('searchInput');
    const suggestionSection = document.getElementById('suggestionSection');
    const suggestionResult = document.getElementById('suggestionResult');
    let dictionaryData = [];

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
        displayDictionary(filterDictionary(query));
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
        fetch('/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text_input: text })
        })
        .then(response => response.json())
        .then(data => {
            dictionaryData = data.dictionary;
            suggestionData = data.suggestion;
            displayHighlightedText(data.original, data.dictionary);
            displayDictionary(dictionaryData, suggestionData);
            highlightedResult.classList.remove('hidden');
            dictionarySection.classList.remove('hidden');
            // suggestionSection.classList.remove('hidden');
            searchInput.value = '';
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

    // Create a map from words to labels
    function createWordMap(dictionary) {
        const map = {};
        dictionary.forEach(item => {
            map[item.word.toLowerCase()] = item.label;
        });
        return map;
    }

    // Display dictionary words
    // function displayDictionary(dictionary, suggestion) {
    //     dictionaryResult.innerHTML = '';
    //     if (dictionary.length === 0) {
    //         dictionaryResult.innerHTML = '<div class="item">No words found.</div>';
    //         return;
    //     }

    //     dictionary.forEach(item => {
    //         const div = document.createElement('div');
    //         div.classList.add('item');
    //         if (item.label === 1) {
    //             div.classList.add('clickable');
    //             div.addEventListener('click', () => {
    //                 displaySuggestions(item.word, suggestion[item.word])
    //                 // console.log(suggestion[item.word])
    //             });
    //         }
    //         div.textContent = item.word;
    //         dictionaryResult.appendChild(div);
    //     });
    // }

    function displayDictionary(dictionary) {
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
                    displaySuggestions(item.word);
                });
            }
            div.textContent = item.word;
            dictionaryResult.appendChild(div);
        });
    }

    // Filter dictionary based on search query
    function filterDictionary(query) {
        if (!query) return dictionaryData;
        return dictionaryData.filter(item => item.word.toLowerCase().includes(query));
    }

    // Display suggestions for a clicked word
    // function displaySuggestions(word, suggestions) {
    //     suggestionResult.innerHTML = `<h4>Suggestions for "${word}":</h4>`;
        
    //     if (suggestions && suggestions.length > 0) {
    //         const ul = document.createElement('ul');
    //         suggestions.forEach(suggestion => {
    //             const li = document.createElement('li');
    //             li.textContent = suggestion;
    //             li.addEventListener('click', () => {
    //                 replaceWordInText(word, suggestion);
    //             });
    //             ul.appendChild(li);
    //         });
    //         suggestionResult.appendChild(ul);
    //     } else {
    //         suggestionResult.innerHTML += '<p>No suggestions available.</p>';
    //     }
    // }

    // Display suggestions based on clicked word
    function displaySuggestions(word) {
        suggestionResult.innerHTML = ''; // Clear previous suggestions
        const suggestions = dataJSON.suggestion[word] || [];
        
        if (suggestions.length === 0) {
            suggestionResult.innerHTML = '<div class="item">No suggestions available.</div>';
        } else {
            suggestions.forEach(suggestion => {
                const div = document.createElement('div');
                div.classList.add('item');
                div.textContent = suggestion;
                suggestionResult.appendChild(div);
            });
        }
    }

    // Replace the clicked word with the selected suggestion in the original text
    function replaceWordInText(originalWord, newWord) {
        let text = highlightedText.innerHTML;
        const regex = new RegExp(`\\b${originalWord}\\b`, 'gi');
        text = text.replace(regex, newWord);
        highlightedText.innerHTML = text;
    }
});
