#!/usr/bin/env python3
import unittest
from poker_engine import evaluate_5_card_hand, evaluate_7_card_hand, Card, PokerEngine

class TestPokerEvaluator(unittest.TestCase):
    def test_5_card_evaluator(self):
        # Straight Flush
        sf = [Card("As"), Card("Ks"), Card("Qs"), Card("Js"), Card("10s")]
        self.assertEqual(evaluate_5_card_hand(sf)[0], 8)
        self.assertEqual(evaluate_5_card_hand(sf)[1], [14])

        # Ace-low Straight Flush
        sf_low = [Card("5d"), Card("4d"), Card("3d"), Card("2d"), Card("Ad")]
        self.assertEqual(evaluate_5_card_hand(sf_low)[0], 8)
        self.assertEqual(evaluate_5_card_hand(sf_low)[1], [5])

        # Four of a Kind
        quads = [Card("Ah"), Card("As"), Card("Ac"), Card("Ad"), Card("Kc")]
        self.assertEqual(evaluate_5_card_hand(quads)[0], 7)
        self.assertEqual(evaluate_5_card_hand(quads)[1], [14, 13])

        # Full House
        fh = [Card("Kh"), Card("Ks"), Card("Kc"), Card("Qd"), Card("Qc")]
        self.assertEqual(evaluate_5_card_hand(fh)[0], 6)
        self.assertEqual(evaluate_5_card_hand(fh)[1], [13, 12])

        # Flush
        flush = [Card("Ad"), Card("Jd"), Card("8d"), Card("4d"), Card("2d")]
        self.assertEqual(evaluate_5_card_hand(flush)[0], 5)
        self.assertEqual(evaluate_5_card_hand(flush)[1], [14, 11, 8, 4, 2])

        # Straight
        straight = [Card("9h"), Card("8s"), Card("7c"), Card("6d"), Card("5c")]
        self.assertEqual(evaluate_5_card_hand(straight)[0], 4)
        self.assertEqual(evaluate_5_card_hand(straight)[1], [9])

        # Three of a Kind
        trips = [Card("Qh"), Card("Qs"), Card("Qc"), Card("Ad"), Card("2c")]
        self.assertEqual(evaluate_5_card_hand(trips)[0], 3)
        self.assertEqual(evaluate_5_card_hand(trips)[1], [12, 14, 2])

        # Two Pair
        twopair = [Card("Jh"), Card("Js"), Card("10c"), Card("10d"), Card("Ac")]
        self.assertEqual(evaluate_5_card_hand(twopair)[0], 2)
        self.assertEqual(evaluate_5_card_hand(twopair)[1], [11, 10, 14])

        # One Pair
        onepair = [Card("2h"), Card("2s"), Card("Ac"), Card("Kd"), Card("Qc")]
        self.assertEqual(evaluate_5_card_hand(onepair)[0], 1)
        self.assertEqual(evaluate_5_card_hand(onepair)[1], [2, 14, 13, 12])

        # High Card
        highcard = [Card("Ah"), Card("Qd"), Card("10s"), Card("7c"), Card("2h")]
        self.assertEqual(evaluate_5_card_hand(highcard)[0], 0)
        self.assertEqual(evaluate_5_card_hand(highcard)[1], [14, 12, 10, 7, 2])

    def test_7_card_evaluator(self):
        # 7 cards: As Ks Qs Js 10s 2h 3d -> should choose the Straight Flush
        hole = ["As", "Ks"]
        community = ["Qs", "Js", "10s", "2h", "3d"]
        score = evaluate_7_card_hand(hole, community)
        self.assertEqual(score[0], 8)
        self.assertEqual(score[1], [14])

        # Two Pair with higher kickers on board
        hole = ["2h", "3d"]
        community = ["As", "Kd", "Qc", "Ac", "Ks"]
        # Best hand: Ac As Ks Kd Qc (Two Pair: A & K, Q kicker)
        score = evaluate_7_card_hand(hole, community)
        self.assertEqual(score[0], 2)
        self.assertEqual(score[1], [14, 13, 12])

    def test_tie_breakers(self):
        # Two Pair comparison
        hand1 = evaluate_5_card_hand([Card("Ah"), Card("As"), Card("Kh"), Card("Ks"), Card("Qc")])
        hand2 = evaluate_5_card_hand([Card("Ad"), Card("Ac"), Card("Kd"), Card("Kc"), Card("Jc")])
        self.assertTrue(hand1 > hand2) # Q kicker beats J kicker

        # Full House comparison
        fh1 = evaluate_5_card_hand([Card("Kh"), Card("Ks"), Card("Kc"), Card("Qd"), Card("Qc")])
        fh2 = evaluate_5_card_hand([Card("Kd"), Card("Ks"), Card("Kc"), Card("Jd"), Card("Jc")])
        self.assertTrue(fh1 > fh2) # KKKQQ beats KKKJJ

