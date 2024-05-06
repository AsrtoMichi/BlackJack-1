from random import shuffle
from typing import Literal, Union
ranks = ('A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K')
suits = ('Spades', 'Hearts', 'Diamonds', 'Clubs')
data = []



class Card:

    '''

    Creating the 'Card' class

    this is used simply to evaluate information about a singular card instead of an entire deck

    '''

    def __init__(self, rank: tuple , suit: tuple) -> str:
        self.rank = rank
        self.suit = suit


    def card_value(self) -> int:

        '''

        Evaluate the value of a card

        in blackjack if cards are any of the royals
        they are just a ten

        and if they are an Ace, they are either 1 or 11
        depending on if that would cause you to bust.
        which is checked for in the hand class

        '''

        # if the rank is is a king, queen, or jack, return 10 as the value of the card.
        if self.rank in ['J', 'Q', 'K']:
            return 10
        # if the rank is an ace return 1 and 11. This will later
        # let us choose whether we want the ace to be a one or eleven
        if self.rank == 'A':
            return 1, 11
        # if it's nothing special just return the number.
        return int(self.rank)


    def __str__(self):
        return f"{self.rank}-{self.suit}"


class Deck:

    '''

    Creating our deck class

    mostly, this will be used for drawing cards,
    setting up a deck so we don't just draw cards at random
    resulting in us having 2 aces of spades, which is illegal in blackjack.

    '''

    def __init__(self):
        # Create a deck, suit first then rank.
        # This makes the deck follow what a brand new pack of cards looks like.
        self.generate_deck() 

       
    def generate_deck(self):
        self.cards = [Card(rank, suit) for suit in suits for rank in ranks]
        shuffle(self.cards)


    def deal_card(self) -> classmethod:

        '''

        simply deals a card by popping one
        from the first spot in the deck array

        '''

        # Check if there are no cards left in the deck
        if not self.cards:
            self.generate_deck()
        # As long as there are cards left in the deck, pop one from the top of the deck out,
        # return the drawn card so it can be added to the hand
        return self.cards.pop(0)


class Hand:

    '''

    creating the 'Hand' class

    this is used simply to store each players hand
    give the value of the two hands
    show if either hand is soft
    and also to make it easier to draw cards

    '''


    def __init__(self):
        # start with two cards in hand.
        self.cards = [(Game.deck.deal_card()), (Game.deck.deal_card())]
        self.soft = any(c.rank == 'A' for c in self.cards)


    def value(self) -> int:

        '''

        The method 'Value', is used to check the value
        of the players hand, this will allow us to check
        to see if the player has busted, has an ace, or
        just has a regular old hand

        '''

        total = 0
        ace_count = 0

        # Calculate the total value of the hand
        for card in self.cards:
            if card.rank == 'A':
                ace_count += 1
            else:
                total += card.card_value()
        # Determine the value of aces

        for _ in range(ace_count):
            if total + 11 <= 21:
                total += 11
                self.soft = True
            else:
                total += 1

        return total


    def reset(self):

        ''' For resetting the hand between games '''

        self.cards.clear()
        self.draw()
        self.draw()


    def draw(self):

        '''

        draw method, simply exists to make it easier
        for a player to draw cards

        '''

        self.cards.append(Game.deck.deal_card())


    def __str__(self):
        return f"{', '.join(map(str, self.cards))}"



class Player:

    '''

    creating the 'Player' class

    this will have a multitude of select-able values
    a strategy, a name, and a budget
    this will all be managed by the player throughout the game
    whether it's a bot or a person.

    '''

    def __init__(self, budget: int, strategy: str, name: str):
        self.name = name
        self.hand = Hand()
        self.state = 'play'
        self.strategy = strategy
        self.bid_amount = 0
        self.starting_bid = 10
        self.current_simulated_bid = self.starting_bid
        self.budget = budget
        self.broke = False


    # player action
    def hit(self):

        '''

        Makes the player draw a card, and makes sure the player state
        is set to 'play' so that the player can keep playing

        '''

        self.hand.draw()

    def stay(self):

        '''

        Changes the player state to 'stay', which changes anything
        that runs based on the 'play' state and causes
        it to stop working.

        '''

        self.state = 'stay'


    def bid(self, amount = 0) ->int :

        '''

        Get a bid from the player if the player is actually a player,
        otherwise automate the bid

        '''

        if self.strategy is None :
            if self.check_broke():
                print('You are out of money and cannot bid anymore')
            else:
                self.bid_amount = int(input('How much?\n'))
                while self.bid_amount > self.budget:
                    self.bid_amount = int(input('How much?\n'))
                    print(f'You don\'t have that much. You have: ${self.budget}')
        else:
            self.bid_amount = amount

        self.budget -= amount
        return self.bid_amount


    #status ceck point
    def check_bust(self) -> bool:

        '''

        Check if the player busted by seeing if the hand
        value is above 21

        '''

        if self.hand.value() > 21:
            self.state = 'bust'
            return True
        return False


    def check_broke(self) -> bool:

        ''' check if the player is broke '''

        if self.budget < 1:
            self.state = 'broke'
            return True
        return False


    # strategies
    def strategy_player(self, strdealer_up_card: classmethod):

        '''

        A random very basic strategy, generated by chatGPT
        and implemented, by no means is it great. but
        it gets the job done for now.

        '''
        dealer_up_card = strdealer_up_card
        player_hand_value = self.hand.value()
        
        if self.strategy == "strategy_one":
            # Define the basic strategy decisions based
            # on the player's hand value and the dealer's up card
            if self.hand.soft:
                if player_hand_value <= 17:
                    self.hit()
                elif player_hand_value == 18 and dealer_up_card.rank in [9, 10, 'J', 'Q', 'K', 'A']:
                    self.hit()
                else:
                    self.stay()
            else:
                if player_hand_value <= 11:
                    self.hit()
                elif player_hand_value == 12: 
                    if dealer_up_card.rank in [2, 3, 7, 8, 9, 10, 'J', 'Q', 'K', 'A']:
                        self.hit()
                    else:
                        self.stay()
                elif 13 <= player_hand_value <= 16:
                    if dealer_up_card.rank in [2, 3, 4, 5, 6]:
                        self.stay()
                    else:
                        self.hit()
                else:
                    self.stay()


    def __str__(self):
        return f"Name: {str(self.name)}; Budget: {str(self.budget)};\nHand: {str(self.hand)};\nHand Value: {str(self.hand.value())}\n"



