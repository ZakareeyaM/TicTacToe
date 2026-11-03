# AI Tic Tac Toe (Varied Difficulty)

Tkinter Tic Tac Toe against an AI that mixes varied openings, immediate win/block checks and minimax.

## Setup

1. Install Python 3.9+ (Tkinter is included on Windows/macOS; on Linux: `sudo apt install python3-tk`).
2. Create a virtual environment (optional) and install dependencies:

   ```
   python -m venv venv
   venv\Scripts\activate        # Windows
   source venv/bin/activate     # macOS / Linux
   pip install -r requirements.txt
   ```

3. Open `.env` and set your Gemini key:

   ```
   GEMINI_API_KEY=your_real_key_here
   ```

   Get a key at https://aistudio.google.com/apikey

4. Run:

   ```
   python main.py
   ```

## Notes

- `.env` is git-ignored. Never commit or share your real key.
- `.env.example` is the safe template to commit.
- The game logic is unchanged from the original script. The key is loaded into `GEMINI_API_KEY` / `GEMINI_API_URL` in `main.py`, but, as in the original, no API calls are made yet.

## Structure

```
tictactoe-ai/
├── main.py
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```
