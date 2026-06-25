#!/usr/bin/env python3
import json
import os
import random
import sys
from collections import Counter
from itertools import combinations

# Card representation: Rank (2-A), Suit (s, h, d, c)
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
SUITS = 'shdc'
RANK_VALUES = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
    'J': 11, 'Q': 12, 'K': 13, 'A': 14
}

class Card:
    def __init__(self, card_str):
        self.suit = card_str[-1]
        self.rank_str = card_str[:-1]
        self.value = RANK_VALUES[self.rank_str]

    def __repr__(self):
        return f"{self.rank_str}{self.suit}"

    def to_dict(self):
        return f"{self.rank_str}{self.suit}"

# 7-card Hand Evaluator
def evaluate_5_card_hand(cards):
    """
    Evaluates a 5-card hand and returns a tuple (hand_rank, tie_breakers)
    Ranks:
    8: Straight Flush
    7: Four of a Kind
    6: Full House
    5: Flush
    4: Straight
    3: Three of a Kind
    2: Two Pair
    1: One Pair
    0: High Card
    """
    values = sorted([c.value for c in cards], reverse=True)
    suits = [c.suit for c in cards]
    
    is_flush = len(set(suits)) == 1
    
    # Check straight
    is_straight = False
    straight_high = None
    unique_values = sorted(list(set(values)), reverse=True)
    if len(unique_values) == 5:
        if unique_values[0] - unique_values[4] == 4:
            is_straight = True
            straight_high = unique_values[0]
        elif unique_values == [14, 5, 4, 3, 2]: # Ace-low straight
            is_straight = True
            straight_high = 5

    counts = Counter(values)
    mc = counts.most_common()
    
    # Straight Flush
    if is_flush and is_straight:
        return (8, [straight_high])
        
    # Four of a Kind
    if mc[0][1] == 4:
        quad_rank = mc[0][0]
        kicker = mc[1][0]
        return (7, [quad_rank, kicker])
        
    # Full House
    if mc[0][1] == 3 and mc[1][1] >= 2:
        trip_rank = mc[0][0]
        pair_rank = mc[1][0]
        return (6, [trip_rank, pair_rank])
        
    # Flush
    if is_flush:
        return (5, values)
        
    # Straight
    if is_straight:
        return (4, [straight_high])
        
    # Three of a Kind
    if mc[0][1] == 3:
        trip_rank = mc[0][0]
        kickers = [item[0] for item in mc[1:]]
        return (3, [trip_rank] + sorted(kickers, reverse=True))
        
    # Two Pair
    if mc[0][1] == 2 and mc[1][1] == 2:
        pairs = sorted([mc[0][0], mc[1][0]], reverse=True)
        kicker = mc[2][0]
        return (2, pairs + [kicker])
        
    # One Pair
    if mc[0][1] == 2:
        pair_rank = mc[0][0]
        kickers = sorted([item[0] for item in mc[1:]], reverse=True)
        return (1, [pair_rank] + kickers)
        
    # High Card
    return (0, values)

def evaluate_7_card_hand(hole_cards, community_cards):
    all_cards = [Card(c) for c in (hole_cards + community_cards)]
    best_score = (-1, [])
    # Find the max score among all 5-card combinations of the 7 cards
    for comb in combinations(all_cards, 5):
        score = evaluate_5_card_hand(comb)
        if score > best_score:
            best_score = score
    return best_score

# Helper to check if string rank is straight
def get_hand_rank_name(rank_code):
    names = {
        8: "Straight Flush",
        7: "Four of a Kind",
        6: "Full House",
        5: "Flush",
        4: "Straight",
        3: "Three of a Kind",
        2: "Two Pair",
        1: "One Pair",
        0: "High Card"
    }
    return names.get(rank_code, "Unknown")

