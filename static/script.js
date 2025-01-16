document.addEventListener('DOMContentLoaded', function () {
    // Authentication Elements
    const signupForm = document.getElementById('signup-form');
    const loginForm = document.getElementById('login-form');
    const logoutButton = document.getElementById('logout-button');

    // Flashcard Elements
    const flashcardForm = document.getElementById('flashcard-form');
    const flashcardsContainer = document.getElementById('flashcards-container');
    const savedFlashcardsContainer = document.getElementById('saved-flashcards-container');

    // Helper function to toggle visibility
    function toggleAuth(isLoggedIn) {
        signupForm.style.display = isLoggedIn ? 'none' : 'block';
        loginForm.style.display = isLoggedIn ? 'none' : 'block';
        logoutButton.style.display = isLoggedIn ? 'block' : 'none';
        flashcardForm.style.display = isLoggedIn ? 'block' : 'none';
    }

    // Check login status (Mock implementation)
    let isLoggedIn = false;
    toggleAuth(isLoggedIn);

    // Signup Handler
    signupForm.addEventListener('submit', async function (e) {
        e.preventDefault();

        const username = document.getElementById('signup-username').value;
        const password = document.getElementById('signup-password').value;

        try {
            const response = await fetch('/signup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();
            alert(data.message || data.error);
        } catch (error) {
            alert('Error signing up: ' + error.message);
        }
    });

    // Login Handler
    loginForm.addEventListener('submit', async function (e) {
        e.preventDefault();

        const username = document.getElementById('login-username').value;
        const password = document.getElementById('login-password').value;

        try {
            const response = await fetch('/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();

            if (response.ok) {
                isLoggedIn = true;
                toggleAuth(isLoggedIn);
                loadSavedFlashcards();
            }

            alert(data.message || data.error);
        } catch (error) {
            alert('Error logging in: ' + error.message);
        }
    });

    // Logout Handler
    logoutButton.addEventListener('click', async function () {
        try {
            const response = await fetch('/logout', {
                method: 'GET'
            });

            const data = await response.json();

            if (response.ok) {
                isLoggedIn = false;
                toggleAuth(isLoggedIn);
                savedFlashcardsContainer.innerHTML = '';
            }

            alert(data.message || data.error);
        } catch (error) {
            alert('Error logging out: ' + error.message);
        }
    });

    // Generate Flashcards Handler
    flashcardForm.addEventListener('submit', async function (e) {
        e.preventDefault();

        const topic = document.getElementById('topic').value;
        flashcardsContainer.innerHTML = '<p>Generating flashcards...</p>';

        try {
            const response = await fetch('/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ topic })
            });

            const data = await response.json();

            if (response.ok) {
                flashcardsContainer.innerHTML = '';
                const flashcards = data.flashcards.split('\n');
                const flashcardsText = flashcards.join('\n');

                flashcards.forEach((flashcard) => {
                    const cardDiv = document.createElement('div');
                    cardDiv.className = 'flashcard';
                    cardDiv.textContent = flashcard.trim();
                    flashcardsContainer.appendChild(cardDiv);
                });

                const saveButton = document.createElement('button');
                saveButton.textContent = 'Save Flashcards';
                saveButton.className = 'save-button';
                saveButton.onclick = async () => {
                    try {
                        const saveResponse = await fetch('/save', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ topic, flashcards: flashcardsText })
                        });

                        const saveData = await saveResponse.json();
                        alert(saveData.message || saveData.error);
                    } catch (error) {
                        alert('Error saving flashcards: ' + error.message);
                    }
                };
                flashcardsContainer.appendChild(saveButton);
            } else {
                flashcardsContainer.innerHTML = `<p class="error">${data.error}</p>`;
            }
        } catch (error) {
            flashcardsContainer.innerHTML = `<p class="error">Error: ${error.message}</p>`;
        }
    });

    // Load Saved Flashcards
    async function loadSavedFlashcards() {
        savedFlashcardsContainer.innerHTML = '<p>Loading saved flashcards...</p>';

        try {
            const response = await fetch('/flashcards');
            const data = await response.json();

            if (response.ok) {
                savedFlashcardsContainer.innerHTML = '';
                data.forEach(({ topic, flashcards }) => {
                    const cardDiv = document.createElement('div');
                    cardDiv.className = 'saved-flashcard';
                    cardDiv.innerHTML = `<h3>${topic}</h3><p>${flashcards}</p>`;
                    savedFlashcardsContainer.appendChild(cardDiv);
                });
            } else {
                savedFlashcardsContainer.innerHTML = `<p class="error">${data.error}</p>`;
            }
        } catch (error) {
            savedFlashcardsContainer.innerHTML = `<p class="error">Error: ${error.message}</p>`;
        }
    }

    // Initialize by checking login state
    if (isLoggedIn) {
        loadSavedFlashcards();
    }
});
