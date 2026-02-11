🃏 Tiến Lên Miền Nam – Online Card Game

An interactive web-based implementation of Tiến Lên Miền Nam (Vietnamese Southern Poker), built with Python and Flask. The game simulates a traditional 4-player card game experience with rule-based gameplay logic and a clean web interface.

🔗 Live Demo: https://tien-len-4ajh.onrender.com/

📌 About the Game

Tiến Lên Miền Nam is a popular Vietnamese shedding-type card game played with a standard 52-card deck. The objective is to be the first player to get rid of all your cards by playing valid combinations that beat the previous player’s hand.

This project recreates the authentic gameplay mechanics and enforces proper rule validation programmatically.

📖 Game Rules (Tiến Lên Miền Nam)
🎯 Objective

Be the first player to discard all your cards.

👥 Players

4 players

Each player is dealt 13 cards

Uses a standard 52-card deck

🃏 Card Ranking
Rank Order (Lowest → Highest)
3 < 4 < 5 < 6 < 7 < 8 < 9 < 10 < J < Q < K < A < 2
2 is the highest rank

3 is the lowest rank

Suit Order (Lowest → Highest
♠ Spades < ♣ Clubs < ♦ Diamonds < ♥ Hearts

Suits only matter when comparing cards of the same rank.

🔹 Valid Combinations
1️⃣ Single Card

Any individual card.

2️⃣ Pair

Two cards of the same rank.

3️⃣ Three of a Kind

Three cards of the same rank.

4️⃣ Straight

Three or more consecutive cards.

Cannot include the card 2.

Example: 5-6-7-8

5️⃣ Double Sequence (Đôi Thông)

Three or more consecutive pairs.

Example: (5-5, 6-6, 7-7)

🔥 Special Rules (Beating a 2)

A single 2 can be beaten by:

A higher 2 (by suit)

A double sequence

A pair of 2s can be beaten by:

A higher pair of 2s

A double sequence of 4 pairs or more (depending on house rules)

(Some rule variations exist; this implementation follows the common Southern version.)

▶️ Gameplay Flow

The player holding 3♠ (Three of Spades) starts the first round.

Players take turns clockwise.

A player must:

Play a higher valid combination of the same type
OR

Pass

If all other players pass:

The last player who played a valid hand starts a new round.

The game continues until one player has no cards left.

🏆 Winning

The first player to discard all cards wins the game.

🚀 Features

♠️ Full 52-card deck implementation

🎮 4-player game simulation

🧠 Rule-based validation engine

🔄 Turn management system

🌐 Web-based interface using Flask

🔐 Session-based game state

🎴 Automatic shuffle & deal

🏆 Win detection

🛠 Tech Stack:
Backend

Python

Flask

Flask-CORS

Frontend

HTML

CSS

JavaScript

Deployment

Render

Waitress (Production WSGI server)

