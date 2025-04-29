document.addEventListener('DOMContentLoaded', () => {
    const cells = document.querySelectorAll('.cell');
    const currentPlayerDisplay = document.getElementById('current-player');
    const resetButton = document.getElementById('reset-button');
    const messageDisplay = document.getElementById('message');

    // Add click event listeners to cells
    cells.forEach(cell => {
        cell.addEventListener('click', handleCellClick);
    });

    // Add click event listener to reset button
    resetButton.addEventListener('click', resetGame);

    async function handleCellClick(e) {
        const position = parseInt(e.target.dataset.position);
        
        try {
            const response = await fetch('/move', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ position }),
            });

            const data = await response.json();

            if (data.status === 'success') {
                updateBoard(data.board);
                currentPlayerDisplay.textContent = data.current_player;

                if (data.winner) {
                    if (data.winner === 'draw') {
                        messageDisplay.textContent = "It's a draw!";
                    } else {
                        messageDisplay.textContent = `Player ${data.winner} wins!`;
                    }
                    cells.forEach(cell => cell.removeEventListener('click', handleCellClick));
                }
            } else {
                messageDisplay.textContent = data.message;
            }
        } catch (error) {
            console.error('Error:', error);
            messageDisplay.textContent = 'An error occurred. Please try again.';
        }
    }

    function updateBoard(board) {
        cells.forEach((cell, index) => {
            cell.textContent = board[index];
        });
    }

    async function resetGame() {
        try {
            const response = await fetch('/reset', {
                method: 'POST',
            });

            const data = await response.json();

            if (data.status === 'success') {
                cells.forEach(cell => {
                    cell.textContent = '';
                    cell.addEventListener('click', handleCellClick);
                });
                currentPlayerDisplay.textContent = 'X';
                messageDisplay.textContent = '';
            }
        } catch (error) {
            console.error('Error:', error);
            messageDisplay.textContent = 'An error occurred while resetting the game.';
        }
    }
}); 