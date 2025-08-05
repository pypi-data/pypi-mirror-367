import sys
if 'src' not in sys.path:
    sys.path.insert(0, 'src')

from proloquor_model.games.cards import Rank, Suit, Card, Deck, PokerDeck

def test_card():
    card = Card(Rank.NINE, Suit.DIAMONDS)

    assert str(card) == "NINE of DIAMONDS"
    
def test_PokerDeck():
    poker_deck = PokerDeck().shuffle()

    assert len(poker_deck) == 52

def test_howMany():
    deck = Deck()
    deck.add(Card(Rank.EIGHT, Suit.HEARTS))
    deck.add(Card(Rank.EIGHT, Suit.HEARTS))
    deck.add(Card(Rank.KING, Suit.SPADES))
    deck.add(Card(Rank.SEVEN, Suit.CLUBS))
    deck.add(Card(Rank.FIVE, Suit.CLUBS))
    deck.add(Card(Rank.KING, Suit.DIAMONDS))

    assert deck.howMany() == 6
    assert deck.howMany(Rank.TEN) == 0
    assert deck.howMany(Rank.SEVEN) == 1
    assert deck.howMany(Rank.KING) == 2
    assert deck.howMany(suit = Suit.DIAMONDS) == 1
    assert deck.howMany(suit = Suit.CLUBS) == 2
    assert deck.howMany(rank = Rank.FIVE, suit = Suit.SPADES) == 0
    assert deck.howMany(rank = Rank.FIVE, suit = Suit.CLUBS) == 1
    assert deck.howMany(rank = Rank.EIGHT, suit = Suit.HEARTS) == 2
    