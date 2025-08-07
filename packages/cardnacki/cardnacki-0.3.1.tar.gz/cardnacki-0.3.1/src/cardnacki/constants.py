from enum import StrEnum

class PokerHand(StrEnum):
    ROYAL_FLUSH = 'Royal Flush'
    STRAIGHT_FLUSH = 'Straight Flush',
    FOUR_OF_A_KIND = 'Four of a Kind'
    FULL_HOUSE = 'Full House'
    FLUSH = 'Flush'
    STRAIGHT = 'Straight'
    THREE_OF_A_KIND = 'Three of a Kind'
    TWO_PAIR = 'Two Pair'
    JACKS_OR_BETTER = 'Jacks or Better'
    ONE_PAIR = 'One Pair'
    HIGH_CARD = 'High Card'


STANDARD_POKER_HANDS = (PokerHand.STRAIGHT_FLUSH, PokerHand.FOUR_OF_A_KIND, PokerHand.FULL_HOUSE, PokerHand.FLUSH,
                        PokerHand.STRAIGHT, PokerHand.THREE_OF_A_KIND, PokerHand.TWO_PAIR, PokerHand.ONE_PAIR,
                        PokerHand.HIGH_CARD)

VIDEO_POKER_HANDS = (PokerHand.ROYAL_FLUSH, PokerHand.STRAIGHT_FLUSH, PokerHand.FOUR_OF_A_KIND, PokerHand.FULL_HOUSE,
                     PokerHand.FLUSH, PokerHand.STRAIGHT, PokerHand.THREE_OF_A_KIND, PokerHand.TWO_PAIR,
                     PokerHand.JACKS_OR_BETTER)
