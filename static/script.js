const gameGrid = document.getElementById('game-grid');
const scoreDisplay = document.getElementById('score');
const resetButton = document.getElementById('reset-button');

let TILE_SIZE = 100; // Default, will be updated
let PADDING = 10;    // Default, will be updated
let currentBoardSize = 4; // Default, will be updated
let currentTargetTileValue = 2048; // Default, will be updated

document.addEventListener('DOMContentLoaded', () => {
    // Read game settings from localStorage or use defaults
    currentBoardSize = parseInt(localStorage.getItem('board-size')) || 4;
    currentTargetTileValue = parseInt(localStorage.getItem('game-mode')) || 2048;

    // Adjust TILE_SIZE and PADDING based on board size for rendering
    const maxGridDimension = 450; // Max width/height for the grid area (e.g., for 4x4 grid)
    
    PADDING = 10; // Keep padding fixed for now
    TILE_SIZE = (maxGridDimension - ((currentBoardSize + 1) * PADDING)) / currentBoardSize;
    
    // Set game grid dimensions
    gameGrid.style.width = `${currentBoardSize * (TILE_SIZE + PADDING) + PADDING}px`;
    gameGrid.style.height = `${currentBoardSize * (TILE_SIZE + PADDING) + PADDING}px`;


    getGameState().then(renderGame);

    document.addEventListener('keydown', async (e) => {
        let direction = '';
        if (e.key === 'ArrowLeft') {
            direction = 'left';
        } else if (e.key === 'ArrowRight') {
            direction = 'right';
        } else if (e.key === 'ArrowUp') {
            direction = 'up';
        } else if (e.key === 'ArrowDown') {
            direction = 'down';
        }

        if (direction) {
            const newState = await sendMove(direction);
            renderGame(newState);
        }
    });

    resetButton.addEventListener('click', async () => {
        const newState = await resetGame();
        renderGame(newState);
    });

    const modeToggleButton = document.getElementById('mode-toggle-button');
    const body = document.body;

    // Check for saved mode in localStorage
    const savedMode = localStorage.getItem('theme-mode');
    if (savedMode === 'dark') {
        body.classList.add('dark-mode');
    } else {
        body.classList.remove('dark-mode');
    }

    const settingsButton = document.getElementById('settings-button');

    settingsButton.addEventListener('click', () => {
        // Add 'pulled' class for animation
        settingsButton.classList.add('pulled');

        // Redirect to settings page
        setTimeout(() => {
            window.location.href = '/settings';
            // Remove 'pulled' class after the animation completes (optional, as page will unload)
            setTimeout(() => {
                settingsButton.classList.remove('pulled');
            }, 300); // Match pull animation duration
        }, 100); // Delay before redirect
    });

    modeToggleButton.addEventListener('click', () => {
        // Add 'pulled' class for animation
        modeToggleButton.classList.add('pulled');

        // Toggle dark mode after a short delay to allow pull animation to start
        setTimeout(() => {
            body.classList.toggle('dark-mode');
            if (body.classList.contains('dark-mode')) {
                localStorage.setItem('theme-mode', 'dark');
            } else {
                localStorage.setItem('theme-mode', 'light');
            }
            // Remove 'pulled' class after the animation completes
            setTimeout(() => {
                modeToggleButton.classList.remove('pulled');
            }, 300); // Match pull animation duration
        }, 100); // Delay before mode toggle
    });
});

async function getGameState() {
    const response = await fetch('/game_state');
    return response.json();
}

async function sendMove(direction) {
    const response = await fetch(`/move/${direction}`, {
        method: 'POST'
    });
    return response.json();
}

async function resetGame() {
    // Send current game settings to backend to reset the game
    const response = await fetch('/reset', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            board_size: currentBoardSize,
            target_tile_value: currentTargetTileValue
        }),
    });
    return response.json();
}

