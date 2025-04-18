from flask import Flask, render_template_string
import random

app = Flask(__name__)


@app.route('/')
def index():
    # A short poem to be hidden in the mosaic
    poem = """
    The road not taken by Robert Frost
    Two roads diverged in a yellow wood
    And sorry I could not travel both
    And be one traveler long I stood
    And looked down one as far as I could
    To where it bent in the undergrowth
    """

    # Clean up the poem: remove extra spaces and line breaks
    poem = ' '.join([line.strip() for line in poem.strip().split('\n')])

    # Generate random positions for the letters
    grid_size = 100
    total_cells = grid_size * grid_size

    # Ensure we have enough cells for the poem
    if len(poem) > total_cells:
        poem = poem[:total_cells]

    # Generate unique positions for each letter
    positions = random.sample(range(total_cells), len(poem))

    # Create a mapping of positions to letters
    letter_positions = {}
    for i, pos in enumerate(positions):
        row = pos // grid_size
        col = pos % grid_size
        letter_positions[f"{row},{col}"] = poem[i]

    # Pass the letter positions to the template
    return render_template_string(HTML_TEMPLATE,
                                  grid_size=grid_size,
                                  letter_positions=letter_positions)


# HTML template with embedded CSS and JavaScript
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pixel Poetry Mosaic</title>
    <style>
        body, html {
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            font-family: 'Arial', sans-serif;
            background-color: #121212;
            color: #f5f5f5;
        }

        .container {
            display: flex;
            flex-direction: column;
            height: 100vh;
        }

        .header {
            padding: 10px 20px;
            background-color: #1e1e1e;
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 10;
        }

        .title {
            font-size: 24px;
            font-weight: bold;
        }

        .controls {
            display: flex;
            gap: 10px;
        }

        button {
            padding: 8px 15px;
            background-color: #3a3a3a;
            color: #f5f5f5;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            transition: background-color 0.3s;
        }

        button:hover {
            background-color: #4a4a4a;
        }

        .mosaic-container {
            flex-grow: 1;
            overflow: hidden;
            position: relative;
        }

        .mosaic {
            position: absolute;
            display: grid;
            grid-template-columns: repeat({{ grid_size }}, 1fr);
            transform-origin: center;
            transition: transform 0.3s ease;
        }

        .pixel {
            width: 20px;
            height: 20px;
            background-color: #2a2a2a;
            border: 1px solid #3a3a3a;
            box-sizing: border-box;
            display: flex;
            justify-content: center;
            align-items: center;
            cursor: pointer;
            transition: background-color 0.2s;
        }

        .pixel:hover {
            background-color: #3a3a3a;
        }

        .pixel.revealed {
            background-color: #4a4a4a;
        }

        .letter {
            font-size: 12px;
            font-weight: bold;
            color: #f5f5f5;
            opacity: 0;
            transition: opacity 0.3s;
        }

        .pixel.revealed .letter {
            opacity: 1;
        }

        .footer {
            padding: 10px 20px;
            background-color: #1e1e1e;
            text-align: center;
            font-size: 12px;
            z-index: 10;
        }

        .zoom-controls {
            position: absolute;
            bottom: 20px;
            right: 20px;
            display: flex;
            flex-direction: column;
            gap: 10px;
            z-index: 10;
        }

        .zoom-btn {
            width: 40px;
            height: 40px;
            font-size: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: rgba(60, 60, 60, 0.7);
            border-radius: 50%;
        }

        .message {
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            background-color: rgba(0, 0, 0, 0.7);
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            z-index: 100;
            opacity: 0;
            transition: opacity 0.5s;
        }

        .message.show {
            opacity: 1;
        }

        /* Progress indicator for revealed letters */
        .progress-container {
            margin-left: 20px;
            flex-grow: 1;
            height: 10px;
            background-color: #3a3a3a;
            border-radius: 5px;
            overflow: hidden;
        }

        .progress-bar {
            height: 100%;
            background-color: #4a90e2;
            width: 0%;
            transition: width 0.3s ease;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="title">Pixel Poetry Mosaic</div>
            <div class="progress-container">
                <div class="progress-bar" id="progress"></div>
            </div>
            <div class="controls">
                <button id="reset-btn">Reset Mosaic</button>
            </div>
        </div>

        <div class="mosaic-container" id="mosaic-container">
            <div class="mosaic" id="mosaic"></div>
        </div>

        <div class="footer">
            Click on pixels to reveal letters of a hidden poem. Your progress is saved automatically.
        </div>

        <div class="zoom-controls">
            <button class="zoom-btn" id="zoom-in">+</button>
            <button class="zoom-btn" id="zoom-out">-</button>
            <button class="zoom-btn" id="zoom-reset">⟳</button>
        </div>
    </div>

    <div class="message" id="message"></div>

    <script>
        // Letter positions from Flask
        const letterPositions = {{ letter_positions|tojson }};
        const gridSize = {{ grid_size }};

        // DOM elements
        const mosaic = document.getElementById('mosaic');
        const mosaicContainer = document.getElementById('mosaic-container');
        const resetBtn = document.getElementById('reset-btn');
        const zoomInBtn = document.getElementById('zoom-in');
        const zoomOutBtn = document.getElementById('zoom-out');
        const zoomResetBtn = document.getElementById('zoom-reset');
        const progressBar = document.getElementById('progress');
        const messageEl = document.getElementById('message');

        // State variables
        let scale = 1;
        let offsetX = 0;
        let offsetY = 0;
        let isDragging = false;
        let startPosX = 0;
        let startPosY = 0;
        let revealedCount = 0;
        let totalLetters = Object.keys(letterPositions).length;

        // Storage key
        const storageKey = 'pixel-poetry-mosaic';
        const resetTimeKey = 'pixel-poetry-reset-time';

        // Constants
        const RESET_INTERVAL_DAYS = 7; // Reset every week

        // Initialize the mosaic
        function initMosaic() {
            // Check if reset is needed
            checkResetSchedule();

            // Create the grid
            mosaic.style.width = `${gridSize * 20}px`;
            mosaic.style.height = `${gridSize * 20}px`;

            // Center the mosaic initially
            centerMosaic();

            // Load saved state
            const savedState = loadState();

            // Create pixels
            for (let row = 0; row < gridSize; row++) {
                for (let col = 0; col < gridSize; col++) {
                    const pixel = document.createElement('div');
                    pixel.className = 'pixel';
                    pixel.dataset.row = row;
                    pixel.dataset.col = col;

                    const position = `${row},${col}`;
                    const letter = letterPositions[position];

                    if (letter) {
                        const letterSpan = document.createElement('span');
                        letterSpan.className = 'letter';
                        letterSpan.textContent = letter;
                        pixel.appendChild(letterSpan);

                        // Apply saved state if exists
                        if (savedState && savedState[position] === true) {
                            pixel.classList.add('revealed');
                            revealedCount++;
                        }
                    }

                    pixel.addEventListener('click', handlePixelClick);
                    mosaic.appendChild(pixel);
                }
            }

            // Update progress bar
            updateProgress();
        }

        // Handle pixel click
        function handlePixelClick(event) {
            const pixel = event.currentTarget;
            const row = pixel.dataset.row;
            const col = pixel.dataset.col;
            const position = `${row},${col}`;

            // Check if this pixel contains a letter
            if (letterPositions[position]) {
                const wasRevealed = pixel.classList.contains('revealed');

                if (wasRevealed) {
                    pixel.classList.remove('revealed');
                    revealedCount--;
                } else {
                    pixel.classList.add('revealed');
                    revealedCount++;
                }

                // Save state
                saveState(position, !wasRevealed);

                // Update progress
                updateProgress();

                // Check if all letters are revealed
                if (revealedCount === totalLetters) {
                    showMessage('Congratulations! You uncovered the entire poem!');
                }
            }
        }

        // Update progress bar
        function updateProgress() {
            const percentage = (revealedCount / totalLetters) * 100;
            progressBar.style.width = `${percentage}%`;
        }

        // Save pixel state to localStorage
        function saveState(position, isRevealed) {
            let state = loadState() || {};
            state[position] = isRevealed;

            try {
                localStorage.setItem(storageKey, JSON.stringify(state));
            } catch (e) {
                showMessage('Error saving state: Storage might be full');
                console.error('Error saving state:', e);
            }
        }

        // Load pixel state from localStorage
        function loadState() {
            try {
                const state = localStorage.getItem(storageKey);
                return state ? JSON.parse(state) : null;
            } catch (e) {
                console.error('Error loading state:', e);
                return null;
            }
        }

        // Reset all pixels to hidden state
        function resetMosaic() {
            // Reset UI
            const revealedPixels = document.querySelectorAll('.pixel.revealed');
            revealedPixels.forEach(pixel => {
                pixel.classList.remove('revealed');
            });

            // Reset counter
            revealedCount = 0;

            // Update progress
            updateProgress();

            // Clear localStorage
            try {
                localStorage.removeItem(storageKey);

                // Set new reset time
                setResetTime();

                showMessage('Mosaic has been reset');
            } catch (e) {
                console.error('Error clearing state:', e);
            }
        }

        // Center the mosaic in the container
        function centerMosaic() {
            const containerWidth = mosaicContainer.offsetWidth;
            const containerHeight = mosaicContainer.offsetHeight;
            const mosaicWidth = gridSize * 20;
            const mosaicHeight = gridSize * 20;

            offsetX = (containerWidth - mosaicWidth) / 2;
            offsetY = (containerHeight - mosaicHeight) / 2;

            updateMosaicPosition();
        }

        // Update mosaic position
        function updateMosaicPosition() {
            mosaic.style.transform = `translate(${offsetX}px, ${offsetY}px) scale(${scale})`;
        }

        // Handle zoom in
        function zoomIn() {
            if (scale < 3) {
                scale += 0.2;
                updateMosaicPosition();
            }
        }

        // Handle zoom out
        function zoomOut() {
            if (scale > 0.4) {
                scale -= 0.2;
                updateMosaicPosition();
            }
        }

        // Reset zoom
        function resetZoom() {
            scale = 1;
            centerMosaic();
        }

        // Set reset time
        function setResetTime() {
            const now = new Date();
            localStorage.setItem(resetTimeKey, now.getTime());
        }

        // Check if mosaic should be reset based on schedule
        function checkResetSchedule() {
            const resetTimeStr = localStorage.getItem(resetTimeKey);

            if (resetTimeStr) {
                const resetTime = parseInt(resetTimeStr);
                const now = new Date().getTime();
                const diff = now - resetTime;
                const daysDiff = diff / (1000 * 60 * 60 * 24);

                if (daysDiff >= RESET_INTERVAL_DAYS) {
                    resetMosaic();
                    showMessage(`Mosaic was automatically reset after ${RESET_INTERVAL_DAYS} days`);
                }
            } else {
                // First time user, set reset time
                setResetTime();
            }
        }

        // Show message
        function showMessage(text) {
            messageEl.textContent = text;
            messageEl.classList.add('show');

            setTimeout(() => {
                messageEl.classList.remove('show');
            }, 3000);
        }

        // Drag functionality
        function startDrag(e) {
            if (e.button === 0) { // Left mouse button only
                isDragging = true;
                startPosX = e.clientX - offsetX;
                startPosY = e.clientY - offsetY;
                mosaicContainer.style.cursor = 'grabbing';
            }
        }

        function drag(e) {
            if (isDragging) {
                offsetX = e.clientX - startPosX;
                offsetY = e.clientY - startPosY;
                updateMosaicPosition();
            }
        }

        function endDrag() {
            isDragging = false;
            mosaicContainer.style.cursor = 'grab';
        }

        // Mouse wheel zoom
        function handleWheel(e) {
            e.preventDefault();

            // Determine zoom direction
            if (e.deltaY < 0) {
                // Zoom in
                if (scale < 3) {
                    scale += 0.1;
                }
            } else {
                // Zoom out
                if (scale > 0.4) {
                    scale -= 0.1;
                }
            }

            updateMosaicPosition();
        }

        // Touch events for mobile
        function handleTouchStart(e) {
            if (e.touches.length === 1) {
                isDragging = true;
                const touch = e.touches[0];
                startPosX = touch.clientX - offsetX;
                startPosY = touch.clientY - offsetY;
            }
        }

        function handleTouchMove(e) {
            if (isDragging && e.touches.length === 1) {
                const touch = e.touches[0];
                offsetX = touch.clientX - startPosX;
                offsetY = touch.clientY - startPosY;
                updateMosaicPosition();
                e.preventDefault();
            }
        }

        function handleTouchEnd() {
            isDragging = false;
        }

        // Event listeners
        resetBtn.addEventListener('click', resetMosaic);
        zoomInBtn.addEventListener('click', zoomIn);
        zoomOutBtn.addEventListener('click', zoomOut);
        zoomResetBtn.addEventListener('click', resetZoom);

        mosaicContainer.addEventListener('mousedown', startDrag);
        mosaicContainer.addEventListener('mousemove', drag);
        mosaicContainer.addEventListener('mouseup', endDrag);
        mosaicContainer.addEventListener('mouseleave', endDrag);
        mosaicContainer.addEventListener('wheel', handleWheel);

        // Mobile support
        mosaicContainer.addEventListener('touchstart', handleTouchStart);
        mosaicContainer.addEventListener('touchmove', handleTouchMove);
        mosaicContainer.addEventListener('touchend', handleTouchEnd);

        // Initialize the mosaic on page load
        window.addEventListener('load', initMosaic);

        // Handle window resize
        window.addEventListener('resize', centerMosaic);
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True, port=5000)