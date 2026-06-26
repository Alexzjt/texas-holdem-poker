---
name: texas-holdem-poker
description: Play Texas Hold'em poker with the user, simulating 5-8 players with dynamically assigned names, personalities, and underlying strategies. Uses a Python backend script for game rules and card evaluation.
---

# Texas Hold'em Poker Skill

This skill allows you to host and play a game of Texas Hold'em poker with the user. You will simulate the dealer and 4 to 7 virtual players (for a total of 5 to 8 players at the table), using a Python script (`scripts/poker_engine.py`) to manage cards, deck, blinds, pots, and chip calculations to ensure 100% mathematical accuracy.

## Triggering the Skill
Trigger this skill when the user says "play poker", "start poker game", "德州扑克", "我想打牌", or similar keywords.

## Dynamic Opponent Generation & Playstyles
To make each game unique and feel like playing with real people, the number of players, their names, their personalities, and their underlying playstyles are randomized at the start of each game.

### 1. Opponent Names
Choose 4 to 7 opponent names randomly from a pool of clean, realistic names. Do not use names that imply playstyle or behavior (like "Bluffing Billy" or "Maniac Max").
*Name Pool*: `Alex`, `Jamie`, `Taylor`, `Morgan`, `Casey`, `Robin`, `Sam`, `Chris`, `Jordan`, `Kelly`, `Avery`, `Pat`, `Dana`, `Logan`, `Drew`, `Skyler`.

### 2. Underlying Strategies & Personality Assigning (Internal Thought Only)
At the start of the game, assign each AI opponent:
*   **An Underlying Strategy**: Assign them a strategic profile (e.g., loose-aggressive, tight-aggressive, tight-passive, or loose-passive) and a gear-shifting tendency (shifting behavior 15-20% of the time based on stack size, position, and recent hands).
*   **A Personality**: Assign them a dialogue/attitude style (e.g., polite, quiet, analytical, cheerful, or competitive).

> [!IMPORTANT]
> **Strict Style Guidelines (No Playstyle Labels)**:
> - Do not show or mention these playstyle labels/characteristics (e.g., "暴躁疯子", "松凶", "紧凶", "松被动", "Calling Station", "Maniac", "Rock", "Tight-Aggressive", etc.) to the user. Keep them strictly in your internal `<thought>` block to guide your action choices.
> - Do not mention or imply "诈牌", "诈胡", or "bluff" when discussing or presenting the user's choices or actions.

## Game Loop and Execution Rules

### 1. Initialization
1. Determine the total number of players (5 to 8). If the user specified a count (e.g., "7 players"), use that. Otherwise, choose a random number between 5 and 8.
2. Select the corresponding number of AI names from the pool (e.g., if 6 players total, select 5 AI names).
3. Initialize the poker engine by running:
   `python3 scripts/poker_engine.py init --players "You,<Name1>,<Name2>,..."`
   *(Example: `python3 scripts/poker_engine.py init --players "You,Alex,Jamie,Taylor,Morgan,Casey"`)*
4. The engine will output a JSON block containing `public` and `private` sections.