class PokerEngine:
    STATE_FILE = "game_state.json"

    def __init__(self):
        self.state = {}

    def load_state(self):
        if os.path.exists(self.STATE_FILE):
            with open(self.STATE_FILE, "r") as f:
                self.state = json.load(f)
        else:
            self.state = {}

    def save_state(self):
        with open(self.STATE_FILE, "w") as f:
            json.dump(self.state, f, indent=2)

    def print_state_json(self):
        # Prepare public and private states
        round_name = self.state.get("round", "finished")
        players = self.state.get("players", [])
        community = self.state.get("community_cards", [])
        
        # Format players for public display
        public_players = []
        for p in players:
            p_info = {
                "name": p["name"],
                "chips": p["chips"],
                "current_bet": p["current_bet"],
                "folded": p["folded"],
                "all_in": p["all_in"],
                "eliminated": p.get("eliminated", False),
                "last_action": p.get("last_action", "")
            }
            # Reveal hole cards if player is 'You' or if it is Showdown
            if p["name"] == "You" or round_name in ("showdown", "finished"):
                p_info["hole_cards"] = p["hole_cards"]
            public_players.append(p_info)

        public_state = {
            "hand_count": self.state.get("hand_count", 0),
            "round": round_name,
            "community_cards": community,
            "pot": self.state.get("pot", 0),
            "current_round_highest_bet": self.state.get("current_round_highest_bet", 0),
            "dealer_button": self.state.get("dealer_button", 0),
            "current_player_name": self.get_current_player_name(),
            "last_action_desc": self.state.get("last_action_desc", ""),
            "players": public_players
        }

        # Showdown additions
        if round_name in ("showdown", "finished") and "showdown_results" in self.state:
            public_state["showdown_results"] = self.state["showdown_results"]

        # Calculate current hand rank for all players (only if they are active)
        players_current_hands = {}
        for p in players:
            if not p.get("eliminated", False) and not p.get("folded", False):
                all_cards = p["hole_cards"] + community
                if len(all_cards) >= 5:
                    score = evaluate_7_card_hand(p["hole_cards"], community)
                    rank_name = get_hand_rank_name(score[0])
                else:
                    vals = sorted([Card(c).value for c in p["hole_cards"]], reverse=True)
                    if len(p["hole_cards"]) == 2 and p["hole_cards"][0][:-1] == p["hole_cards"][1][:-1]:
                        score = (1, [vals[0]])
                    else:
                        score = (0, vals)
                    rank_name = get_hand_rank_name(score[0])
                players_current_hands[p["name"]] = {
                    "hand_rank_name": rank_name,
                    "score": score
                }
            else:
                players_current_hands[p["name"]] = {
                    "hand_rank_name": "Folded" if p.get("folded", False) else "Eliminated",
                    "score": None
                }

        private_state = {
            "deck": self.state.get("deck", []),
            "players_hole_cards": {p["name"]: p["hole_cards"] for p in players},
            "players_current_hands": players_current_hands
        }

        output = {
            "public": public_state,
            "private": private_state
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))

    def get_current_player_name(self):
        curr_idx = self.state.get("current_player")
        if curr_idx is None or curr_idx == -1:
            return None
        players = self.state.get("players", [])
        if 0 <= curr_idx < len(players):
            return players[curr_idx]["name"]
        return None

    def init_game(self, player_names, start_chips=1000):
        players = []
        for name in player_names:
            players.append({
                "name": name,
                "chips": start_chips,
                "hole_cards": [],
                "folded": False,
                "all_in": False,
                "eliminated": False,
                "current_bet": 0,
                "total_bet_in_hand": 0,
                "last_action": "",
                "has_acted": False
            })
        
        self.state = {
            "hand_count": 0,
            "dealer_button": random.randint(0, len(players) - 1),
            "players": players,
            "deck": [],
            "community_cards": [],
            "pot": 0,
            "current_round_highest_bet": 0,
            "current_player": -1,
            "round": "finished", # Will transition to preflop on next_hand
            "last_action_desc": "Game initialized."
        }
        self.start_next_hand()

    def start_next_hand(self):
        players = self.state["players"]
        self.state.pop("showdown_results", None)
        
        # Check if players are eliminated
        active_count = 0
        for p in players:
            if p["chips"] <= 0:
                p["eliminated"] = True
                p["folded"] = True
                p["all_in"] = False
            else:
                p["eliminated"] = False
                p["folded"] = False
                p["all_in"] = False
                active_count += 1
            p["current_bet"] = 0
            p["total_bet_in_hand"] = 0
            p["hole_cards"] = []
            p["last_action"] = ""
            p["has_acted"] = False
            
        if active_count < 2:
            self.state["round"] = "finished"
            # Find the winner
            winners = [p["name"] for p in players if not p.get("eliminated", False)]
            winner_str = winners[0] if winners else "No one"
            self.state["last_action_desc"] = f"Game Over! {winner_str} wins the tournament!"
            self.state["current_player"] = -1
            self.save_state()
            return

        # Advance dealer button
        num_players = len(players)
        while True:
            self.state["dealer_button"] = (self.state["dealer_button"] + 1) % num_players
            if not players[self.state["dealer_button"]]["eliminated"]:
                break
        
        # Prepare deck
        deck = [f"{r}{s}" for r in RANKS for s in SUITS]
        random.shuffle(deck)
        self.state["deck"] = deck
        
        # Deal hole cards
        for p in players:
            if not p["eliminated"]:
                p["hole_cards"] = [self.state["deck"].pop(), self.state["deck"].pop()]

        self.state["community_cards"] = []
        self.state["pot"] = 0
        self.state["hand_count"] += 1
        self.state["round"] = "preflop"
        
        # Post Blinds
        sb_amt = 5
        bb_amt = 10
        
        # Find SB player (first active player to the left of button)
        sb_idx = self.find_next_active_player(self.state["dealer_button"])
        # Find BB player (first active player to the left of SB)
        bb_idx = self.find_next_active_player(sb_idx)
        
        # SB Post
        sb_player = players[sb_idx]
        sb_post = min(sb_amt, sb_player["chips"])
        sb_player["chips"] -= sb_post
        sb_player["current_bet"] = sb_post
        sb_player["total_bet_in_hand"] = sb_post
        sb_player["last_action"] = f"Posts SB {sb_post}"
        if sb_player["chips"] == 0:
            sb_player["all_in"] = True
            
        # BB Post
        bb_player = players[bb_idx]
        bb_post = min(bb_amt, bb_player["chips"])
        bb_player["chips"] -= bb_post
        bb_player["current_bet"] = bb_post
        bb_player["total_bet_in_hand"] = bb_post
        bb_player["last_action"] = f"Posts BB {bb_post}"
        if bb_player["chips"] == 0:
            bb_player["all_in"] = True

        self.state["current_round_highest_bet"] = max(sb_post, bb_post)
        self.state["last_raise_increment"] = 10
        
        # In preflop, action starts left of Big Blind
        self.state["current_player"] = self.find_next_active_player(bb_idx)
        self.state["last_action_desc"] = f"Hand #{self.state['hand_count']} started. Blinds posted: SB {sb_player['name']} ({sb_post}), BB {bb_player['name']} ({bb_post})."
        
        # Reset other players' has_acted flags (SB and BB haven't fully acted yet)
        for p in players:
            p["has_acted"] = False
            
        # Check if pre-flop betting is already settled (e.g. if everyone is all-in)
        self.check_betting_round_settled()
        self.save_state()

    def find_next_active_player(self, start_idx):
        players = self.state["players"]
        num_players = len(players)
        idx = (start_idx + 1) % num_players
        for _ in range(num_players):
            p = players[idx]
            if not p["eliminated"] and not p["folded"] and not p["all_in"]:
                return idx
            idx = (idx + 1) % num_players
        return start_idx

    def process_action(self, player_name, action_type, amount=0):
        players = self.state["players"]
        curr_idx = self.state["current_player"]
        
        if curr_idx == -1:
            raise ValueError("No active hand is playing. Run next_hand or init.")

        curr_player = players[curr_idx]
        if curr_player["name"] != player_name:
            raise ValueError(f"It is {curr_player['name']}'s turn, not {player_name}'s.")

        highest_bet = self.state["current_round_highest_bet"]
        call_needed = highest_bet - curr_player["current_bet"]
        action_desc = ""

        if action_type == "fold":
            curr_player["folded"] = True
            curr_player["last_action"] = "Fold"
            action_desc = f"{player_name} folds."
            
        elif action_type == "check":
            if call_needed > 0:
                raise ValueError(f"Cannot check. Must call {call_needed} or fold.")
            curr_player["last_action"] = "Check"
            curr_player["has_acted"] = True
            action_desc = f"{player_name} checks."
            
        elif action_type == "call":
            call_amt = min(call_needed, curr_player["chips"])
            curr_player["chips"] -= call_amt
            curr_player["current_bet"] += call_amt
            curr_player["total_bet_in_hand"] += call_amt
            curr_player["has_acted"] = True
            
            if curr_player["chips"] == 0:
                curr_player["all_in"] = True
                curr_player["last_action"] = f"Calls {call_amt} (All-in)"
                action_desc = f"{player_name} calls {call_amt} and is All-in!"
            else:
                curr_player["last_action"] = f"Calls {call_amt}"
                action_desc = f"{player_name} calls {call_amt}."
                
        elif action_type == "raise":
            # amount is the target total bet size for this round
            last_inc = self.state.get("last_raise_increment", 10)
            if amount < highest_bet + last_inc and amount < curr_player["chips"] + curr_player["current_bet"]:
                min_raise = highest_bet + last_inc
                raise ValueError(f"Raise amount {amount} must be at least {min_raise} or all-in.")
                
            raise_added = amount - curr_player["current_bet"]
            if raise_added > curr_player["chips"]:
                # If they try to raise more than chips, force All-in
                raise_added = curr_player["chips"]
                amount = curr_player["current_bet"] + raise_added

            curr_player["chips"] -= raise_added
            curr_player["current_bet"] += raise_added
            curr_player["total_bet_in_hand"] += raise_added
            curr_player["has_acted"] = True
            
            raise_increment = amount - highest_bet
            self.state["last_raise_increment"] = max(last_inc, raise_increment)
            self.state["current_round_highest_bet"] = amount
            
            # Since bet increased, everyone else (active, non-all-in) must act again
            for p in players:
                if p["name"] != player_name:
                    p["has_acted"] = False

            if curr_player["chips"] == 0:
                curr_player["all_in"] = True
                curr_player["last_action"] = f"Raises to {amount} (All-in)"
                action_desc = f"{player_name} raises to {amount} and is All-in!"
            else:
                curr_player["last_action"] = f"Raises to {amount}"
                action_desc = f"{player_name} raises to {amount}."
        else:
            raise ValueError(f"Unknown action type: {action_type}")

        self.state["last_action_desc"] = action_desc

        # Check if hand immediately ends because only one player is left
        active_players = [p for p in players if not p["folded"] and not p["eliminated"]]
        if len(active_players) == 1:
            # Single remaining player wins the pot
            winner = active_players[0]
            pot = self.state["pot"] + sum(p["current_bet"] for p in players)
            winner["chips"] += pot
            self.state["pot"] = 0
            # Reset current bets
            for p in players:
                p["current_bet"] = 0
            self.state.pop("showdown_results", None)
            self.state["round"] = "finished"
            self.state["current_player"] = -1
            self.state["last_action_desc"] += f" Everyone else folded. {winner['name']} wins the pot of {pot}."
            self.save_state()
            return

        # Check if betting round is settled
        settled = self.check_betting_round_settled()
        if not settled:
            self.state["current_player"] = self.find_next_active_player(curr_idx)
        self.save_state()

    def check_betting_round_settled(self):
        players = self.state["players"]
        highest_bet = self.state["current_round_highest_bet"]
        
        # Betting round is settled if:
        # 1. All active (non-folded, non-allin) players have acted.
        # 2. All active, non-allin players have current_bet == highest_bet.
        deciding_players = [p for p in players if not p["folded"] and not p["eliminated"] and not p["all_in"]]
        
        settled = True
        for p in deciding_players:
            if not p["has_acted"] or p["current_bet"] != highest_bet:
                settled = False
                break

        # Special case: if there are 0 or 1 players left who can make decisions, and everyone else is folded or all-in,
        # then no more betting can happen in this round.
        if len(deciding_players) < 2:
            # Check if there is still a mismatch in bets between the one deciding player and all-in players
            # Actually, if the deciding player has acted or matches the current bet, or there's no more bets to resolve:
            # Let's see: if everyone who can act has acted, we can settle the round.
            if len(deciding_players) == 1:
                # The single active player must have acted and matched the highest bet (or checked)
                p = deciding_players[0]
                if not p["has_acted"] or p["current_bet"] < highest_bet:
                    settled = False

        if settled:
            # Settle bets into the pot
            round_contrib = sum(p["current_bet"] for p in players)
            self.state["pot"] += round_contrib
            for p in players:
                p["current_bet"] = 0
                p["has_acted"] = False
            self.state["current_round_highest_bet"] = 0
            self.state["last_raise_increment"] = 10
            
            # Transition to next round
            self.advance_round()
            return True
        return False

    def advance_round(self):
        curr_round = self.state["round"]
        deck = self.state["deck"]
        players = self.state["players"]

        # Check if we should skip betting rounds (all-in runout)
        # If less than 2 players are active and have chips remaining, they can't make choices.
        deciding_players = [p for p in players if not p["folded"] and not p["eliminated"] and not p["all_in"]]
        
        if len(deciding_players) < 2:
            # Auto-runout to Showdown
            while curr_round not in ("showdown", "finished"):
                if curr_round == "preflop":
                    # Burn 1, Deal 3 Flop
                    deck.pop()
                    self.state["community_cards"].extend([deck.pop(), deck.pop(), deck.pop()])
                    curr_round = "flop"
                elif curr_round == "flop":
                    # Burn 1, Deal 1 Turn
                    deck.pop()
                    self.state["community_cards"].append(deck.pop())
                    curr_round = "turn"
                elif curr_round == "turn":
                    # Burn 1, Deal 1 River
                    deck.pop()
                    self.state["community_cards"].append(deck.pop())
                    curr_round = "river"
                elif curr_round == "river":
                    curr_round = "showdown"
            
            self.state["round"] = "showdown"
            self.execute_showdown()
            return

        # Normal advancement
        if curr_round == "preflop":
            # Flop
            deck.pop() # Burn
            self.state["community_cards"].extend([deck.pop(), deck.pop(), deck.pop()])
            self.state["round"] = "flop"
            self.state["current_player"] = self.find_first_active_player_postflop()
            self.state["last_action_desc"] += " Transition to Flop."
        elif curr_round == "flop":
            # Turn
            deck.pop() # Burn
            self.state["community_cards"].append(deck.pop())
            self.state["round"] = "turn"
            self.state["current_player"] = self.find_first_active_player_postflop()
            self.state["last_action_desc"] += " Transition to Turn."
        elif curr_round == "turn":
            # River
            deck.pop() # Burn
            self.state["community_cards"].append(deck.pop())
            self.state["round"] = "river"
            self.state["current_player"] = self.find_first_active_player_postflop()
            self.state["last_action_desc"] += " Transition to River."
        elif curr_round == "river":
            self.state["round"] = "showdown"
            self.execute_showdown()
        
        # Check if the advanced round is already settled (e.g. if a player was all-in preflop)
        if self.state["round"] != "showdown" and self.state["round"] != "finished":
            self.check_betting_round_settled()

    def find_first_active_player_postflop(self):
        # Post-flop betting starts with the Small Blind or first active player left of Button
        players = self.state["players"]
        num_players = len(players)
        idx = (self.state["dealer_button"] + 1) % num_players
        for _ in range(num_players):
            p = players[idx]
            if not p["eliminated"] and not p["folded"] and not p["all_in"]:
                return idx
            idx = (idx + 1) % num_players
        return -1

    def execute_showdown(self):
        players = self.state["players"]
        community = self.state["community_cards"]
        pot = self.state["pot"]
        
        # Get active, non-folded players
        active_players = [p for p in players if not p["folded"] and not p["eliminated"]]
        
        # Evaluate hand for each active player
        player_scores = {}
        for p in active_players:
            score = evaluate_7_card_hand(p["hole_cards"], community)
            player_scores[p["name"]] = score

        # Sort scores to figure out rank
        # We need to distribute chips correctly, respecting side pots.
        # Side pot algorithm:
        # 1. We know each player's total_bet_in_hand
        # 2. Iterate and split pot into side pots based on player contributions.
        showdown_results = []
        payouts = {p["name"]: 0 for p in players}
        
        # Save a copy of player contributions for evaluation
        contributions = {p["name"]: p["total_bet_in_hand"] for p in players}
        
        # While there are chips in play in the contributions:
        # We find the smallest contribution of any player who is active/folded (but not eliminated with 0 bet).
        # We group contributions, find the winners among eligible active players, and distribute.
        remaining_pot = pot
        
        while sum(contributions.values()) > 0:
            # Find the active players who have a contribution > 0
            contrib_players = [name for name, contrib in contributions.items() if contrib > 0]
            if not contrib_players:
                break
                
            # Find the minimum contribution in this tier
            min_contrib = min(contributions[name] for name in contrib_players)
            
            # Create a sub-pot for this tier
            tier_pot = 0
            tier_contributors = []
            for name in contributions.keys():
                contrib = contributions[name]
                take = min(min_contrib, contrib)
                tier_pot += take
                contributions[name] -= take
                if take > 0:
                    tier_contributors.append(name)
            
            # Eligible players to win this tier pot are active players in this tier (non-folded)
            eligible_winners = [name for name in tier_contributors if name in player_scores]
            
            if not eligible_winners:
                # If no active player is eligible (e.g. they all folded, which shouldn't happen for the last player,
                # but could happen if someone folded and only all-in players are active),
                # refund the pot to the contributors
                for name in tier_contributors:
                    payouts[name] += min_contrib # simple refund
                continue
                
            # Determine the winner(s) among eligible players
            best_score = None
            winners = []
            for name in eligible_winners:
                score = player_scores[name]
                if best_score is None or score > best_score:
                    best_score = score
                    winners = [name]
                elif score == best_score:
                    winners.append(name)
            
            # Distribute tier pot to winner(s)
            split_share = tier_pot // len(winners)
            remainder = tier_pot % len(winners)
            
            for i, winner_name in enumerate(winners):
                payouts[winner_name] += split_share
                if i == 0:
                    payouts[winner_name] += remainder # Give remainder to first winner
                    
        # Apply payouts
        for name, amount in payouts.items():
            for p in players:
                if p["name"] == name:
                    p["chips"] += amount

        # Build showdown results for display
        for p in active_players:
            score = player_scores[p["name"]]
            rank_name = get_hand_rank_name(score[0])
            showdown_results.append({
                "name": p["name"],
                "hole_cards": p["hole_cards"],
                "hand_rank_name": rank_name,
                "won_chips": payouts[p["name"]],
                "score_repr": str(score)
            })

        # Add players who folded but spent chips
        for p in players:
            if p["folded"] and not p["eliminated"] and payouts.get(p["name"], 0) > 0:
                showdown_results.append({
                    "name": p["name"],
                    "hole_cards": p["hole_cards"],
                    "hand_rank_name": "Folded",
                    "won_chips": payouts[p["name"]],
                    "score_repr": ""
                })

        self.state["showdown_results"] = showdown_results
        self.state["round"] = "finished"
        self.state["current_player"] = -1
        
        # Clear bets
        for p in players:
            p["current_bet"] = 0
            
        winner_names = [r["name"] for r in showdown_results if r["won_chips"] > 0]
        self.state["last_action_desc"] = f"Showdown completed. Winners: {', '.join(winner_names)}."
        self.state["pot"] = 0

