from dataclasses import dataclass, field
import random
from typing import TypeVar, Generic
from enum import Enum, auto

from .card import Card, deck_unshuffled


class PileType(Enum):
    DECK = auto()
    DISCARD = auto()
    STAGED = auto()
    HAND = auto()


@dataclass
class PileProps:
    """Dataclass that evaluates aspects of a list of cards. Can be part of a Pile or instantiated independently.
    Attributes: cards: list[Card] & the_suit: str (helpful if used in some type of trump game)
    """
    cards: list[Card]
    the_suit: str = None

    @property
    def suits(self) -> set:
        """Return a set of suits contains in cards"""
        return {c.suit for c in self.cards}

    @property
    def suit_cards(self) -> list[Card]:
        """Returns cards of a self.the_suit ordered by rank_int desc"""
        return sorted([c for c in self.cards if c.suit == self.the_suit], key=lambda x: x.rank_int, reverse=True)

    @property
    def non_suit_cards(self) -> list[Card]:
        return [c for c in self.cards if c.suit != self.the_suit]

    @property
    def suit_length(self) -> int:
        return len(self.suit_cards)

    @property
    def suit_rank_ints(self) -> list[int]:
        return sorted([c.rank_int for c in self.suit_cards], reverse=True)

    def suit_length_by_ranks(self, ranks: list[int]) -> int:
        return len([c for c in self.suit_cards if c.rank_int in ranks])

    def suit_has_rank(self, rank: int) -> bool:
        """Accepts a rank (e.g. 11 for Jack), returns bool if card exists for self.the_suit"""
        return rank in self.suit_rank_ints

    def suit_has_any_ranks(self, ranks: list[int]) -> bool:
        return any(c in self.suit_rank_ints for c in ranks)

    @property
    def suit_highest_card(self) -> Card | None:
        return self.suit_cards[0] if self.suit_length else None

    @property
    def suit_second_highest_card(self) -> Card | None:
        return self.suit_cards[1] if self.suit_length >= 2 else None

    def has_a_non_suit_rank(self, rank: int) -> bool:
        return rank in [c.rank_int for c in self.non_suit_cards]


def create_cards_from_rank_suits(deck: "Deck", rank_suits: str) -> list[Card] | list[None]:
    """Accepts a deck & string of rank_suits, such as 'Ah Kh As Tc' or 'Ah'.
    Error thrown if rank_suits aren't unique or rank_suit doesn't exist in a standard deck.
    If nothing is provided, return an empty list.
    Note: the deck is important because properties may be applied to the cards in that deck, so we need to ACCESS cards,
    not CREATE them here"""
    if not rank_suits:
        return []
    deck_rank_suits = {c.rank_suit for c in deck.cards}
    rank_suits = rank_suits.split(' ')
    if len(set(rank_suits)) != len(rank_suits):
        raise ValueError("You have a duplicate card")
    cards = []
    for rank_suit in rank_suits:
        if rank_suit not in deck_rank_suits:
            raise ValueError(f"'{rank_suit}' not in the deck.")
        cards.append(next(c for c in deck.cards if c.rank_suit == rank_suit))
    return cards



T = TypeVar("T", bound=Card)


@dataclass
class Pile(Generic[T]):
    """A collection that accepts a list of Cards & can: pop, push, shuffle, peek, remove, clear"""
    cards: list[T] = field(default_factory=list)
    start_shuffled: bool = False

    def __post_init__(self):
        if not all(isinstance(card, Card) for card in self.cards):
            raise TypeError("All elements in 'cards' must be instances of Card.")
        if self.start_shuffled and self.cards:
            self.shuffle()

    @classmethod
    def create_from_rank_suits(cls, deck, rank_suits: str):
        """Alternate constructor from a string of rank_suits, such as 'Ah Kh As Tc' or 'Ah'.
        Error thrown if Rank_suits aren't unique or rank_suit doesn't exist in a standard deck.
        If nothing is provided, return an empty list."""
        cards = create_cards_from_rank_suits(deck, rank_suits)
        return cls(cards)

    def __iter__(self):
        return iter(self.cards)

    def __len__(self) -> int:
        return len(self.cards) if self.cards else 0

    def __getitem__(self, rank_suits: str) -> Card | list[Card] | None:
        """This is helpful for tests where the test needs a card or list of cards.
        Example call would be: deck['Kh'] or deck['Ah Kh'].
        deck['Kh'] returns Card; deck['Ah Kh'] returns list[Card]; deck[''] returns None; deck['Xa'] throws."""
        rank_suit_list: list[str] = rank_suits.split(' ')
        if len(set(rank_suit_list)) != len(rank_suit_list):
            raise ValueError('Your cards must be unique')
        if rank_suits == '' or len(rank_suit_list) == 0:
            return None
        if len(rank_suit_list) == 1:
            return next((c for c in self.cards if c.rank_suit == rank_suit_list[0]), ValueError(f"Card not in the deck."))
        return [c for c in self.cards for rs in rank_suit_list if c.rank_suit == rs]

    @property
    def card_cnt(self) -> int:
        return len(self.cards) if self.cards else 0

    @property
    def is_empty(self) -> bool:
        return len(self.cards) == 0

    def to_rank_suits(self) -> str:
        return ' '.join([c.rank_suit for c in self])

    def shuffle(self):
        random.shuffle(self.cards)

    def push(self, card: T):
        if not isinstance(card, Card):
            raise TypeError("Only Card instances can be added to the pile.")
        self.cards.append(card)

    def remove(self, item: T):
        if item not in self.cards:
            raise ValueError(f"{item} not found")
        self.cards.remove(item)

    def pop(self) -> T | None:
        return self.cards.pop() if self.cards else None

    def clear(self) -> None:
        self.cards.clear()

    def peek(self) -> T | None:
        return self.cards[-1] if self.cards else None

    def reveal(self) -> list[T]:
        return self.cards

    def sort_by_rank(self, descending: bool = False) -> None:
        self.cards.sort(key=lambda card: card.rank_int, reverse=descending)

    def sort_by_suit(self, descending: bool = False) -> None:
        self.cards.sort(key=lambda card: card.suit, reverse=descending)


@dataclass
class Deck(Pile[Card]):
    """A standard 52 card playing deck"""
    cards: list[Card] = field(init=False)

    def __post_init__(self):
        self.cards = [Card(idx, *c) for idx, c in enumerate(deck_unshuffled)]
        super().__post_init__()
