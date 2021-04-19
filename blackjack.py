import sys
import random
import pandas as pd
import pickle

class Player():
	def __init__(self, name, hit_strategy):
		self.name = name
		# self.hit_to = hit_to
		self.data = {0:{'active': True, 'name': name, 'total': 0, 'result': None, 'bust': False, 'blackjack': False, 'cards': [], 'hit_strategy': hit_strategy, 'dealer_up_card': 0},
					 1:{'active': False, 'name': name, 'total': 0, 'result': None, 'bust': False, 'blackjack': False, 'cards': [], 'hit_strategy': hit_strategy, 'dealer_up_card': 0},
					 2:{'active': False, 'name': name, 'total': 0, 'result': None, 'bust': False, 'blackjack': False, 'cards': [], 'hit_strategy': hit_strategy, 'dealer_up_card': 0}}
		# self.num_hands = len(self.data)

	@property
	def num_hands(self):
		active_count = 0
		for key, value in self.data.items():
			if value['active'] == True: active_count += 1
		return active_count
		

class Dealer():
	def __init__(self, hit_to):
		# self.hit_to = hit_to
		self.data = {'active': True, 'name': 'dealer', 'total': 0, 'result': None, 'bust': False, 'blackjack': False, 'cards': [], 'hit_strategy': hit_to, 'dealer_up_card': 0}
	
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
	if the_dealer.data['total'] == 21:
		the_dealer.data['blackjack'] = True
		for p in players:
			for h in range(p.num_hands):
				if p.data[h]['total'] < 21:
					p.data[h]['result'] = 'lose'
				elif p.data[h]['total'] == 21:
					p.data[h]['result'] = 'push'
					p.data[h]['blackjack'] = True
	return players, the_dealer

def total(hands):
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


def game(deck_count, num_players, num_rounds, cut_cards, dealer_hit_to, hit_strategies):
	round_counter = 0
	used_cards = 0
	reshuffle = False
	dealer_bust = False
	df = pd.DataFrame()

	# validate 
	if len(hit_strategies) != num_players:
		sys.exit('num_players must equal len(hit_strategies)')

	# read split strategies into dataframe
	split_df = pd.read_csv('split_strategy.csv').set_index('0')


	# shuffle the deck(s)
	shuffled_deck = shuffle(deck_count, cut_cards)


	while round_counter < num_rounds:
		if reshuffle:
			shuffled_deck = shuffle(deck_count, cut_cards)

		# list to hold player objects
		players = []

		for n in range(num_players):
			name = 'Player' + str(n+1)
			players.append(Player(name, hit_strategies[n]))

		# print(hit_strategies)
		# print(players[0].data[0]['hit_strategy'])

		the_dealer = Dealer(dealer_hit_to)

		# deal the cards
		shuffled_deck, players, the_dealer, reshuffle = deal(shuffled_deck, players, the_dealer, reshuffle)

		# calculate hand totals and assign dealer up card
		the_dealer.data['total'] = total(the_dealer.data['cards'])

		dealer_up = the_dealer.data['cards'][0]
		if dealer_up == 'K' or dealer_up == 'Q' or dealer_up == 'J':
			dealer_up = 10
		elif dealer_up == 'A': dealer_up = 11

		the_dealer.data['dealer_up_card'] = dealer_up

		for p in players:
			for h in range(p.num_hands):
				p.data[h]['total'] = total(p.data[h]['cards'])
				p.data[h]['dealer_up_card'] = dealer_up

		# check for dealer blackjack
		players, the_dealer = blackjack_check(players, the_dealer)
		

		if the_dealer.data['blackjack'] == False:
			for p in players:
				for h in range(p.num_hands):
					#check for splittable hand and split
					if p.data[h]['cards'][0] == p.data[h]['cards'][1]:
						if split_df[str(the_dealer.data['cards'][0])][str(p.data[h]['cards'][0])]:
							p.data[h+1]['active'] = True
							p.data[h+1]['cards'].append(p.data[h]['cards'].pop())
							p.data[h]['cards'], shuffled_deck, reshuffle = hit(p.data[h]['cards'], shuffled_deck, reshuffle)
							p.data[h+1]['cards'], shuffled_deck, reshuffle = hit(p.data[h+1]['cards'], shuffled_deck, reshuffle)
							p.data[h]['total'] = total(p.data[h]['cards'])
							p.data[h+1]['total'] = total(p.data[h+1]['cards'])
							p.data[h+1]['dealer_up_card'] = p.data[h]['dealer_up_card']

			for p in players:
				for h in range(p.num_hands):
					# hit player hands while total < hit_to target
					while p.data[h]['total'] < p.data[h]['hit_strategy'][dealer_up]:
						p.data[h]['cards'], shuffled_deck, reshuffle = hit(p.data[h]['cards'], shuffled_deck, reshuffle)
						p.data[h]['total'] = total(p.data[h]['cards'])
						if p.data[h]['total'] > 21: p.data[h]['bust'] = True


			# hit dealer hand while total < hit_to target
			while the_dealer.data['total'] < the_dealer.data['hit_strategy']:
				the_dealer.data['cards'], shuffled_deck, reshuffle = hit(the_dealer.data['cards'], shuffled_deck, reshuffle)
				the_dealer.data['total'] = total(the_dealer.data['cards'])
				if the_dealer.data['total'] > 21: the_dealer.data['bust'] = True

		for p in players:
			for h in range(p.num_hands):
				if the_dealer.data['blackjack'] == False:
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
				
				# write each player's data to a dataframe
				if p.data[h]['active'] == True:
					temp_df = pd.DataFrame.from_dict(p.data[h], orient='index').swapaxes('index','columns')
					temp_df['round'] = round_counter
					temp_df['hand'] = h
					temp_df = temp_df.drop(['active'], axis=1)
					df = df.append(temp_df)
		
		# write dealer's data to dataframe
		temp_df = pd.DataFrame.from_dict(the_dealer.data, orient='index').swapaxes('index','columns')
		temp_df['round'] = round_counter
		temp_df['hand'] = 0
		temp_df = temp_df.drop(['active'], axis=1)
		df = df.append(temp_df)

		
		round_counter += 1
		# print(round_counter)
		# print(shuffled_deck)

	df.reset_index(inplace=True, drop=True)
	# print(df.head(20))
	outfile = open('blackjack.pickle','wb')
	pickle.dump(df,outfile)
	outfile.close()
	print('Done!')

if __name__ == "__main__":
	deck_count = 1
	num_players = 3
	num_rounds = 500
	cut_cards = True
	dealer_hit_to = 17
	# format of hit_strategies dict: {player: {dealer_up_card: player_hit_to}}
	hit_strategies = {0: {2: 13, 3: 13, 4: 12, 5: 12, 6: 12, 7: 12, 8: 17, 9: 17, 10: 17, 11: 17},
				      1: {2: 13, 3: 13, 4: 12, 5: 12, 6: 12, 7: 12, 8: 17, 9: 17, 10: 17, 11: 17},
				      2: {2: 13, 3: 13, 4: 12, 5: 12, 6: 12, 7: 12, 8: 17, 9: 17, 10: 17, 11: 17}}
	

	game(deck_count, num_players, num_rounds, cut_cards, dealer_hit_to, hit_strategies)







