function submitForm(event) {
    event.preventDefault(); // Prevent default form submission

    const textArea = document.getElementById('text_input');
    const textValue = textArea.value.trim();

    if (textValue === '') {
        alert('Please enter some text before submitting.');
        return;
    }

    // Create JSON object
    const result = {
        text: textValue,
        length: textValue.length
    };

    // Display JSON object
    const resultDiv = document.getElementById('result');
    resultDiv.innerHTML = `<pre>${JSON.stringify(result, null, 2)}</pre>`;

    // Optionally reset the form
    textArea.value = '';
}

function submitForm(event) {
    event.preventDefault(); // Prevent default form submission

    const form = document.getElementById('textForm');
    const formData = new FormData(form);

    fetch('/submit', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        // Display the processed text
        document.getElementById('result').innerHTML = `Processed Text: ${data.processed_text}`;
    })
    .catch(error => console.error('Error:', error));
}

// function submitForm(event) {
//     event.preventDefault(); // Prevent default form submission

//     const form = document.getElementById('form');
//     const formData = new FormData(form);

//     fetch('/form', {
//         method: 'POST',
//         body: formData
//     })
//     .then(response => response.json())
//     .then(data => {
//         // Display the result message
//         const resultDiv = document.getElementById('result');
//         resultDiv.innerHTML = `<p>${data.message}</p>`;

//         // Create a list to display the parts
//         const partsList = document.createElement('div');

//         // Iterate over the parts data
//         data.parts.forEach(part => {
//             const listItem = document.createElement('div');
            
//             // Create a button element for items with status 1, or a plain span for others
//             if (part.status === 1) {
//                 const button = document.createElement('button');
//                 button.textContent = part.text;
//                 button.className = 'btn btn-danger'; // Bootstrap class for highlighted button
//                 button.style.margin = '2px';
//                 button.addEventListener('click', () => {
//                     alert(`Clicked on: ${part.text}`);
//                     // Add additional functionality for button click here
//                 });
//                 listItem.appendChild(button);
//             } else {
//                 const span = document.createElement('span');
//                 span.textContent = part.text;
//                 span.className = 'btn btn-light'; // Bootstrap class for non-clickable text
//                 span.style.margin = '2px';
//                 listItem.appendChild(span);
//             }
            
//             // Append list item to the list
//             partsList.appendChild(listItem);
//         });

//         // Add the list to the results div
//         const resultsDiv = document.getElementById('result');
//         resultsDiv.innerHTML = ''; // Clear previous content
//         resultsDiv.appendChild(partsList);
            
//         // Clear the form input
//         form.reset();
//     })
//     .catch(error => console.error('Error:', error));
// }

// $(document).ready(function() {
//     // Example data
//     const optionsData = [
//         { id: 1, text: "my", status: 0 },
//         { id: 2, text: "nama", status: 1 },
//         { id: 3, text: "is", status: 0 },
//         { id: 4, text: "Fahri", status: 0 }
//     ];

//     // Initialize Select2
//     $('#exampleSelect').select2({
//         placeholder: 'Select options',
//         allowClear: true,
//         data: optionsData,
//         dropdownCssClass: 'select2-dropdown-custom', // Apply custom dropdown styles
//         templateResult: formatOption // Custom formatting function
//     });

//     // Function to format each option
//     function formatOption(option) {
//         if (!option.id) {
//             return option.text;
//         }

//         // Apply custom styles based on status
//         const $option = $(
//             `<span class="${option.status === 1 ? 'highlighted-option' : ''}">${option.text}</span>`
//         );

//         return $option;
//     }
// });