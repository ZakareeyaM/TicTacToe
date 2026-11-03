import os
import tkinter as tk
from tkinter import messagebox
import random

from dotenv import load_dotenv

# =========================
# API CONFIGURATION (loaded from .env)
# =========================
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_API_URL = os.getenv(
    "GEMINI_API_URL",
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
)

# =========================
# GAME STATE
# =========================
player_symbol = "X"
ai_symbol = "O"
player_score = 0
ai_score = 0
draws = 0

board = [["" for _ in range(3)] for _ in range(3)]
buttons = [[None for _ in range(3)] for _ in range(3)]

# Track AI's opening strategy to ensure variety
last_opening_moves = []

# =========================
# GUI SETUP
# =========================
root = tk.Tk()
root.title("AI Tic Tac Toe (Varied Difficulty)")

scoreboard = tk.Label(root, font=("Arial", 14))
scoreboard.pack(pady=5)

strategy_label = tk.Label(root, font=("Arial", 10), fg="blue")
strategy_label.pack(pady=2)

board_frame = tk.Frame(root)
board_frame.pack()

abort_button = tk.Button(root, text="Abort Game", fg="red", font=("Arial", 12))

# =========================
# GAME LOGIC
# =========================
def update_score():
    scoreboard.config(
        text=f"You: {player_score}   AI: {ai_score}   Draws: {draws}"
    )

def reset_board():
    global board
    board = [["" for _ in range(3)] for _ in range(3)]
    for r in range(3):
        for c in range(3):
            buttons[r][c].config(text=" ", state=tk.NORMAL)
    strategy_label.config(text="")
    if ai_symbol == "X":
        root.after(200, ai_move)

def check_winner():
    lines = (
        board +
        list(zip(*board)) +
        [
            [board[0][0], board[1][1], board[2][2]],
            [board[0][2], board[1][1], board[2][0]]
        ]
    )
    for line in lines:
        if line[0] and line.count(line[0]) == 3:
            return line[0]
    if all(board[r][c] for r in range(3) for c in range(3)):
        return "Draw"
    return None

def end_game(winner):
    global player_score, ai_score, draws
    if winner == "Draw":
        draws += 1
        msg = "It's a draw!"
    elif winner == player_symbol:
        player_score += 1
        msg = "You win! 🎉"
    else:
        ai_score += 1
        msg = "AI wins!"
    update_score()
    if messagebox.askyesno("Game Over", msg + " Play again?"):
        reset_board()
    else:
        root.destroy()

def on_click(r, c):
    if board[r][c]:
        return
    board[r][c] = player_symbol
    buttons[r][c].config(text=player_symbol, state=tk.DISABLED)
    winner = check_winner()
    if winner:
        end_game(winner)
        return
    root.after(150, ai_move)

# =========================
# AI LOGIC - INTENTIONALLY VARIED
# =========================
def ai_move():
    move = get_ai_move()
    if not move:
        return
    r, c = move
    board[r][c] = ai_symbol
    buttons[r][c].config(text=ai_symbol, state=tk.DISABLED)
    winner = check_winner()
    if winner:
        end_game(winner)

def get_ai_move():
    """AI with VARIED opening strategies to make game winnable and interesting."""
    
    moves_made = sum(1 for r in range(3) for c in range(3) if board[r][c] != "")
    
    # FIRST MOVE: Use varied, interesting strategies
    if moves_made == 1:
        return get_varied_opening_move()
    
    # SECOND MOVE: Still be creative, not always optimal
    if moves_made == 2:
        return get_varied_second_move()
    
    # REST OF GAME: Play smart but not perfect (80% optimal, 20% random good moves)
    if random.random() < 0.2:
        # 20% of the time, make a "good but not perfect" move
        return get_good_but_imperfect_move()
    
    # 80% of the time, try to play optimally
    return minimax_move(board, ai_symbol)

def get_varied_opening_move():
    """AI's first move - cycle through different strategies to avoid monotony."""
    global last_opening_moves
    
    # Find where player placed X
    player_pos = None
    for r in range(3):
        for c in range(3):
            if board[r][c] == player_symbol:
                player_pos = (r, c)
                break
    
    available_moves = [(r, c) for r in range(3) for c in range(3) if board[r][c] == ""]
    
    # Define different opening strategies
    strategies = []
    
    if player_pos == (1, 1):  # Player took center
        strategies = [
            ("Corner Attack", [(0, 0), (0, 2), (2, 0), (2, 2)]),
        ]
    elif player_pos in [(0, 0), (0, 2), (2, 0), (2, 2)]:  # Player took corner
        # Varied strategies when player takes corner
        corners = [(0, 0), (0, 2), (2, 0), (2, 2)]
        edges = [(0, 1), (1, 0), (1, 2), (2, 1)]
        opposite_corner = {(0, 0): (2, 2), (0, 2): (2, 0), (2, 0): (0, 2), (2, 2): (0, 0)}
        
        strategies = [
            ("Edge Play", [e for e in edges if board[e[0]][e[1]] == ""]),
            ("Corner Response", [c for c in corners if board[c[0]][c[1]] == "" and c != player_pos]),
            ("Opposite Corner", [opposite_corner[player_pos]] if board[opposite_corner[player_pos][0]][opposite_corner[player_pos][1]] == "" else available_moves),
        ]
        # Only add center strategy 30% of the time
        if random.random() < 0.3 and board[1][1] == "":
            strategies.append(("Center Control", [(1, 1)]))
    else:  # Player took edge
        corners = [(0, 0), (0, 2), (2, 0), (2, 2)]
        edges = [(0, 1), (1, 0), (1, 2), (2, 1)]
        
        strategies = [
            ("Corner First", [c for c in corners if board[c[0]][c[1]] == ""]),
            ("Edge Response", [e for e in edges if board[e[0]][e[1]] == ""]),
        ]
        # Only add center 40% of the time
        if random.random() < 0.4 and board[1][1] == "":
            strategies.append(("Center Control", [(1, 1)]))
    
    # Avoid repeating the same strategy too many times
    if len(last_opening_moves) >= 3:
        last_three = last_opening_moves[-3:]
        # Filter out strategies we've used too much recently
        strategies = [s for s in strategies if s[0] not in last_three]
    
    # Pick a random strategy
    if strategies:
        strategy_name, moves = random.choice(strategies)
        if moves:
            move = random.choice(moves)
            last_opening_moves.append(strategy_name)
            if len(last_opening_moves) > 5:
                last_opening_moves.pop(0)
            strategy_label.config(text=f"AI Strategy: {strategy_name}")
            print(f"AI Opening Strategy: {strategy_name} -> {move}")
            return move
    
    # Fallback
    return random.choice(available_moves)

