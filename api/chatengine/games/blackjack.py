from .chatgame import ChatGame
from asgiref.sync import sync_to_async
import random
import datetime

class Blackjack(ChatGame):

    STATE_NOT_STARTED = "not_started"
    STATE_WAITING_FOR_BETS = "waiting_for_bets"
    STETE_WAITING_FOR_PLAYERS = "waiting_for_players"
    STATE_DEAL_HANDS = "deal_hands"
    STATE_WAITING_FOR_MOVES = "waiting_for_moves"
    
    def __init__(self,chatbot):
        super().__init__(chatbot)
        self.game_state = ""
        self.game_started = 0
        self.own_hand = {}
        self.players = {}
        self.deck = []
        self.initialize_game()

    def initialize_game(self):
        self.players = {}
        self.game_started = 0
        self.game_state = self.STATE_NOT_STARTED
        self.own_hand = {}
        self.deck = list(range(0, 52))
        random.shuffle(self.deck)

    def pull_from_deck(self):
        card = self.deck.pop()
        if len(self.deck) < 10:
            self.deck = list(range(0, 52))
            random.shuffle(self.deck)
        return card


    def card_to_str(self, card):
        suits = [ "♠", "♥", "♦", "♣" ]
        values = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        suit = card // 13
        value = card % 13
        return f"{values[value]}{suits[suit]}" 

    def add_player_to_game(self, chatuser, bet):
        self.players[chatuser.username] = chatuser
        self.players[chatuser.username].bet = bet
        self.players[chatuser.username].did_stand = False
        self.players[chatuser.username].is_busted = False
        self.players[chatuser.username].hand_value = 0
        chatuser.current_score -= bet

    async def settlement(self):
        response = ""
        cnt_not_standing_players = len([player for player in self.players.values() if not player.did_stand])
        if cnt_not_standing_players == 0:
            response += "Mindenki döntött , jöhet az osztó! "
            dealer_hand_value = sum([card % 13 + 2 for card in self.own_hand])
            if dealer_hand_value > 21 and 0 in [card % 13 for card in self.own_hand]:
                dealer_hand_value -= 10
            while dealer_hand_value < 17:
                self.own_hand.append(self.pull_from_deck())
                dealer_hand_value = sum([card % 13 + 2 for card in self.own_hand])
                if dealer_hand_value > 21 and 0 in [card % 13 for card in self.own_hand]:
                    dealer_hand_value -= 10
            response += f"Az osztó lapjai: {' '.join([self.card_to_str(card) for card in self.own_hand])}. (takarva) "
            for player_tuple in self.players.items():
                player = player_tuple[1]
                player_won = False
                if player.hand_value == 21 and dealer_hand_value != 21:
                    player_won = True
                elif player.hand_value > dealer_hand_value and not player.is_busted:
                    player_won = True
                if player_won:
                    player.current_score += player.bet * 2
                    await sync_to_async(player.save)()
                    response += f"Kedves @{player.visible_name}, nyertél {player.bet*2} zsetont! "
                elif player.hand_value == dealer_hand_value and not player.is_busted:
                    player.current_score += player.bet
                    await sync_to_async(player.save)()
                    response += f"Kedves @{player.visible_name}, döntetlen lett a játék! "
                else:
                    response += f"Kedves @{player.visible_name}, vesztettél {player.bet} zsetont! "
            self.initialize_game()
        else: 
            if cnt_not_standing_players == 1:
                not_standing_player = [
                    player for player in self.players.values() if not player.did_stand][0]
                response += f"Kedves @{not_standing_player.visible_name} döntésére várunk! "
            response += f"Még {cnt_not_standing_players} játékosnak döntenie kell! "
        return response


    def update_hand_value(self, player):
        hand_value = 0
        for card in player.hand:
            card_value = card % 13 + 2
            if card_value < 10:
                hand_value += card_value 
            elif card_value < 14:
                hand_value += 10
            else: 
                hand_value += 11
        if hand_value > 21 and 0 in [card % 13 for card in player.hand]:
            hand_value -= 10
        player.hand_value = hand_value


    async def player_move(self, chatuser, move):
        response = ""
        params = move.split(" ")[1:]
        if self.game_state == self.STATE_WAITING_FOR_BETS and (datetime.datetime.now() - self.game_started).seconds > 60:
            self.game_state = self.STATE_DEAL_HANDS
            response = "A BlackJack kör elindul több beszállás nincs! "
        elif self.game_state == self.STATE_WAITING_FOR_MOVES and (datetime.datetime.now() - self.game_started).seconds > 60:
            for player_tuple in self.players.items():
                player = player_tuple[1]
                if not player.did_stand:
                    player.did_stand = True
        if self.game_state == self.STATE_NOT_STARTED:
            #if chatuser.username not in self.players:
            #    return f"Kedves @{chatuser.visible_name}, ebből a játkból sajnos kimaradtál. " 
            if len(params) != 1:
                return f"Kedves @{chatuser.visible_name}, a !blackjack parancshoz add meg , hogy mennyit szeretnél tenni , pédául: !blackjack 1000. "
            player_bet = int(params[0])
            if player_bet < 1:
                return f"Kedves @{chatuser.visible_name}, a tét csak pozitív egész szám lehet. "
            if player_bet > chatuser.current_score:
                return f"Kedved @{chatuser.visible_name}, nincs ennyi pontod , jelenleg ennyi pontod van : {chatuser.current_score}. "
            # A new game has started with a player joining
            self.add_player_to_game(chatuser, player_bet)
            self.game_state = self.STATE_WAITING_FOR_BETS
            self.game_started = datetime.datetime.now()
            response = ("FIGYELEM ! Indul a BlackJack. Egy percetek van beszállni! "+f" @{chatuser.visible_name} már fogadott is , tétje: {player_bet}. ")
        elif self.game_state == self.STATE_WAITING_FOR_BETS:
            if chatuser.username not in self.players:
                return f"Kedves @{chatuser.visible_name}, ebből a játkból sajnos kimaradtál. " 
            if len(params) != 1:
                return f"Kedves @{chatuser.visible_name}, a !blackjack parancshoz add meg , hogy mennyit szeretnél tenni , pédául: !blackjack 1000. "
            player_bet = int(params[0])
            if player_bet < 1:
                return f"Kedves @{chatuser.visible_name}, a tét csak pozitív egész szám lehet. "
            if player_bet > chatuser.current_score:
                return f"Kedved @{chatuser.visible_name}, nincs ennyi pontod , jelenleg ennyi pontod van : {chatuser.current_score}. "
            if chatuser.username in self.players:
                chatuser.current_score += self.players[chatuser.username].bet
                self.players[chatuser.username].bet = player_bet
                chatuser.current_score -= player_bet
                response = f"Kedves @{chatuser.visible_name}, a téted megváltozott : {player_bet} ."
            else:
                self.add_player_to_game(chatuser, player_bet)
                response = f"Kedves @{chatuser.visible_name}, a téted : {player_bet}. "
        elif self.game_state == self.STATE_DEAL_HANDS:
            # Shuffle the deck
            # Deal two cards to each player
            self.own_hand = [self.pull_from_deck(), self.pull_from_deck()]
            response = f"Az osztó lapjai: {self.card_to_str(self.own_hand[0])} {self.card_to_str(self.own_hand[1])}. "
            for player_tuple in self.players.items():
                player = player_tuple[1]
                player.hand = [self.pull_from_deck(), self.pull_from_deck()]
                response += f"Kedves @{player.visible_name}, a lapjaid: {self.card_to_str(player.hand[0])} {self.card_to_str(player.hand[1])} "
            response += f"Játékosok döntsetek ! hit vagy stand. "
            self.game_state = self.STATE_WAITING_FOR_MOVES
            self.game_started = datetime.datetime.now()
        elif self.game_state == self.STATE_WAITING_FOR_MOVES:
            if chatuser.username not in self.players:
                return f"Kedves @{chatuser.visible_name}, ebből a játkból sajnos kimaradtál. " 
            print("Game waiting for moves")
            if len(params) != 1:
                return f"Kedves @{chatuser.visible_name}, csak hit vagy stand lehet a válaszod. "
            player_move = params[0]
            player = self.players[chatuser.username]
            if player_move not in ["hit", "stand"]:
                return f"Kedves @{chatuser.visible_name}, csak hit vagy stand lehet a válaszod. "
            if player_move == "hit":
                player.hand.append(self.pull_from_deck())
                self.update_hand_value(player)
                if player.hand_value > 21:
                    response = f"Kedves @{player.visible_name}, vesztettél ! Lapjaid: {' '.join([self.card_to_str(card) for card in player.hand])}. "
                    player.did_stand = True
                    player.is_busted = True
                elif player.hand_value == 21:
                    response = f"Kedves @{chatuser.visible_name}, 21 pontod van. Lapjaid: {' '.join([self.card_to_str(card) for card in player.hand])}. "
                    player.did_stand = True
                else:
                    response = f"Kedves @{player.visible_name}, lapjaid: {' '.join([self.card_to_str(card) for card in player.hand])}. Hit vagy stand? "
            elif player_move == "stand":
                self.update_hand_value(player)
                response = f"@{player.visible_name}, rendben, lapjaid : {' '.join([self.card_to_str(card) for card in player.hand])} "
                player.did_stand = True
            response += await self.settlement()

        await sync_to_async(chatuser.save)()
        print(f"Ronomicon: {response}")
        return response