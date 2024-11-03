from card_elements import Card, Deck, Pile
from codecarbon import EmissionsTracker
import random

with EmissionsTracker() as tracker:

    class Game:
        values = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
        suits = {u'\u2660': "black", u'\u2665': "red", u'\u2663': "black", u'\u2666': "red"}
        numPlayPiles = 7

        def __init__(self):
            self.value_ranks = {value: index for index, value in enumerate(self.values)}
            
            # Shuffle deck at initialization for randomness
            self.deck = Deck(self.values, self.suits)
            random.shuffle(self.deck.cards)
            
            self.playPiles = [self._initialize_pile(i) for i in range(self.numPlayPiles)]
            self.blockPiles = {suit: Pile() for suit in self.suits}
            self.deck.cards[0].flip()

        def _initialize_pile(self, count):
            pile = Pile()
            for _ in range(count + 1):
                pile.addCard(self.deck.takeFirstCard(flip=False))
            pile.flipFirstCard()
            return pile

        def checkCardOrder(self, higherCard, lowerCard):
            """Check if two cards follow order rules."""
            return (
                self.suits[higherCard.suit] != self.suits[lowerCard.suit] and
                self.value_ranks[higherCard.value] - 1 == self.value_ranks[lowerCard.value]
            )

        def checkIfCompleted(self):
            """Check if the game is complete."""
            return (
                len(self.deck.cards) == 0 and
                all(len(pile.cards) == 0 for pile in self.playPiles) and
                all(len(pile.cards) == 13 for pile in self.blockPiles.values())
            )

        def addToBlock(self, card):
            """Attempt to add a card to its block pile."""
            if not card:
                return False
            block_pile = self.blockPiles[card.suit]
            top_card_rank = self.value_ranks[block_pile.cards[0].value] if block_pile.cards else -1
            if top_card_rank + 1 == self.value_ranks[card.value] or card.value == "A":
                block_pile.cards.insert(0, card)
                return True
            return False

        def takeTurn(self):
            """Execute a turn's actions efficiently."""
            top_card = self.deck.getFirstCard()

            # Flip any unflipped cards at the ends of play piles
            for pile in self.playPiles:
                if pile.cards and not pile.cards[0].flipped:
                    pile.cards[0].flip()

            # Check play piles and add cards to block piles if possible
            for pile in self.playPiles:
                if pile.cards and self.addToBlock(pile.cards[0]):
                    pile.cards.pop(0)
                    return True

            # Add top card of deck to block pile if it fits
            if top_card and self.addToBlock(top_card):
                self.deck.takeFirstCard()
                return True

            # Move Kings to empty piles if possible
            empty_pile = next((pile for pile in self.playPiles if not pile.cards), None)
            if empty_pile:
                for pile in self.playPiles:
                    if pile.cards and pile.cards[0].value == "K":
                        empty_pile.addCard(pile.cards.pop(0))
                        return True
                if top_card and top_card.value == "K":
                    empty_pile.addCard(self.deck.takeFirstCard())
                    return True

            # Add drawn card to play piles if order allows
            if top_card:
                for pile in self.playPiles:
                    if pile.cards and self.checkCardOrder(pile.cards[0], top_card):
                        pile.addCard(self.deck.takeFirstCard())
                        return True

            return False

        def simulate(self):
            """Run the game simulation until no moves are possible."""
            seen_cards = set()
            while True:
                if not self.takeTurn():
                    top_card = self.deck.getFirstCard()
                    if not self.deck.cards or top_card in seen_cards:
                        break
                    self.deck.drawCard()
                    seen_cards.add(top_card)

    def main():
        game = Game()
        game.simulate()
        if game.checkIfCompleted():
            print("Congrats! You won!")
        else:
            print("Sorry, you did not win")

    main()