def main():
    engine = PokerEngine()
    engine.load_state()

    if len(sys.argv) < 2:
        print("Usage: poker_engine.py [init | action | next_hand | show] ...")
        sys.exit(1)

    cmd = sys.argv[1]

    try:
        if cmd == "init":
            # --players <names_comma_separated>
            players_str = "You,Alex,Jamie,Taylor,Morgan,Casey"
            if "--players" in sys.argv:
                idx = sys.argv.index("--players")
                players_str = sys.argv[idx + 1]
            player_names = [p.strip() for p in players_str.split(",")]
            engine.init_game(player_names)
            engine.print_state_json()
            
        elif cmd == "action":
            # --player <name> --type <fold/check/call/raise> [--amount <amount>]
            player = None
            action_type = None
            amount = 0
            
            if "--player" in sys.argv:
                player = sys.argv[sys.argv.index("--player") + 1]
            if "--type" in sys.argv:
                action_type = sys.argv[sys.argv.index("--type") + 1]
            if "--amount" in sys.argv:
                amount = int(sys.argv[sys.argv.index("--amount") + 1])
                
            if not player or not action_type:
                print("Error: --player and --type are required for action.", file=sys.stderr)
                sys.exit(1)
                
            engine.process_action(player, action_type, amount)
            
            # If the round advanced to finished (or showdown) during process_action, 
            # the state will show the showdown results.
            engine.print_state_json()
            
        elif cmd == "next_hand":
            engine.start_next_hand()
            engine.print_state_json()
            
        elif cmd == "show":
            engine.print_state_json()
            
        else:
            print(f"Unknown command: {cmd}", file=sys.stderr)
            sys.exit(1)
            
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main()
