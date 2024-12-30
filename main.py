'''
TODO:
calculate the player advantage for the next hand using Monte Carlo simulations
print the estimated player advantage and the best bet value
graph it alongside player advantage given by High-Low card counting over
the course of a n deck shoe
'''

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

    # max count of cards for a hand (1 player):
    # player: 4 * 1 + 4 * 2 + 3 * 3 | dealer: 3 + 4 * 4   ->   16
    deck = np.random.choice(deck, size=16, replace=True)

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

    # check for blackjack -> has 3:2 returns
    if sum(player_hand) == 21:
        if sum(dealer_hand) == 21:
            return 0
        else:
            return 1.5

    # save dealers up-card -> matters for playing perfect strategy
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
    '''# create num_simulations copies of deck
    decks = np.tile(deck, (num_simulations, 1))
    # shuffle all the decks differently
    for i in range(num_simulations):
        np.random.shuffle(decks[i])
    # get results
    results = np.vectorize(simulate_hand, signature="(n)->()")(decks)'''

    results = list()
    for _ in range(num_simulations):
        results.append(simulate_hand(deck))

    #print(results)
    results = np.array(results)
    wins = np.count_nonzero(results == 1)
    losses = np.count_nonzero(results == -1)
    blackjack = np.count_nonzero(results == 1.5)
    ties = np.count_nonzero(results == 0)
    p_win = wins / num_simulations
    p_loss = losses / num_simulations
    p_blackjack = blackjack / num_simulations
    p_tie = ties / num_simulations
    print(f"Wins: {wins}, Losses: {losses}, BlackJacks: {blackjack}")
    # Calculate expected value
    ev = np.sum(results) / num_simulations
    var = (
            (p_win * (1 - ev) ** 2) +
            (p_blackjack * (1.5 - ev) ** 2) +
            (p_loss * (-1 - ev) ** 2) +
            (p_tie * (0 - ev) ** 2)
    )
    return ev, var



# Define parameters
num_simulations = 115377 # epsilon = 0.01
num_hands = 100
initial_deck = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11] * 4
bankroll = 100000

# Run simulation and print results
avg_ev = 0
avg_var = 0
Max = -1
Min = float('inf')
for _ in range(num_hands):
    expected_value, variance = monte_carlo_blackjack(initial_deck, num_simulations)
    Max = max(Max, expected_value)
    Min = min(Min, expected_value)
    avg_ev += expected_value
    avg_var += variance
    print(f"ev: {expected_value}, var: {variance}")
    print(f"Expected Value of the Next Bet: {bankroll * expected_value / variance}")

print(f"Average ev over {num_hands} hands: {avg_ev / num_hands}")
print(f"Average var over {num_hands} hands: {avg_var / num_hands}")
print(f"Max: {Max}, Min: {Min}")
