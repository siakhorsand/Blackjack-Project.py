#! /usr/bin/env python3


import deck
import db
import locale as lc

#  set locale
result = lc.setlocale(lc.LC_ALL, "")
if result[0] == "C":
    lc.setlocale(lc.LC_ALL, "en_us")


def display_header():
    # Welcome
    print("Welcome to BLACKJACK!")
    print("Blackjack payout is 3:2")
    print("Enter 'x' for bet to exit")


def get_starting_balance():
    # Get the starting amount input
    try:
        balance = db.read_money()
    except FileNotFoundError:
        print("Data file is missing, resetting the game.")
        balance = 1000
        db.write_money(balance)

    #  if amount <5 reset to 1000
    if 5 > balance:
        print("You don't have enough to play, resetting back to 10000")
        balance = 1000
        db.write_money(balance)
    print("Money", lc.currency(balance, grouping=True))
    print()
    return balance


def get_bet_amount(balance):
    # get the bet and make sure it's not more than player money
    while True:
        # bet input
        bet = input("Bet amount:       ")
        if bet == "x":
            return bet

        try:
            bet = float(bet)
        except ValueError:
            print("Invalid Entry, please try again.")
            print()
            continue

        if bet < 5:
            print("The minimum bet is 5. Please try again.")
        elif bet > 2500:
            print("The maximum bet is 1000. Please try again.")
        elif bet > balance:
            print("You don't have enough to cover that bet. Please try again.")
        else:
            print()
            return bet


def play_player_hand(deck_of_cards, hand):
    while True:
        player_choice = input("HIT OR STAND?   (h/s)")
        print()

        if player_choice.lower() == "h":
            deck.add_card(hand, deck.deal(deck_of_cards))
            display_cards(hand, "YOUR CARDS: ")
            if deck.calculate(hand) > 21:
                break
        elif player_choice.lower() == "s":
            break
        else:
            print("not a valid choice, please try again.")

    return hand


#  display cards in a hand
# def display_cards(hand, title):
#    print(title.upper())
#   for card in hand:
#       print(deck.display_card(card))
#  print()


def display_outcome(player_points, player_hand, dealer_points, dealer_hand, bet, balance):
    if player_points > 21:
        print("SORRY, YOU BUSTED. YOU LOSE")
        balance -= bet
    elif player_points == 21 and len(player_hand) == 2:
        if dealer_points == 21 and len(dealer_hand) == 2:
            print("BAD LUCK, YOU BOTH GOT BLACKJACK! NOBODY WINS.(⊙︿⊙)")
        else:
            print("BLACKJACK! YOU WIN")
            balance += bet * 1.5
    elif dealer_points == 21 and len(dealer_hand) == 2:
        print("THE DEALER GOT BLACKJACK, YOU LOSE. (ᵟຶ︵ ᵟຶ)")
        balance -= bet
    elif player_points == 21 and len(player_hand) == 2 and player_points > dealer_points:
        print("YOU GOT BLACKJACK! YOU WIN!!! (◠﹏◠)")
        balance -= bet
    elif dealer_points > 21:
        print("THE DEALER BUSTED. YOU WON!!!! (◠﹏◠)")
        balance += bet
    elif player_points > dealer_points:
        print("YOU WON! (◠﹏◠)")
        balance += bet
    elif player_points < dealer_points:
        print("YOU LOSE. (ᵟຶ︵ ᵟຶ)")
        balance += bet * 1.5
    else:
        print("YOU AND THE DEALER PUSHED.")

        # Calculate and display the odds
        total_outcomes = 0
        favorable_outcomes = 0

        # Simulate remaining possible outcomes
        deck_of_cards = deck.get_deck()
        deck.remove_cards(deck_of_cards, player_hand + dealer_hand)  # Remove player and dealer cards from deck

        remaining_cards = len(deck_of_cards)
        for i in range(remaining_cards):
            dealer_possible_hand = dealer_hand.copy()
            deck.add_card(dealer_possible_hand, deck_of_cards[i])

            # Simulate dealer's play
            while deck.calculate(dealer_possible_hand) < 17:
                deck.add_card(dealer_possible_hand, deck.deal(deck_of_cards))

            dealer_possible_points = deck.calculate(dealer_possible_hand)

            # Compare player and dealer points
            if player_points > dealer_possible_points:
                favorable_outcomes += 1
            total_outcomes += 1

        # Calculate and display the odds
        if total_outcomes > 0:
            win_percentage = (favorable_outcomes / total_outcomes) * 100
            print("ODDS OF WINNING: {:.2f}%".format(win_percentage))
        else:
            print("ODDS OF WINNING: N/A")
    return balance


def display_cards(hand, title):
    print(title.upper())
    for card in hand:
        deck.display_card(card)  # no need to print here, as display_card now includes a print statement
    print()


def main():
    display_header()
    balance: float = get_starting_balance()
    # Loop
    while True:
        bet = get_bet_amount(balance)
        if bet == "x":
            break

        bet = float(bet)

        deck_of_cards = deck.get_deck()
        deck.shuffle(deck_of_cards)

        player_hand = deck.get_empty_hand()
        dealer_hand = deck.get_empty_hand()

        deck.add_card(player_hand, deck.deal(deck_of_cards))
        deck.add_card(dealer_hand, deck.deal(deck_of_cards))
        deck.add_card(player_hand, deck.deal(deck_of_cards))

        display_cards(dealer_hand, "DEALER'S SHOW CARD: ")
        display_cards(player_hand, "YOUR CARDS: ")

        #  play player hand
        player_hand = play_player_hand(deck_of_cards, player_hand)

        deck.add_card(dealer_hand, deck.deal(deck_of_cards))
        if deck.calculate(player_hand) <= 21:
            while deck.calculate(dealer_hand) < 17:
                deck.add_card(dealer_hand, deck.deal(deck_of_cards))

        display_cards(dealer_hand, "DEALER'S CARDS: ")

        # Display the points
        player_points = deck.calculate(player_hand)
        dealer_points = deck.calculate(dealer_hand)
        print("YOUR POINTS:\t", player_points)
        print("DEALER POINTS:\t", dealer_points)
        print()

        balance = display_outcome(player_points, player_hand, dealer_points, dealer_hand, bet, balance)

        # Print
        print("Money", lc.currency(round(balance, 2), grouping=True))
        print()

        db.write_money(balance)

        if balance < 5:
            print("YOU ARE OUT OF MONEY. ")
            break

        play_again = input("PLAY AGAIN? (y/n)")

        if play_again.lower() != "y":
            print("COME AGAIN SOON!")
            break

    print("BYE")


main()
