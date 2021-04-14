import os
import random
import pandas as pd

#this is new
#so is this

deck_count = 1
num_players = 3
num_hands_per_tourney = 500
num_tournys = 1
cut_cards = True
dealer_hit_to = 17
dealer_bust = False

class Player():
	def __init__(self,name, strategy, hit_to):
		self.name = name
		self.strategy = strategy
		self.hit_to = hit_to
		self.data = {0:{'name': name, 'total': 0, 'result': None, 'bust': False, 'cards': []}}
		self.num_hands = len(self.data)
# turn this back on if num_shoes does not work
#	@property
#	def num_hands(self):
#		return len(self.data)

class Dealer():
	def __init__(self, hit_to):
		self.hit_to = hit_to
		self.data = {'name': 'dealer', 'total': 0, 'result': None, 'bust': False, 'cards': []}
#		self.num_hands = 1
	

def shuffle(deck_count, cut):
	deck = [2,3,4,5,6,7,8,9,10,'J','Q','K','A'] * 4 * deck_count # four cards of each suit

	random.shuffle(deck)

	if cut: # if cut == True then place cut randomly in first 25-35% of deck
		cut_placement_min = int(round(52 * deck_count * 0.25))
		cut_placement_max = int(round(52 * deck_count * 0.35))
		cut_placement = random.randint(cut_placement_min, cut_placement_max)
		deck.insert(cut_placement, 'CUT')

	global reshuffle
	reshuffle = False

	return deck

def deal(shuffled_deck, players, the_dealer, reshuffle):
	for i in range(2):
		for p in players:
			for h in range(p.num_hands):
				# print(shuffled_deck) # debugging
				if shuffled_deck[-1] == 'CUT': #if the next card is CUT remove it and set the reshuffle flag to True
					shuffled_deck.pop()
					reshuffle = True
				p.data[h]['cards'].append(shuffled_deck.pop()) # deal one card to each player, then one to dealer and repeat once to have two cards each
		
		if shuffled_deck[-1] == 'CUT': #if the next card is CUT remove it and set the reshuffle flag to True
			shuffled_deck.pop()
			reshuffle = True
		the_dealer.data['cards'].append(shuffled_deck.pop())	
	
	return shuffled_deck, players, the_dealer, reshuffle


def hit(hand, deck, reshuffle):
	#print(deck) #debug
	if deck[-1] == 'CUT': #if the next card is CUT remove it and set the reshuffle flag to True
		deck.pop()
		reshuffle = True
	hand.append(deck.pop())
	return hand, deck, reshuffle

def blackjack_check(players, the_dealer):
	for p in players:
		for h in range(p.num_hands):
			if the_dealer.data['total'] == 21 and p.data[h]['total'] < 21:
				p.data[h]['result'] = 'lose'
				# p.data[h]['active'] = False
			elif the_dealer.data['total'] == 21 and p.data[h]['total'] == 21:
				p.data[h]['result'] = 'push'
				# p.data[h]['active'] = False
	return players

def total(hands): #need to account for situation where A needs to be 1 after hit. ex: A, 2 + 10
	total = [0,0]
	for card in hands:
		if card == 'J' or card == 'Q' or card == 'K':
			total[0] += 10
			total[1] += 10
		elif str(card).isnumeric() == True:
			total[0] += card
			total[1] += card
		else:
			total[0] += 1
			total[1] += 11
	if total[0] == total[1]: return total[0]
	elif max(total[0], total[1]) <= 21: return max(total[0], total[1])
	else:
		return min(total[0], total[1])


def game():
	round_counter = 0
	used_cards = 0
	reshuffle = False
	df = pd.DataFrame()


	# shuffle the deck(s)
	shuffled_deck = shuffle(deck_count, cut_cards)


	while round_counter < num_hands_per_tourney:
		if reshuffle:
			shuffled_deck = shuffle(deck_count, cut_cards)

		players = []
		strat = 'stict'

		for n in range(num_players):
			name = 'Bot' + str(n+1)
			players.append(Player(name, strat, 17))

		the_dealer = Dealer(dealer_hit_to)

		# print('cards remaining:')
		# print(len(shuffled_deck))
		# print(reshuffle)
		# print(shuffled_deck)

		# deal the cards
		shuffled_deck, players, the_dealer, reshuffle = deal(shuffled_deck, players, the_dealer, reshuffle)


		# calculate hand totals
		for p in players:
			for h in range(p.num_hands):
				p.data[h]['total'] = total(p.data[h]['cards'])
		the_dealer.data['total'] = total(the_dealer.data['cards'])


		# check for dealer blackjack
		players = blackjack_check(players, the_dealer)

		# hit player hands while total < hit_to target
		for p in players:
			for h in range(p.num_hands):
				while p.data[h]['total'] < p.hit_to:
					p.data[h]['cards'], shuffled_deck, reshuffle = hit(p.data[h]['cards'], shuffled_deck, reshuffle)
					p.data[h]['total'] = total(p.data[h]['cards'])
					if p.data[h]['total'] > 21: p.data[h]['bust'] = True


		# hit dealer hand while total < hit_to target
		while the_dealer.data['total'] < dealer_hit_to:
			the_dealer.data['cards'], shuffled_deck, reshuffle = hit(the_dealer.data['cards'], shuffled_deck, reshuffle)
			the_dealer.data['total'] = total(the_dealer.data['cards'])
			if the_dealer.data['total'] > 21: the_dealer.data['bust'] = True

		for p in players:
			for h in range(p.num_hands):
				if p.data[h]['bust']:
					p.data[h]['result'] = 'lose'
				elif the_dealer.data['bust']:
					p.data[h]['result'] = 'win'
				elif p.data[h]['total'] > the_dealer.data['total']:
					p.data[h]['result'] = 'win'
				elif p.data[h]['total'] < the_dealer.data['total']:
					p.data[h]['result'] = 'lose'
				elif p.data[h]['total'] == the_dealer.data['total']:
					p.data[h]['result'] = 'push'
				
				temp_df = pd.DataFrame.from_dict(p.data[h], orient='index').swapaxes('index','columns')
				temp_df['round'] = round_counter
				df = df.append(temp_df)
				# print(temp_df)
				# print(p.name)
				# print(p.data[h])
		
		temp_df = pd.DataFrame.from_dict(the_dealer.data, orient='index').swapaxes('index','columns')
		temp_df['round'] = round_counter
		df = df.append(temp_df)
		# print('dealer')	
		# print(the_dealer.data)

		round_counter += 1
		# print(round_counter)
		# print(shuffled_deck)
	df.reset_index(inplace=True, drop=True)
	print(df.head(20))

if __name__ == "__main__":
	game()