async function renderGame(gameState) {
    console.log('Current Game State:', gameState); // Debugging line
    scoreDisplay.textContent = gameState.score;

    // Store current tiles for animation
    const existingTiles = new Map();
    document.querySelectorAll('.tile').forEach(tileEl => {
        existingTiles.set(tileEl.dataset.id, tileEl);
    });

    // Apply animations
    const animationPromises = [];
    console.log('Animations to apply:', gameState.animations); // Debugging line
    if (gameState.animations) {
        gameState.animations.forEach(anim => {
            const tileEl = existingTiles.get(anim.id);
            if (tileEl) {
                // Use dynamically calculated TILE_SIZE and PADDING
                const startX = anim.start_pos[1] * (TILE_SIZE + PADDING) + PADDING;
                const startY = anim.start_pos[0] * (TILE_SIZE + PADDING) + PADDING;
                const endX = anim.end_pos[1] * (TILE_SIZE + PADDING) + PADDING;
                const endY = anim.end_pos[0] * (TILE_SIZE + PADDING) + PADDING;

                // Set initial position if it's a merge animation (tile might not be at start_pos yet)
                if (anim.is_merge) {
                    tileEl.style.left = `${startX}px`;
                    tileEl.style.top = `${startY}px`;
                }

                // Trigger reflow to ensure transition starts from current position
                tileEl.offsetWidth;

                tileEl.style.transition = 'transform 0.1s ease-out';
                tileEl.style.transform = `translate(${endX - startX}px, ${endY - startY}px)`;

                const promise = new Promise(resolve => {
                    tileEl.addEventListener('transitionend', () => {
                        if (anim.is_merge) {
                            tileEl.remove(); // Remove merged tile after animation
                        }
                        resolve();
                    }, { once: true });
                });
                animationPromises.push(promise);
            }
        });
    }

    await Promise.all(animationPromises);

    // Clear existing tiles and render new grid state after animations
    gameGrid.innerHTML = '';

    // Render empty cells (optional, for visual grid)
    // Loop based on currentBoardSize from gameState or global variable
    for (let i = 0; i < gameState.board_size; i++) {
        for (let j = 0; j < gameState.board_size; j++) {
            const cell = document.createElement('div');
            cell.classList.add('grid-cell');
            // Set cell size dynamically if needed, or rely on CSS
            cell.style.width = `${TILE_SIZE}px`;
            cell.style.height = `${TILE_SIZE}px`;
            cell.style.left = `${j * (TILE_SIZE + PADDING) + PADDING}px`;
            cell.style.top = `${i * (TILE_SIZE + PADDING) + PADDING}px`;
            gameGrid.appendChild(cell);
        }
    }

    // Render tiles
    gameState.grid.forEach((row, i) => {
        row.forEach((cell, j) => {
            if (cell.value !== 0) {
                const tile = document.createElement('div');
                tile.classList.add('tile', `tile-${cell.value}`);
                tile.textContent = cell.value;
                // Use dynamically calculated TILE_SIZE and PADDING
                tile.style.width = `${TILE_SIZE}px`;
                tile.style.height = `${TILE_SIZE}px`;
                tile.style.left = `${j * (TILE_SIZE + PADDING) + PADDING}px`;
                tile.style.top = `${i * (TILE_SIZE + PADDING) + PADDING}px`;
                tile.dataset.id = cell.id; // Store ID for animations

                // 动态调整字体大小
                let fontSize;
                const valueLength = String(cell.value).length;
                if (valueLength <= 2) {
                    fontSize = TILE_SIZE * 0.4; // 两位数及以下，字体较大
                } else if (valueLength === 3) {
                    fontSize = TILE_SIZE * 0.3; // 三位数，字体适中
                } else if (valueLength === 4) {
                    fontSize = TILE_SIZE * 0.2; // 四位数，字体较小
                } else {
                    fontSize = TILE_SIZE * 0.15; // 更多位数，字体更小
                }
                tile.style.fontSize = `${fontSize}px`;
                gameGrid.appendChild(tile);

                // Add new-tile class for pop-in animation
                if (gameState.new_tiles && gameState.new_tiles.some(nt => nt.tile.id === cell.id)) {
                    tile.classList.add('new-tile');
                    // Remove the class after the animation to prevent re-triggering
                    setTimeout(() => {
                        tile.classList.remove('new-tile');
                    }, 200); // Match CSS animation duration
                }
            }
        });
    });

    // 使用标志变量避免重复显示游戏结束提示
    if ((gameState.game_over || gameState.won) && !window.gameEndAlertShown) {
        window.gameEndAlertShown = true;
        if (gameState.game_over) {
            alert('Game Over! Your score: ' + gameState.score);
        } else if (gameState.won) {
            alert('You Win! Your score: ' + gameState.score);
        }
    }
    
    // 如果游戏重置，重置提示标志
    if (!gameState.game_over && !gameState.won) {
        window.gameEndAlertShown = false;
    }
}