class TestPokerEngine(unittest.TestCase):
    def setUp(self):
        self.engine = PokerEngine()

    def test_initialization(self):
        player_names = ["You", "Alice", "Bob"]
        self.engine.init_game(player_names)
        state = self.engine.state
        
        self.assertEqual(state["hand_count"], 1)
        self.assertEqual(len(state["players"]), 3)
        self.assertEqual(state["round"], "preflop")
        self.assertEqual(len(state["community_cards"]), 0)
        self.assertTrue(state["pot"] == 0) # Blinds are in players' current_bet, not pot yet
        
        # Check that blinds are posted
        # Dealer button is random. Let's see:
        # SB is (button+1)%3, BB is (button+2)%3
        # Current player should be (button+3)%3 which is button (preflop starts left of BB)
        btn = state["dealer_button"]
        sb_idx = (btn + 1) % 3
        bb_idx = (btn + 2) % 3
        curr_idx = state["current_player"]
        
        self.assertEqual(curr_idx, btn)
        self.assertEqual(state["players"][sb_idx]["current_bet"], 5)
        self.assertEqual(state["players"][bb_idx]["current_bet"], 10)
        self.assertEqual(state["players"][sb_idx]["chips"], 995)
        self.assertEqual(state["players"][bb_idx]["chips"], 990)

    def test_game_flow_simple(self):
        # Make a mock game with known button and deck
        player_names = ["You", "Alice", "Bob"]
        self.engine.init_game(player_names)
        
        # Let's force the dealer button to 0 (You)
        self.engine.state["dealer_button"] = 0
        self.engine.state["players"][0]["chips"] = 1000
        self.engine.state["players"][1]["chips"] = 1000
        self.engine.state["players"][2]["chips"] = 1000
        
        # Reset bets and start preflop
        # SB is Alice (1), BB is Bob (2)
        # UTG is You (0)
        self.engine.state["players"][0]["current_bet"] = 0
        self.engine.state["players"][1]["current_bet"] = 5
        self.engine.state["players"][2]["current_bet"] = 10
        self.engine.state["players"][0]["chips"] = 1000
        self.engine.state["players"][1]["chips"] = 995
        self.engine.state["players"][2]["chips"] = 990
        self.engine.state["players"][0]["total_bet_in_hand"] = 0
        self.engine.state["players"][1]["total_bet_in_hand"] = 5
        self.engine.state["players"][2]["total_bet_in_hand"] = 10
        
        self.engine.state["current_player"] = 0
        self.engine.state["current_round_highest_bet"] = 10
        self.engine.state["round"] = "preflop"
        self.engine.state["pot"] = 0
        
        # Reset has_acted
        for p in self.engine.state["players"]:
            p["has_acted"] = False
            p["folded"] = False
            p["all_in"] = False

        # UTG (You) Calls 10
        self.engine.process_action("You", "call")
        self.assertEqual(self.engine.state["players"][0]["current_bet"], 10)
        self.assertEqual(self.engine.state["players"][0]["chips"], 990)
        self.assertEqual(self.engine.get_current_player_name(), "Alice")
        
        # Alice (SB) Calls 10 (she already has 5 in)
        self.engine.process_action("Alice", "call")
        self.assertEqual(self.engine.state["players"][1]["current_bet"], 10)
        self.assertEqual(self.engine.state["players"][1]["chips"], 990)
        self.assertEqual(self.engine.get_current_player_name(), "Bob")
        
        # Bob (BB) Checks (already has 10 in)
        self.engine.process_action("Bob", "check")
        
        # Round should advance to Flop!
        self.assertEqual(self.engine.state["round"], "flop")
        self.assertEqual(self.engine.state["pot"], 30)
        self.assertEqual(len(self.engine.state["community_cards"]), 3)
        # Post-flop starts with Small Blind (Alice)
        self.assertEqual(self.engine.get_current_player_name(), "Alice")

    def test_side_pots(self):
        # 3 players: You, Alice, Bob
        self.engine.init_game(["You", "Alice", "Bob"])
        
        # Override cards and bets to simulate pre-flop all-in
        # You: all-in for 100
        # Alice: all-in for 200
        # Bob: calls 200
        
        self.engine.state["players"][0]["hole_cards"] = ["As", "Ks"] # You (Royal flush potential)
        self.engine.state["players"][1]["hole_cards"] = ["Qc", "Qh"] # Alice (Three of a kind potential)
        self.engine.state["players"][2]["hole_cards"] = ["2c", "2d"] # Bob (One pair potential)
        
        self.engine.state["community_cards"] = ["Qs", "Js", "10s", "3c", "4d"]
        # Community cards give:
        # You: As Ks Qs Js 10s -> Royal Flush (rank 8, high 14)
        # Alice: Qc Qh Qs Js 10s -> Three of a Kind Queens (rank 3, high 12, kickers 14, 11)
        # Bob: 2c 2d Qs Js 10s -> One Pair Twos (rank 1, high 2, kickers 12, 11, 10)
        
        self.engine.state["players"][0]["total_bet_in_hand"] = 100
        self.engine.state["players"][0]["chips"] = 0
        self.engine.state["players"][0]["all_in"] = True
        
        self.engine.state["players"][1]["total_bet_in_hand"] = 200
        self.engine.state["players"][1]["chips"] = 0
        self.engine.state["players"][1]["all_in"] = True
        
        self.engine.state["players"][2]["total_bet_in_hand"] = 200
        self.engine.state["players"][2]["chips"] = 800
        
        # Pot is 500
        self.engine.state["pot"] = 500
        self.engine.state["round"] = "showdown"
        
        self.engine.execute_showdown()
        
        # Payout calculations:
        # Main pot (You, Alice, Bob contribute 100 each): 300. Won by You (Royal Flush).
        # Side pot 1 (Alice and Bob contribute 100 each): 200. Won by Alice (Three of a Kind beats Bob's One Pair).
        # Bob wins 0.
        
        # Final chips:
        # You: was 0 + 300 = 300
        # Alice: was 0 + 200 = 200
        # Bob: was 800 + 0 = 800
        
        self.assertEqual(self.engine.state["players"][0]["chips"], 300)
        self.assertEqual(self.engine.state["players"][1]["chips"], 200)
        self.assertEqual(self.engine.state["players"][2]["chips"], 800)

    def test_raise_increment(self):
        # Initialize game
        self.engine.init_game(["You", "Alice", "Bob"])
        self.engine.state["dealer_button"] = 0
        
        # SB is Alice (1), BB is Bob (2)
        # UTG is You (0)
        self.engine.state["players"][0]["current_bet"] = 0
        self.engine.state["players"][1]["current_bet"] = 5
        self.engine.state["players"][2]["current_bet"] = 10
        self.engine.state["players"][0]["chips"] = 1000
        self.engine.state["players"][1]["chips"] = 995
        self.engine.state["players"][2]["chips"] = 990
        
        self.engine.state["current_player"] = 0
        self.engine.state["current_round_highest_bet"] = 10
        self.engine.state["last_raise_increment"] = 10
        self.engine.state["round"] = "preflop"
        
        # UTG (You) raises to 40 (increase of 30 over 10)
        self.engine.process_action("You", "raise", 40)
        self.assertEqual(self.engine.state["last_raise_increment"], 30)
        self.assertEqual(self.engine.state["current_round_highest_bet"], 40)
        
        # Next is Alice (current player is now Alice)
        # Alice tries to raise to 50 (which is an increase of 10 over 40)
        # This should fail because minimum re-raise must be at least 40 + 30 = 70.
        with self.assertRaises(ValueError):
            self.engine.process_action("Alice", "raise", 50)
            
        # Alice raises to 70 (which is a valid raise)
        self.engine.process_action("Alice", "raise", 70)
        self.assertEqual(self.engine.state["last_raise_increment"], 30)
        self.assertEqual(self.engine.state["current_round_highest_bet"], 70)

if __name__ == "__main__":
    unittest.main()
