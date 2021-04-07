import os
import random

#this is new

deck_count = 2
num_players = 3
num_hands = 1000
cut_cards = True
reshuffle = False
dealer_hit_to = 17

class Player():
	def __init__(self, name, strategy):
		self.name = name
		self.strategy = strategy
		self.hit_to = 17
		self.hands = []
		self.totals = []
		self.actions = {0: None}
		self.results = {0: True}
		self.actives = {0: True}
	@property
	def num_hands(self):
		return int(sum([len(item) for item in self.hands])/2) #2 cards per hand initially, so card-count / 2 = hand count
	

def shuffle(deck_count, cut):
	deck = [2,3,4,5,6,7,8,9,10,'J','Q','K','A'] * 4 * deck_count # four cards of each suit

	random.shuffle(deck)

	if cut: # if cut == True then place cut randomly in first 25-35% of deck
		cut_placement_min = int(round(52 * deck_count * 0.25))
		cut_placement_max = int(round(52 * deck_count * 0.35))
		cut_placement = random.randint(cut_placement_min, cut_placement_max)
		deck.insert(cut_placement, 'CUT')

	return deck

def deal(shuffled_deck, players, dealer_hand):
	for i in range(2):
		for p in players:
			if shuffled_deck[-1] == 'CUT': #if the next card is CUT remove it and set the reshuffle flag to True
				deck.pop()
				global reshuffle
				reshuffle = True
			p.hands.append(shuffled_deck.pop()) # deal one card to each player, then one to dealer and repeat once to have two cards each
		dealer_hand.append(shuffled_deck.pop())	
	for p in players:
		p.hands = [p.hands]
		p.actives = [True]
	dealer_hand = [dealer_hand]
	
	return shuffled_deck, players, dealer_hand


def hit(hand, deck):
	#print(deck) #debug
	hand.append(deck.pop())
	return hand, deck

def blackjack(players, dealer_hand):
	dealer_total = total(dealer_hand)

	for p in players:
		player_total = total(p.hand)
		
		if player_total == 21 and dealer_total < 21:
			p.score = player_total
			p.result = 'blackjack'
			p.active = False
		elif player_total < 21 and dealer_total == 21:
			p.total = player_total
			p.result = 'beaten by dealer'
			p.active = False
		elif player_total == 21 and dealer_total == 21:
			p.total = player_total
			p.result = 'push'
			p.active = False

	return players, dealer_hand

def total(hands):
    totals = []
    hand_count = len(hands)
    for hand in range(hand_count):
        total = 0
        for card in range(len(hands[hand])):
            if hands[hand][card] == 'J' or hands[hand][card] == 'Q' or hands[hand][card] == 'K':
                total += 10
            elif str(hands[hand][card]).isnumeric() == True:
                total += hands[hand][card]
            else:
                if total >= 11:
                    total +=1
                else:
                	total += 11
        totals.append(total)
    return totals



def game():
	round_counter = 0
	used_cards = 0

	players = []
	strat = 'stict'

	for n in range(num_players):
		name = 'Bot' + str(n+1)
		players.append(Player(name, strat))

	shuffled_deck = shuffle(deck_count, cut_cards)

	#print(len(shuffled_deck)-1)

	dealer_hand = []

	shuffled_deck, players, dealer_hand = deal(shuffled_deck, players, dealer_hand)

	

	for p in players:
		p.totals = total(p.hands)
		for i in range(p.num_hands):
			print(p.name)
			print(p.hands[i])
			print(p.totals[i])
	print('dealer')
	print(dealer_hand[i])
	dealer_total = total(dealer_hand)
	print(dealer_total)

	print('##############################################')


	#dealer_total = total(dealer_hand)

	for p in players:
		p.totals = total(p.hands)
		for i in range(p.num_hands):
			while p.actives[i] != False:
				if dealer_total == 21 and p.totals[i] < 21:
					p.results[i] = 'lose - delear 21'
					p.actives[i] = False
				elif dealer_total == 21 and p.totals[i] == 21:
					p.results[i] = 'push'
					p.actives[i] = False
				elif p.totals[i] > 21:
					p.results[i] = 'bust'
					p.actives[i] = False
				elif p.totals[i] >= p.hit_to:
					p.actives[i] = False
				elif p.totals[i] < p.hit_to:
					p.hands[i], shuffled_deck = hit(p.hands[i], shuffled_deck)
				p.totals = total(p.hands)

	while dealer_total < 17:
		dealer_hand, shuffled_deck = hit(dealer_hand, shuffled_deck)

	for p in players:
		p.totals = total(p.hands)
		for i in range(p.num_hands):
			print(p.name)
			print(p.hands[i])
			print(p.totals[i])
			print(p.results[i])
	print('dealer')
	print(dealer_hand[i])
	dealer_total = total(dealer_hand)
	print(dealer_total)

	print('##############################################')
					


		


	# for p in players:
	# 	for i in range(p.num_hands):
	# 		p.total

	# if total(dealer_hand) == 21:
	# 	for p in players:
	# 		if p.





if __name__ == "__main__":
	game()