class Dealer(Player):

    '''

    A dealer is another player where
    his strategy is automatic

    '''

    # initialize the dealer as a player
    def __init__(self):
        super().__init__(float('inf'), 'dealer', 'Dealer')
        self.up_card = self.hand.cards[0]

    def dealer_strategy(self):

        '''

        the dealers strategy is always:
        hit below 17 and on soft 17
        stay on hard 17 or above 17

        '''

        if self.hand.value() < 17 or (
            self.hand.value() == 17 and self.hand.soft):
            self.hit()
        else:
            self.stay()

    def __str__(self):
        return f"Name: {self.name}; up_card: {self.up_card}"



class Game:

    '''

    Create the 'Game' class

    This will be used to create and run the game as well as
    log it within a variable which we have set to 'data'


    '''

    game_count = 0
    deck = Deck()

    def __init__(self,  budget: int =100, strategy: Union[None, Literal['strategy_one']] = None , name: str ='Player'):

        self.dealer = Dealer()
        self.player = Player(budget, strategy, name)
        self.pot = 0
        self.simulated = False
        Game.game_count += 1


    def log_game(self):

        '''

        as mentioned above,
        the game class is in charge
        of logging the game.
        which is what this method does

        '''

        data.append((Game.game_count, self.player.budget))


    def player_turn(self):

        ''' player's turn function '''

        if self.player.strategy is None:

            self.player.budget -= 10
            self.pot += 10
            option = ('1', 'HIT', '2', 'STAY','3', 'BID')
            question = "What would you like to do? \n1) Hit \n2) Stay \n3) Bid\n"
            player_move = input(question).upper()
            while player_move not in option:
                print('Not a valid move')
                player_move = input(question).upper()
            
            # execute that move
            if player_move in option[:2]:
                self.player.hit()
            elif player_move in option[2:4]:
                self.player.stay()
            elif player_move in option[4:]:
                self.pot += self.player.bid()

            print(f"Hand: {self.player.hand}")
            print(f"Hand Value: {self.player.hand.value()}")
            print()

            # Check if the player busted
            if self.player.check_bust():
                print('Sorry, you busted.')
                return True


        # get the move that the player wants to do
        else:
            self.player.strategy_player(self.dealer.up_card)
            self.player.check_bust()

            # in this version we are using the 2 - 1 - 2 bidding strategy
            # which increments by 1 every win, then resets to 1 at a loss

            self.pot += self.player.bid(self.player.current_simulated_bid)
        
        
    def check_win(self) -> bool:

        '''

        Check if the player has won the round
        this will be if the hand value is higher
        than the dealers
        and the hand has not busted
        or if the dealer has busted
        and the player hasn't

        '''
        
        # Check bust for both
        self.dealer.check_bust()
        self.player.check_bust()

        player_value = self.player.hand.value()
        dealer_value = self.dealer.hand.value()
    
        if (player_value > dealer_value and self.player.state != 'bust') or self.dealer.state == 'bust':
            if self.player.state == 'bust' and self.dealer.state == 'bust':
                return False
            else:
                self.player.budget += self.pot
                return True
        else:
            return False


    def change_bid(self):

        '''

        change the amount of the
        simulated bid depending on win/loss

        '''

        if self.check_win():
            self.player.budget += self.pot
            self.player.current_simulated_bid += 2
        else:
            self.player.current_simulated_bid = self.player.starting_bid


    def run(self):

        '''

        this function actually runs the game,
        letting the player make their moves first
        then the dealer making theirs.

        '''

        self.pot = 0

        if self.player.strategy is None:
            print('Buy in is 10 bucks.')
            print(self.dealer)
            print()
            print(self.player)

        # while the player and is not staying, busted or out of budget
        while 'play' in (self.player.state, self.dealer.state):
            if self.player_turn():
                break
            self.dealer.dealer_strategy()
           
        # add the dealers bet to the pot, which will always be equal to the pot.
        self.pot += self.dealer.bid(self.pot)

        # Check win and lost
        if self.player.strategy is None:
            if self.check_win():
                print("You win!")
            else: 
                print("You lose.")
        else: 
            self.change_bid()
            

        #self.log_game()
        #print(data[-1])
        
if __name__ == "__main__":
    game = Game(strategy= None)
    game.run()
