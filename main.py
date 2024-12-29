'''
TODO:
calculate the player advantage for the next hand using Monte Carlo simulations
print the estimated player advantage and the best bet value
graph it alongside player advantage given by High-Low card counting over
the course of a n deck shoe
'''

# max count of cards for a hand (1 player):
# player: 4 * 1 + 4 * 2 + 3 * 3 | dealer: 3 + 4 * 4   ->   16

import random
from copy import deepcopy
import numpy as np

# perfect strategy tables
hard_totals = {
    21: ['s'] * 10,
    20: ['s'] * 10,
    19: ['s'] * 10,
    18: ['s'] * 10,
    17: ['s'] * 10,
    16: ['s'] * 5 + ['h'] * 5,
    15: ['s'] * 5 + ['h'] * 5,
    14: ['s'] * 5 + ['h'] * 5,
    13: ['s'] * 5 + ['h'] * 5,
    12: ['h'] * 2 + ['s'] * 3 + ['h'] * 5,
    11: ['h'] * 10,
    10: ['h'] * 10,
    9: ['h'] * 10,
    8: ['h'] * 10,
    7: ['h'] * 10,
    6: ['h'] * 10,
    5: ['h'] * 10,
    4: ['h'] * 10,
    3: ['h'] * 10,
    2: ['h'] * 10,
}

soft_totals = {
    21: ['s'] * 10,
    20: ['s'] * 10,
    19: ['s'] * 10,
    18: ['s'] * 7 + ['h'] * 3,
    17: ['h'] * 10,
    16: ['h'] * 10,
    15: ['h'] * 10,
    14: ['h'] * 10,
    13: ['h'] * 10,
}


# Function to simulate one blackjack hand
def simulate_hand(deck):
    def hand_value(hand):
        value = sum(hand)
        # Adjust for aces
        if value > 21 and 11 in hand:
            hand[hand.index(11)] = 1
            value = sum(hand)
            # hand is no longer soft total (ace value was switched to 1)
            nonlocal is_soft_total
            is_soft_total = False
        return value

    def dealer_play(deck, dealer_hand):
        while hand_value(dealer_hand) < 17:
            dealer_hand.append(deck.pop(0))
        return hand_value(dealer_hand)

    deck = deck.tolist()

    # Deal hands
    player_hand = [deck.pop(0), deck.pop(0)]
    dealer_hand = [deck.pop(0), deck.pop(0)]
    up_card = dealer_hand[0]

    # check if player hand is soft total
    # if the hand has an ace that can be counted as an 11, it is a soft total
    # otherwise the hand is a hard total
    is_soft_total = (11 in player_hand and sum(player_hand) <= 21)

    # Player plays

    player_value = hand_value(player_hand)
    #print(player_hand, player_value)

    if is_soft_total:
        curr_move = soft_totals[player_value][up_card - 2]
    else:
        curr_move = hard_totals[player_value][up_card - 2]

    while curr_move == 'h':
        player_hand.append(deck.pop(0))
        player_value = hand_value(player_hand)
        if player_value > 21:
            # busted
            break

        if is_soft_total:
            curr_move = soft_totals[player_value][up_card - 2]
        else:
            curr_move = hard_totals[player_value][up_card - 2]

    # If player busts
    if player_value > 21:
        return -1  # Loss

    # Dealer plays
    dealer_value = dealer_play(deck, dealer_hand)

    # Determine result
    if dealer_value > 21 or player_value > dealer_value:
        return 1  # Win
    elif player_value == dealer_value:
        return 0  # Tie
    else:
        return -1  # Loss


# Function for Monte Carlo Simulation
def monte_carlo_blackjack(deck, num_simulations=1000):
    # create num_simulations copies of deck
    decks = np.tile(deck, (num_simulations, 1))
    # shuffle all the decks differently
    for i in range(num_simulations):
        np.random.shuffle(decks[i])
    # get results
    results = np.vectorize(simulate_hand, signature="(n)->()")(decks)

    #print(results)
    # Calculate expected value
    ev = np.sum(results) / num_simulations
    return ev



# Define parameters
num_simulations = 10000
num_hands = 500
initial_deck = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11] * 4

# Run simulation and print results
avg = 0
Max = -1
Min = float('inf')
for _ in range(num_hands):
    expected_value = monte_carlo_blackjack(initial_deck, num_simulations)
    Max = max(Max, expected_value)
    Min = min(Min, expected_value)
    avg += expected_value
    #print(f"Expected Value of the Next Bet: {expected_value:.4f}")

print(f"Average ev over {num_hands} hands: {avg / num_hands}")
print(f"Max: {Max}, Min: {Min}")
