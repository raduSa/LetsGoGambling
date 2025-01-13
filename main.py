import numpy as np

# perfect strategy tables
hard_totals = {
    21: ['stay'] * 10,
    20: ['stay'] * 10,
    19: ['stay'] * 10,
    18: ['stay'] * 10,
    17: ['stay'] * 10,
    16: ['stay'] * 5 + ['hit'] * 5,
    15: ['stay'] * 5 + ['hit'] * 5,
    14: ['stay'] * 5 + ['hit'] * 5,
    13: ['stay'] * 5 + ['hit'] * 5,
    12: ['hit'] * 2 + ['stay'] * 3 + ['hit'] * 5,
    11: ['hit'] * 10,
    10: ['hit'] * 10,
    9: ['hit'] * 10,
    8: ['hit'] * 10,
    7: ['hit'] * 10,
    6: ['hit'] * 10,
    5: ['hit'] * 10,
    4: ['hit'] * 10,
    3: ['hit'] * 10,
    2: ['hit'] * 10,
}

soft_totals = {
    21: ['stay'] * 10,
    20: ['stay'] * 10,
    19: ['stay'] * 10,
    18: ['stay'] * 7 + ['hit'] * 3,
    17: ['hit'] * 10,
    16: ['hit'] * 10,
    15: ['hit'] * 10,
    14: ['hit'] * 10,
    13: ['hit'] * 10,
}


# Function to simulate one blackjack hand
def simulate_hand(deck, remove_from_deck):
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
            dealt_card = deck.pop(0)
            dealer_hand.append(dealt_card)
            if remove_from_deck:
                initial_deck.remove(dealt_card)
        return hand_value(dealer_hand)

    if not remove_from_deck:
        deck = deck.tolist()

    # Deal hands
    player_hand = [deck.pop(0), deck.pop(0)]
    dealer_hand = [deck.pop(0), deck.pop(0)]

    # Remove dealt cards
    if remove_from_deck:
        for card in player_hand:
            initial_deck.remove(card)
        for card in dealer_hand:
            initial_deck.remove(card)

    # check for blackjack -> has 3:2 returns
    if sum(player_hand) == 21:
        if sum(dealer_hand) == 21:
            return 0
        else:
            return 1.5

    # check if player hand is soft total
    # if the hand has an ace that can be counted as an 11, it is a soft total
    # otherwise the hand is a hard total
    is_soft_total = (11 in player_hand and sum(player_hand) <= 21)

    # Player plays
    player_value = hand_value(player_hand)

    # print(player_hand, player_value)

    # save dealers up-card -> matters for playing perfect strategy
    up_card = dealer_hand[0]

    if is_soft_total:
        curr_move = soft_totals[player_value][up_card - 2]
    else:
        curr_move = hard_totals[player_value][up_card - 2]

    while curr_move == 'hit':
        dealt_card = deck.pop(0)
        player_hand.append(dealt_card)
        if remove_from_deck:
            initial_deck.remove(dealt_card)
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
    # max count of cards for a hand (1 player):
    # player: 4 * 1 + 4 * 2 + 3 * 3 | dealer: 3 + 4 * 4   ->   16

    # create num_simulations copies of deck (simulate only 16 cards per deck)
    decks = np.random.choice(deck, size=(num_simulations, 16), replace=True)

    results = list()
    for curr_deck in decks:
        results.append(simulate_hand(curr_deck, remove_from_deck=False))

    # print(results)
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

def play_match():
    global initial_deck, num_simulations, bankroll
    while len(initial_deck) > 16:
        expected_value, variance = monte_carlo_blackjack(initial_deck, num_simulations)
        if expected_value > 0:
            bet_size = bankroll * (expected_value / variance)
        else:
            bet_size = 0

        result = simulate_hand(initial_deck, remove_from_deck=True)
        print(len(initial_deck))
        print(initial_deck, result, expected_value)
        bankroll += bet_size * result
        print(bankroll)

# Define parameters
# epsilon = 0.01 -> 115377
# epsilon = 0.1 -> 1153
num_simulations = 115377
num_hands = 100
initial_deck = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11] * 4 * 4
bankroll = 100_000

# Run simulation and print results
avg_ev = 0
avg_var = 0
max_ev = -1
min_ev = float('inf')
'''for _ in range(num_hands):
    expected_value, variance = monte_carlo_blackjack(initial_deck, num_simulations)
    max_ev = max(max_ev, expected_value)
    min_ev = min(min_ev, expected_value)
    avg_ev += expected_value
    avg_var += variance
    print(f"ev: {expected_value}, var: {variance}")
    print(f"Expected Value of the Next Bet: {bankroll * expected_value / variance}")
    print()'''

'''print(f"Average ev over {num_hands} hands: {avg_ev / num_hands}")
print(f"Average var over {num_hands} hands: {avg_var / num_hands}")
print(f"Max ev: {max_ev}, Min ev: {min_ev}")'''

play_match()
