from .chatgame import ChatGame
import random
from asgiref.sync import sync_to_async 

class Roulette(ChatGame):

    async def player_move(self,chatuser,move, log):
        response = ""
        instructions = f"Kedves @{chatuser.nickname} a rulett parancshoz add meg , hogy mire teszel és mennyit. Tehetsz az alábbiakra : piros , fekete , konkrét szám, páros , páratlan , alacsony (1-18) , magas (19-36)."
        if move == f"{self.chatbot.twitch_prefix}rulett":
            return instructions
        params = move.split(" ")[1:]
        if len(params) != 2:
            return instructions
        bet, amount = params
        if not amount.isdigit():
            return f"Kedves {chatuser.nickname}, a tét csak szám lehet."
        if int(amount) < 1:
            return f"Kedves {chatuser.nickname}, a tét csak pozitív szám lehet" 
        if bet not in ["piros", "fekete", "konkrét", "páros", "páratlan", "alacsony", "magas"] and not bet.isdigit():
            return f"Kedves {chatuser.nickname}, a tét csak piros, fekete, konkrét szá, páros, páratlan, alacsony vagy magas lehet."
        if int(amount) > chatuser.current_score:
            return f"Kedves {chatuser.nickname}, nincs elegő pontod. Jelenelegi pontszámod: {chatuser.current_score}"
        chatuser.current_score -= int(amount)
        rolled_result = random.randint(1, 36)
        red_numbers = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
        black_numbers = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]
        if bet in ["piros", "fekete"]:
            if (bet == "piros" and rolled_result in red_numbers) or (bet == "fekete" and rolled_result in black_numbers):
                chatuser.current_score += int(amount)*2
                response = f"Gratulálunk! @{chatuser.nickname} nyertél {int(amount)*2} pontot! Az eredmény: {rolled_result}. A jelenelegi pontszámod: {chatuser.current_score}"
            else:
                response = f"Sajnos @{chatuser.nickname}, nem nyertél. Az eredmény: {rolled_result}. A jelenelegi pontszámod: {chatuser.current_score}"
        elif bet in ["páros", "páratlan"]:
            if (bet == "páros" and rolled_result % 2 == 0) or (bet == "páratlan" and rolled_result % 2 == 1):
                chatuser.current_score += int(amount)*2
                response = f"Gratulálunk! @{chatuser.nickname} nyertél {int(amount)*2} pontot! Az eredmény: {rolled_result}. A jelenelegi pontszámod: {chatuser.current_score}"
            else:
                response = f"Sajnos @{chatuser.nickname}, nem nyertél. Az eredmény: {rolled_result}. A jelenelegi pontszámod: {chatuser.current_score}"
        elif bet in ["alacsony", "magas"]:
            if (bet == "alacsony" and rolled_result <= 18) or (bet == "magas" and rolled_result >= 19):
                chatuser.current_score += int(amount)*2
                response = f"Gratulálunk! @{chatuser.nickname} nyertél {int(amount)*2} pontot! Az eredmény: {rolled_result}. A jelenelegi pontszámod: {chatuser.current_score}"
            else:
                response = f"Sajnos @{chatuser.nickname}, nem nyertél. Az eredmény: {rolled_result}."
        else:
            if rolled_result == int(bet):
                chatuser.current_score += int(amount)*36
                response = f"Gratulálunk! @{chatuser.nickname} nyertél {int(amount)*36} pontot! Az eredmény: {rolled_result}. A jelenelegi pontszámod: {chatuser.current_score}"
            else:
                chatuser.current_score -= int(amount)
                response = f"Sajnos @{chatuser.nickname}, nem nyertél. Az eredmény: {rolled_result}. A jelenelegi pontszámod: {chatuser.current_score}"
        sync_to_async(chatuser.save)()
        return response