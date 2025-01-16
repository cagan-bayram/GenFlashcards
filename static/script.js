document.getElementById('flashcard-form').addEventListener('submit', async function (e) {
    e.preventDefault();
    
    const topic = document.getElementById('topic').value;
    const flashcardsContainer = document.getElementById('flashcards-container');
    flashcardsContainer.innerHTML = "<p>Generating flashcards...</p>";

    try {
        const response = await fetch('/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ topic })
        });
        
        const data = await response.json();

        if (response.ok) {
            flashcardsContainer.innerHTML = "";
            const flashcards = data.flashcards.split('\n');
            flashcards.forEach((flashcard) => {
                const cardDiv = document.createElement('div');
                cardDiv.className = 'flashcard';
                cardDiv.textContent = flashcard.trim();
                flashcardsContainer.appendChild(cardDiv);
            });
        } else {
            flashcardsContainer.innerHTML = `<p class="error">${data.error}</p>`;
        }
    } catch (error) {
        flashcardsContainer.innerHTML = `<p class="error">Error: ${error.message}</p>`;
    }
});