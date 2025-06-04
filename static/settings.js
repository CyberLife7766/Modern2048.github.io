document.addEventListener('DOMContentLoaded', () => {
    // --- Dark/Light Mode Toggle Logic --- 红
    const modeToggleCheckbox = document.getElementById('mode-toggle-checkbox');
    const body = document.body;

    // Set initial state based on localStorage
    if (localStorage.getItem('theme-mode') === 'dark') {
        body.classList.add('dark-mode');
        modeToggleCheckbox.checked = true; // Set checkbox state
    } else {
        body.classList.remove('dark-mode');
        modeToggleCheckbox.checked = false; // Set checkbox state
    }

    modeToggleCheckbox.addEventListener('change', () => { // Change event for checkbox
        body.classList.toggle('dark-mode');
        if (body.classList.contains('dark-mode')) {
            localStorage.setItem('theme-mode', 'dark');
        } else {
            localStorage.setItem('theme-mode', 'light');
        }
    });

    // --- Game Mode and Board Size Selection Logic ---
    const gameModeSelect = document.getElementById('game-mode-select');
    const boardSizeSelect = document.getElementById('board-size-select');

    // Set initial state based on localStorage or defaults
    let currentMode = localStorage.getItem('game-mode') || '2048';
    let currentBoardSize = localStorage.getItem('board-size') || '4';

    gameModeSelect.value = currentMode;
    boardSizeSelect.value = currentBoardSize;

    gameModeSelect.addEventListener('change', () => {
        localStorage.setItem('game-mode', gameModeSelect.value);
    });

    boardSizeSelect.addEventListener('change', () => {
        localStorage.setItem('board-size', boardSizeSelect.value);
    });

    // --- Back Button Logic ---
    const backButton = document.getElementById('back-button');
    backButton.addEventListener('click', () => {
        // Get current game settings from localStorage
        const selectedMode = localStorage.getItem('game-mode') || '2048';
        const selectedBoardSize = localStorage.getItem('board-size') || '4';

        // Send settings to backend to reset the game
        fetch('/reset', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                board_size: parseInt(selectedBoardSize),
                target_tile_value: parseInt(selectedMode)
            }),
        })
        .then(response => response.json())
        .then(data => {
            console.log('Game reset with new settings:', data);
            window.location.href = '/'; // Go back to the main game page after reset
        })
        .catch(error => {
            console.error('Error resetting game:', error);
            window.location.href = '/'; // Still go back even if there's an error
        });
    });
});
