from collections import Counter

from .card import Card
from .constants import PokerHand, STANDARD_POKER_HANDS
from .poker_hand_lu_job import hand_desc_lu


def describe_poker_hand(h: list[Card], possible_outcomes: tuple[PokerHand, ...] = STANDARD_POKER_HANDS) -> PokerHand:
    """Accepts a list of Cards and returns a PokerHand (ex: PokerHand.STRAIGHT_FLUSH)"""
    rank_ints = [c.rank_int for c in h]
    rank_ctr = Counter([c.rank_int for c in h]).most_common()
    sorted_rank_set = sorted(set(rank_ints))

    is_flush = len({c.suit for c in h}) == 1
    is_straight = len(sorted_rank_set) == 5 and ((sorted_rank_set[-1] - sorted_rank_set[0] == 4) or (sorted_rank_set == [2, 3, 4, 5, 14]))

    if is_flush and is_straight:
        if PokerHand.ROYAL_FLUSH in possible_outcomes and sorted_rank_set[4] == 14 and sorted_rank_set[3] == 13:
            return PokerHand.ROYAL_FLUSH
        return PokerHand.STRAIGHT_FLUSH

    max_pair_cnt = rank_ctr[0][1] if len(rank_ctr) > 0 else 0
    second_max_pair_cnt = rank_ctr[1][1] if len(rank_ctr) > 1 else 0

    if max_pair_cnt == 4:
        return PokerHand.FOUR_OF_A_KIND

    if max_pair_cnt == 3 and second_max_pair_cnt == 2:
        return PokerHand.FULL_HOUSE

    if is_flush:
        return PokerHand.FLUSH

    if is_straight:
        return PokerHand.STRAIGHT

    if max_pair_cnt == 3 and second_max_pair_cnt != 2:
        return PokerHand.THREE_OF_A_KIND

    if max_pair_cnt == 2 and second_max_pair_cnt == 2:
        return PokerHand.TWO_PAIR

    if PokerHand.JACKS_OR_BETTER in possible_outcomes and max_pair_cnt == 2 and rank_ctr[0][0] >= 11:
        return PokerHand.JACKS_OR_BETTER

    if max_pair_cnt == 2 and second_max_pair_cnt == 1:
        return PokerHand.ONE_PAIR

    return PokerHand.HIGH_CARD


def describe_poker_hand_from_lu_job(cards: list[Card]) -> PokerHand | None:
    """Does not accept a possible_hands parm; assumes Jacks Or Better and Royal Flush are valid hands.
    Encodes list of Card into a sorted string key (ex. "22AJT") to look up the non-suit based hands.
    Returns the PokerHand if found or None if not."""
    encoded_key = ''.join(sorted([c.rank_str for c in cards]))
    hand_desc: PokerHand = hand_desc_lu.get(encoded_key)
    if hand_desc and hand_desc != PokerHand.STRAIGHT:
        return hand_desc
    if len({c.suit for c in cards}) == 1:
        if {c.rank_int for c in cards} == {10, 11, 12, 13, 14}:
            return PokerHand.ROYAL_FLUSH
        if hand_desc == PokerHand.STRAIGHT:
            return PokerHand.STRAIGHT_FLUSH
        return PokerHand.FLUSH
    if hand_desc == PokerHand.STRAIGHT:
        return PokerHand.STRAIGHT
    return None
