#! /usr/bin/env python3
import random


#  create a new deck of cards
def get_deck():
    # create lists and tuples
    deck = []
    ranks = {"A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"}
    suits = {"Diamonds", "Clubs", "Hearts", "Spades"}

    #  load the deck of cards
    for suit in suits:
        for rank in ranks:
            if rank == "A":
                card_value = 11
            elif rank == "J" or rank == "Q" or rank == "K":
                card_value = 10
            else:
                card_value = int(rank)

            card = [rank, suit, card_value]
            deck.append(card)
    return deck


#  shuffle the deck of cards
def shuffle(deck):
    random.shuffle(deck)


#  deal a card
def deal(deck):
    card = deck.pop()
    return card


#  get an empty hand
def get_empty_hand():
    hand = []
    return hand


#  add a card to the hand
def add_card(hand, card):
    hand.append(card)


# calculate hand point value
def calculate(hand):
    points = 0
    ace_count = 0

    for card in hand:
        if card[0] == "A":
            ace_count += 1
        points += card[2]

    if ace_count > 0 and points > 21:
        points = points - (ace_count * 10)

    if ace_count > 1 and points <= 11:
        points += 10

    return points


#  display a card
def display_card(card):
    card_name, card_suit, _ = card

    if card_suit == 'Hearts':
        suit = '♥'
    elif card_suit == 'Diamonds':
        suit = '♦'
    elif card_suit == 'Clubs':
        suit = '♣'
    elif card_suit == 'Spades':
        suit = '♠'
    else:
        raise ValueError('Invalid card suit: {}'.format(card_suit))

    if card_name == '10':  # 10 is the only two-digit number, adjust spacing
        card_display = '''
            ┌─────────┐
            │{}{}      │
            │         │
            │     {}   │
            │         │
            │      {}{}│
            └─────────┘'''.format(card_name, suit, suit, card_name, suit)
    else:
        card_display = '''
            ┌─────────┐
            │{}{}       │
            │         │
            │    {}    │
            │         │
            │       {}{}│
            └─────────┘'''.format(card_name, suit, suit, card_name, suit)

    print(card_display)


def remove_cards(deck, cards):
    for card in cards:
        if card in deck:
            deck.remove(card)


# Other functions...

#  main for testing
def main():
    print("Card Tester")

    deck = get_deck()
    shuffle(deck)

    for i in range(5):
        display_card(deck[i])  # Removed the print statement here
    print()

    hand = get_empty_hand()
    add_card(hand, deal(deck))
    add_card(hand, deal(deck))
    add_card(hand, deal(deck))

    print("HAND")
    for card in hand:
        display_card(card)  # Removed the print statement here
    print("Points", calculate(hand))


if __name__ == "__main__":
    main()
