from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# Initialize game board
board = [''] * 9
current_player = 'X'
game_over = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/reset', methods=['POST'])
def reset():
    global board, current_player, game_over
    board = [''] * 9
    current_player = 'X'
    game_over = False
    return jsonify({'status': 'success'})

@app.route('/move', methods=['POST'])
def make_move():
    global board, current_player, game_over
    
    if game_over:
        return jsonify({'status': 'error', 'message': 'Game is over'})
    
    data = request.get_json()
    position = data.get('position')
    
    if not position or position < 0 or position > 8:
        return jsonify({'status': 'error', 'message': 'Invalid position'})
    
    if board[position] != '':
        return jsonify({'status': 'error', 'message': 'Position already taken'})
    
    board[position] = current_player
    
    # Check for win
    if check_winner(current_player):
        game_over = True
        return jsonify({
            'status': 'success',
            'winner': current_player,
            'board': board
        })
    
    # Check for draw
    if '' not in board:
        game_over = True
        return jsonify({
            'status': 'success',
            'winner': 'draw',
            'board': board
        })
    
    # Switch player
    current_player = 'O' if current_player == 'X' else 'X'
    
    return jsonify({
        'status': 'success',
        'current_player': current_player,
        'board': board
    })

def check_winner(player):
    # Check rows
    for i in range(0, 9, 3):
        if board[i] == board[i+1] == board[i+2] == player:
            return True
    
    # Check columns
    for i in range(3):
        if board[i] == board[i+3] == board[i+6] == player:
            return True
    
    # Check diagonals
    if board[0] == board[4] == board[8] == player:
        return True
    if board[2] == board[4] == board[6] == player:
        return True
    
    return False

if __name__ == '__main__':
    app.run(debug=True) 