def get_varied_second_move():
    """Second move - still be creative."""
    # Check for immediate threats first
    immediate = check_immediate_threat()
    if immediate:
        return immediate
    
    # Otherwise, make an interesting but not always perfect move
    available = [(r, c) for r in range(3) for c in range(3) if board[r][c] == ""]
    
    # 50% chance to play optimally, 50% chance to play creatively
    if random.random() < 0.5:
        return minimax_move(board, ai_symbol)
    else:
        return random.choice(available)

def get_good_but_imperfect_move():
    """Make a 'good' move but not necessarily the perfect one."""
    # Check for immediate threats
    immediate = check_immediate_threat()
    if immediate:
        return immediate
    
    # Otherwise pick a random good position
    available = [(r, c) for r in range(3) for c in range(3) if board[r][c] == ""]
    
    # Prefer corners and center
    good_positions = [(1, 1), (0, 0), (0, 2), (2, 0), (2, 2)]
    good_available = [pos for pos in good_positions if pos in available]
    
    if good_available:
        return random.choice(good_available)
    return random.choice(available)

def check_immediate_threat():
    """Check if we can win immediately or must block immediately."""
    # Check if AI can win
    for r in range(3):
        for c in range(3):
            if board[r][c] == "":
                board[r][c] = ai_symbol
                if check_winner_board(board) == ai_symbol:
                    board[r][c] = ""
                    return (r, c)
                board[r][c] = ""
    
    # Check if must block player
    for r in range(3):
        for c in range(3):
            if board[r][c] == "":
                board[r][c] = player_symbol
                if check_winner_board(board) == player_symbol:
                    board[r][c] = ""
                    return (r, c)
                board[r][c] = ""
    
    return None

def minimax_move(bd, symbol):
    """Standard minimax for when AI plays optimally."""
    best_val = -1000
    best_moves = []
    
    for r in range(3):
        for c in range(3):
            if bd[r][c] == "":
                bd[r][c] = symbol
                val = minimax_value(bd, 0, False)
                bd[r][c] = ""
                
                if val > best_val:
                    best_val = val
                    best_moves = [(r, c)]
                elif val == best_val:
                    best_moves.append((r, c))
    
    return random.choice(best_moves) if best_moves else None

def minimax_value(bd_inner, depth, is_max):
    winner = check_winner_board(bd_inner)
    if winner == ai_symbol: return 10 - depth
    if winner == player_symbol: return depth - 10
    if winner == "Draw": return 0
    
    if is_max:
        best = -1000
        for r in range(3):
            for c in range(3):
                if bd_inner[r][c] == "":
                    bd_inner[r][c] = ai_symbol
                    best = max(best, minimax_value(bd_inner, depth+1, False))
                    bd_inner[r][c] = ""
        return best
    else:
        best = 1000
        for r in range(3):
            for c in range(3):
                if bd_inner[r][c] == "":
                    bd_inner[r][c] = player_symbol
                    best = min(best, minimax_value(bd_inner, depth+1, True))
                    bd_inner[r][c] = ""
        return best

def check_winner_board(bd_inner):
    lines = (
        bd_inner +
        list(zip(*bd_inner)) +
        [
            [bd_inner[0][0], bd_inner[1][1], bd_inner[2][2]],
            [bd_inner[0][2], bd_inner[1][1], bd_inner[2][0]]
        ]
    )
    for line in lines:
        if line[0] and line.count(line[0]) == 3:
            return line[0]
    if all(bd_inner[r][c] for r in range(3) for c in range(3)):
        return "Draw"
    return None

# =========================
# ABORT HANDLER
# =========================
def abort_game():
    if messagebox.askyesno("Abort Game", "Are you sure you want to quit?"):
        root.destroy()

abort_button.config(command=abort_game)
abort_button.pack(pady=5)

# =========================
# BUILD BOARD
# =========================
for r in range(3):
    for c in range(3):
        btn = tk.Button(
            board_frame,
            text=" ",
            font=("Arial", 36),
            width=4,
            height=2,
            command=lambda r=r, c=c: on_click(r, c)
        )
        btn.grid(row=r, column=c)
        buttons[r][c] = btn

update_score()
root.mainloop()