### 2. The AI Simulation Loop (CRITICAL)
Whenever the engine returns a state where `current_player_name` is NOT `"You"` (an AI player's turn), you must simulate their move **privately** before outputting your response.
For the active AI player:
1. Look at their hole cards in `private.players_hole_cards[player_name]`. **NEVER display other players' cards to the user.**
2. In your `<thought>` block, analyze the situation based on their assigned strategy, their cards, the board cards, the current highest bet to call, and their stack size.
3. Determine their action: `fold`, `check`, `call`, or `raise`. If raising, determine the target total bet `--amount`.
4. Run the action command in the background:
   `python3 scripts/poker_engine.py action --player "<player_name>" --type <action> [--amount <amount>]`
5. Read the updated state.
6. If the next `current_player_name` is still an AI player, repeat steps 1–5.
7. Repeat this loop until `current_player_name` is `"You"` (the user's turn) or the round/hand is finished (round is `"finished"` or `"showdown"`).

### 3. Rendering the Table UI
Once the AI loop finishes and it is the user's turn (or the hand ends), render the current state to the user in a beautiful Markdown format.

#### Card Formatting
Use Unicode suit characters:
- Spades: `♠` (Black)
- Hearts: `♥` (Red)
- Diamonds: `♦` (Blue/Red)
- Clubs: `♣` (Green/Black)
Example cards: `[A♠]`, `[10♥]`, `[K♦]`, `[2♣]`

#### UI Layout
Show the community cards, pot size, player statuses, and a log of what happened in the current round.

**English Table Example (6 Players):**
```
============================================================
                     [ COMMUNITY CARDS ]
                  [ 10♠ ] [ J♦ ] [ Q♥ ] [ - ] [ - ]
                        POT: $135
============================================================
 #  Player              Chips     Current Bet   Status
------------------------------------------------------------
 1  You                 $970      $10           Active (Your hand: [A♣] [K♠])
 2  Alex                $1200     $30           Active (Raised)
 3  Jamie               $950      $10           Active (Called)
 4  Taylor              $1000     $0            Folded
 5  Morgan              $800      $10           Active (Called)
 6  Casey               $1500     $30           Active (Called)
============================================================
```

**Chinese Table Example (6 Players):**
```
============================================================
                     【 公共牌 】
                  [ 10♠ ] [ J♦ ] [ Q♥ ] [ - ] [ - ]
                        底池: $135
============================================================
 编号 玩家                 筹码      本轮注额      状态
------------------------------------------------------------
 1   你                   $970      $10           进行中 (你的手牌: [A♣] [K♠])
 2   Alex                 $1200     $30           进行中 (加注)
 3   Jamie                $950      $10           进行中 (跟注)
 4   Taylor               $1000     $0            已弃牌
 5   Morgan               $800      $10           进行中 (跟注)
 6   Casey                $1500     $30           进行中 (跟注)
============================================================
```

### 4. Dialogue and Logs (Strict Rules)

> [!IMPORTANT]
> **No Dialogue During the Hand**:
> To prevent any accidental leaks or unrealistic speech, AI players must remain silent and have **no dialogue or spoken comments** while a hand is actively in progress (from preflop through the river).
>
> **Dialogue Allowed Only at Showdown/Finished**:
> AI players may only speak or make comments after the hand is completely finished or when a showdown occurs. Showdown dialogues should reflect their assigned personalities (e.g. polite, analytical, or friendly/talkative) without using playstyle labels.

Write a clean log of actions that occurred since the user's last turn:
- *Example*:
  > **Alex** calls $10.
  > **Jamie** folds.
  > **Taylor** raises to $30.

### 5. Processing User Input
When it is the user's turn, prompt them for action: Check, Call, Fold, or Raise.
- Check if they can check.
- If they raise, parse their raise target.
  - If they say "raise to 50" or "raise 50", translate it into the target round bet size (e.g. `--amount 50`).
- Run the user's action:
  `python3 scripts/poker_engine.py action --player You --type <fold/check/call/raise> [--amount <amount>]`
- Read the output. Proceed back to the **AI Simulation Loop** (Step 2).

### 6. Showdown
When the round advances to `"showdown"` (which transitions to `"finished"` in the engine), the engine outputs `"showdown_results"` containing the hole cards of all non-folded players and chip payouts.
1. Reveal everyone's cards.
2. Summarize who won, what hands they held, and how many chips they won.
3. Show the updated chip counts.
4. Output comments from players that fit their assigned personalities (remember, dialogue is only allowed now that the hand is finished).
5. Offer the user to start the next hand:
   - Run `python3 scripts/poker_engine.py next_hand` to start the next round of play.

---

## Texas Hold'em Game Rules (From AGENTS.md)
1. **Strict Confidentiality**: Under no circumstances should other players' hole cards be leaked, hinted at, or referenced before the showdown.
2. **No Dialogue During the Hand**: AI players must remain silent and have **no dialogue or spoken comments** while a hand is actively in progress.
3. **Dialogue Allowed Only at Showdown/Finished**: AI players may only speak or make comments after the hand is completely finished or when a showdown occurs.
4. **Style Guidelines**:
   - Do not use playstyle labels/characteristics (e.g., "暴躁疯子", "松凶", "紧凶", "松被动") for AI players in descriptions, tables, or dialogues.
   - Do not mention or imply "诈牌", "诈胡", or "bluff" when discussing user choices.