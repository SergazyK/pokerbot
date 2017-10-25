from deuces import Card
from deuces import Evaluator
from deuces import Deck

def conv(c):
    res = c[1] + c[0].lower()
    return res
def fast_eval(hole_card, public_card, players = 9, simulations = 1000):
    players = players - 1
    for i in range(0, len(hole_card)):
        hole_card[i] = Card.new(conv(hole_card[i]))
    for i in range(0, len(public_card)):
        public_card[i] = Card.new(conv(public_card[i]))
    win_rate = 0
    evaluator = Evaluator()
    for _ in range(simulations):
        deck = Deck()
        for c in hole_card:
            deck.cards.remove(c)
        for c in public_card:
            deck.cards.remove(c)
        player_hands = []
        for _ in range(players):
            player_hands.append(deck.draw(2))
        board = []
        board.extend(public_card)
        if 5 - len(public_card) == 1:
            board.append(deck.draw(1))
        else:
            board.extend(deck.draw(5 - len(public_card)))
        flag = True
        num = 1.0
        for p in range(0, len(player_hands)):
            if evaluator.evaluate(board, player_hands[p]) < evaluator.evaluate(board, hole_card):
                flag = False
                break
            elif evaluator.evaluate(board, player_hands[p]) > evaluator.evaluate(board, hole_card):
                continue
            else:
                num += 1.0
        if flag:
            win_rate += 1.0/num
    return 1.0*win_rate/simulations