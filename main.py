import numpy as np
import matplotlib.pyplot as plt

card_count = 0
# How much to bet based on the true count
bet_percentage_bankroll = {
    -3: 0.005,
    -2: 0.01,
    -1: 0.02, 
    0: 0.03,
    1: 0.05,
    2: 0.1,
    3: 0.2,
    4: 0.3,
    5: 0.4,
}

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
# Gets card counting value based on HI-LO strategy
def get_card_value(card):
    if card < 7:
        return 1
    if card >= 10:
        return -1
    return 0

def get_nr_decks(deck):
    return np.ceil(len(deck) / 52)

def get_bet_percentage_bankroll(card_count, deck):
    global bet_percentage_bankroll
    #true_count = card_count // get_nr_decks(deck)
    true_count = card_count

    if (true_count < -3):
        return bet_percentage_bankroll[-3]
    if (true_count > 5):
        return bet_percentage_bankroll[5]
    return bet_percentage_bankroll[true_count]

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
        global card_count
        while hand_value(dealer_hand) < 17:
            dealt_card = deck.pop(0)
            dealer_hand.append(dealt_card)
            card_count += get_card_value(dealer_hand[-1])
        return hand_value(dealer_hand)

    global card_count
    # Converting to list if needed
    if isinstance(deck, np.ndarray):
        deck = deck.tolist()

    # Deal hands
    player_hand = [deck.pop(0), deck.pop(0)]
    dealer_hand = [deck.pop(0), deck.pop(0)]
    card_count = get_card_value(player_hand[0]) + get_card_value(player_hand[1]) + get_card_value(dealer_hand[0]) + get_card_value(dealer_hand[1])


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
        card_count += get_card_value(player_hand[-1])
        dealt_card = deck.pop(0)
        player_hand.append(dealt_card)
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



# Returns the results of each hand in the match
def simulate_full_match_count(deck, bankroll):
    global card_count
    card_count = 0

    bankrolls = []
    # Keep simulating hands until there is not enough cards left in the deck
    while len(deck) > 16:
        bankroll += get_bet_percentage_bankroll(card_count, deck) * simulate_hand(deck)
    
        bankrolls.append(bankroll)

    return bankrolls

# Function for Monte Carlo Simulation
def monte_carlo_blackjack(deck, num_simulations=1000):
    # max count of cards for a hand (1 player):
    # player: 4 * 1 + 4 * 2 + 3 * 3 | dealer: 3 + 4 * 4   ->   16

    # create num_simulations copies of deck (simulate only 16 cards per deck)
    decks = np.random.choice(deck, size=(num_simulations, 16), replace=True)

    results = list()
    for curr_deck in decks:
        results.append(simulate_hand(curr_deck))

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
    # print(f"Wins: {wins}, Losses: {losses}, BlackJacks: {blackjack}")

    # Calculate expected value
    ev = np.sum(results) / num_simulations
    var = (
            (p_win * (1 - ev) ** 2) +
            (p_blackjack * (1.5 - ev) ** 2) +
            (p_loss * (-1 - ev) ** 2) +
            (p_tie * (0 - ev) ** 2)
    )
    return ev, var

def play_match(deck, bankroll, num_simulations):
    bankrolls = []
    while len(deck) > 16:
        expected_value, variance = monte_carlo_blackjack(deck, num_simulations)
        if expected_value > 0:
            bet_size = bankroll * (expected_value / variance)
        else:
            bet_size = 0

        result = simulate_hand(deck)
        # print(len(deck))
        # print(deck, result, expected_value)
        bankroll += bet_size * result
        bankrolls.append(bankroll)

    return bankrolls


def plot_by_bank_results(monte_carlo_results, counting_results):
    # Graph the money afther the matches
    plt.plot(counting_results, label="Counting", color="blue", linestyle="-")
    plt.plot(monte_carlo_results, label="Monte Carlo", color="green", linestyle="-")

    plt.title("Money comparison")
    plt.xlabel("Entries")
    plt.ylabel("Money")
    plt.legend()
    plt.grid()

    plt.show()


def plot_by_nr_simulations():
    num_simulations =  np.linspace(10_000, 115_777, 1000).astype(int)
    expected_values = []
    variances = []

    for num_sim in num_simulations:
        expected_value, variance = monte_carlo_blackjack(initial_deck, num_sim)
        expected_values.append(expected_value)
        variances.append(variance)

    plt.plot(num_simulations, expected_values, label='Expected Value')

    plt.xlabel('Number of Simulations')
    plt.ylabel('Player edge')

    plt.axhline(-0.025, color='r', linestyle='-', label='Theoretical edge')
    plt.title('Expected Value by Number of Simulations')

    plt.legend()
    plt.savefig('assets/expected_value_by_sim.png')
    plt.show()

# Define parameters
# epsilon = 0.01 -> 115377
# epsilon = 0.1 -> 1153
num_simulations = 115377
num_hands = 100

bankroll_default = 100_000
bankroll_count = 100_000
bet_sum_count = 1000

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

counting_results = []
monte_carlo_results = []

nr_matches = 5
for i in range(nr_matches):
    print(f"Playing match: [{i}]")
    initial_deck = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11] * 4 * 4

    np.random.shuffle(initial_deck)
    initial_deck_cp = initial_deck.copy()

    print("Playing match using Monte Carlo simulation...")
    bankrolls_default = play_match(initial_deck, bankroll_default, num_simulations)
    monte_carlo_results.extend(bankrolls_default)

    print("Playing match using High-Low Counting...")
    bankrolls_count = simulate_full_match_count(initial_deck_cp, bankroll_count)
    counting_results.extend(bankrolls_count)

    print("Bankrolls defaults:", bankroll_default)
    print("Bankrolls count:", bankroll_count)
    print()

plot_by_bank_results(monte_carlo_results, counting_results)
plot_by_nr_simulations()
