import sys
import json
import random

from pypokerengine.players import BasePokerPlayer
from pypokerengine.api.game import setup_config, start_poker
import pypokerengine.utils.visualize_utils as U
from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate
from pypokerengine.api.emulator import Emulator
from pypokerengine.utils.game_state_utils import restore_game_state, attach_hole_card, attach_hole_card_from_deck
from eval import fast_eval

NB_SIMULATION = 100

class FishPlayer(BasePokerPlayer):  # Do not forget to make parent class as "BasePokerPlayer"

    #  we define the logic to make an action through this method. (so this method would be the core of your AI)
    def declare_action(self, valid_actions, hole_card, round_state):
        # valid_actions format => [raise_action_info, call_action_info, fold_action_info]
        call_action_info = valid_actions[1]
        action, amount = call_action_info["action"], call_action_info["amount"]
        return action, amount   # action returned here is sent to the poker engine

    def receive_game_start_message(self, game_info):
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass

class FoldPlayer(BasePokerPlayer):
    def declare_action(self, valid_actions, hole_card, round_state):
        return 'fold', 0

    def receive_game_start_message(self, game_info):
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, new_action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass

class RandomPlayer(BasePokerPlayer):
    def __init__(self):
        self.fold_ratio = self.call_ratio = raise_ratio = 1.0 / 3

    def set_action_ratio(self, fold_ratio, call_ratio, raise_ratio):
        ratio = [fold_ratio, call_ratio, raise_ratio]
        scaled_ratio = [1.0 * num / sum(ratio) for num in ratio]
        self.fold_ratio, self.call_ratio, self.raise_ratio = scaled_ratio

    def declare_action(self, valid_actions, hole_card, round_state):
        choice = self.__choice_action(valid_actions)
        action = choice["action"]
        amount = choice["amount"]
        if action == "raise":
            amount = random.randrange(amount["min"], max(amount["min"], amount["max"]) + 1)
        return action, amount

    def __choice_action(self, valid_actions):
        r = random.random()
        if r <= self.fold_ratio:
            return valid_actions[0]
        elif r <= self.call_ratio:
            return valid_actions[1]
        else:
            return valid_actions[2]

    def receive_game_start_message(self, game_info):
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, new_action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass

class AllInPlayer(BasePokerPlayer):
    # def get_position(self, round_state):
    #     my_pos = round_state['next_player']
    #     cur_dist = 0
    #     cur_pos = my_pos
    #     while cur_pos != round_state['big_blind_pos']:
    #         cur_pos = (cur_pos + 1) % 9
    #         if round_state['seats'][cur_pos]['state'] != 'folded':
    #             cur_dist += 1
    #     return cur_dist

    def declare_action(self, valid_actions, hole_card, round_state):
        community_card = round_state['community_card']
        win_rate = fast_eval(hole_card,community_card, simulations = 1000)
        if win_rate >= 1.0 / self.nb_player ** 0.5:
            if valid_actions[2]['amount']['max'] != -1:
                return valid_actions[2]['action'], valid_actions[2]['amount']['max']
            else:
                return valid_actions[1]['action'], valid_actions[1]['amount']

        if valid_actions[1]['amount'] <= 30:
            return valid_actions[1]['action'], valid_actions[1]['amount']
        return valid_actions[0]['action'], 0

    def receive_game_start_message(self, game_info):
        self.nb_player = game_info['player_num']
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass

class HonestPlayer(BasePokerPlayer):
    def __init__(self, nb_simulation=50):
        self.nb_simulation = nb_simulation

    def declare_action(self, valid_actions, hole_card, round_state):
        community_card = round_state['community_card']
        win_rate = estimate_hole_card_win_rate(
            nb_simulation=self.nb_simulation,
            nb_player=self.nb_player,
            hole_card=gen_cards(hole_card),
            community_card=gen_cards(community_card)
        )
        if win_rate >= 1.0 / self.nb_player:
            action = valid_actions[1]  # fetch CALL action info
        else:
            action = valid_actions[0]  # fetch FOLD action info
        return action['action'], action['amount']

    def receive_game_start_message(self, game_info):
        self.nb_player = game_info['player_num']

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass

class ConsolePlayer(BasePokerPlayer):

    def declare_action(self, valid_actions, hole_card, round_state):
        print(U.visualize_declare_action(valid_actions, hole_card, round_state, self.uuid))
        action, amount = self._receive_action_from_console(valid_actions)
        return action, amount

    def receive_game_start_message(self, game_info):
        print(U.visualize_game_start(game_info, self.uuid))
        self._wait_until_input()

    def receive_round_start_message(self, round_count, hole_card, seats):
        print(U.visualize_round_start(round_count, hole_card, seats, self.uuid))
        self._wait_until_input()

    def receive_street_start_message(self, street, round_state):
        print(U.visualize_street_start(street, round_state, self.uuid))
        self._wait_until_input()

    def receive_game_update_message(self, new_action, round_state):
        print(U.visualize_game_update(new_action, round_state, self.uuid))
        self._wait_until_input()

    def receive_round_result_message(self, winners, hand_info, round_state):
        print(U.visualize_round_result(winners, hand_info, round_state, self.uuid))
        self._wait_until_input()

    def _wait_until_input(self):
        input("Enter some key to continue ...")

    # FIXME: This code would be crash if receives invalid input.
    #        So you should add error handling properly.
    def _receive_action_from_console(self, valid_actions):
        action = input("Enter action to declare >> ")
        if action == 'fold': amount = 0
        if action == 'call':  amount = valid_actions[1]['action']
        if action == 'raise':  amount = int(input("Enter raise amount >> "))
        return action, amount

DEBUG_MODE = False
def log(msg):
    if DEBUG_MODE: print("[debug_info] --> %s" % msg)

class EmulatorPlayer(BasePokerPlayer):
    def set_opponents_model(self, model_player):
        self.opponents_model = model_player

    # setup Emulator with passed game information
    def receive_game_start_message(self, game_info):
        self.my_model = MyModel()
        nb_player = game_info['player_num']
        max_round = game_info['rule']['max_round']
        sb_amount = game_info['rule']['small_blind_amount']
        ante_amount = game_info['rule']['ante']

        self.emulator = Emulator()
        self.emulator.set_game_rule(nb_player, max_round, sb_amount, ante_amount)
        self.opponents_model = RandomPlayer()
        for player_info in game_info['seats']:
            uuid = player_info['uuid']
            player_model = self.my_model if uuid == self.uuid else self.opponents_model
            self.emulator.register_player(uuid, player_model)

    def declare_action(self, valid_actions, hole_card, round_state):
        try_actions = [MyModel.FOLD, MyModel.CALL, MyModel.MIN_RAISE, MyModel.MAX_RAISE]
        action_results = [0 for i in range(len(try_actions))]

        log("hole_card of emulator player is %s" % hole_card)
        for action in try_actions:
            self.my_model.set_action(action)
            simulation_results = []
            for i in range(NB_SIMULATION):
                game_state = self._setup_game_state(round_state, hole_card)
                round_finished_state, _events = self.emulator.run_until_round_finish(game_state)
                my_stack = [player for player in round_finished_state['table'].seats.players if player.uuid == self.uuid][0].stack
                simulation_results.append(my_stack)
            action_results[action] = 1.0 * sum(simulation_results) / NB_SIMULATION
            log("average stack after simulation when declares %s : %s" % (
                {0:'FOLD', 1:'CALL', 2:'MIN_RAISE', 3:'MAX_RAISE'}[action], action_results[action])
                )

        best_action = max(zip(action_results, try_actions))[1]
        self.my_model.set_action(best_action)
        return self.my_model.declare_action(valid_actions, hole_card, round_state)

    def _setup_game_state(self, round_state, my_hole_card):
        game_state = restore_game_state(round_state)
        game_state['table'].deck.shuffle()
        player_uuids = [player_info['uuid'] for player_info in round_state['seats']]
        for uuid in player_uuids:
            if uuid == self.uuid:
                game_state = attach_hole_card(game_state, uuid, gen_cards(my_hole_card))  # attach my holecard
            else:
                game_state = attach_hole_card_from_deck(game_state, uuid)  # attach opponents holecard at random
        return game_state

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, new_action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass

class MyModel(BasePokerPlayer):

    FOLD = 0
    CALL = 1
    MIN_RAISE = 2
    MAX_RAISE = 3

    def set_action(self, action):
        self.action = action

    def declare_action(self, valid_actions, hole_card, round_state):
        if self.FOLD == self.action:
            return valid_actions[0]['action'], valid_actions[0]['amount']
        elif self.CALL == self.action:
            return valid_actions[1]['action'], valid_actions[1]['amount']
        elif self.MIN_RAISE == self.action:
            return valid_actions[2]['action'], valid_actions[2]['amount']['min']
        elif self.MAX_RAISE == self.action:
            return valid_actions[2]['action'], valid_actions[2]['amount']['max']
        else:
            raise Exception("Invalid action [ %s ] is set" % self.action)


def predict_S(name, street, bank, amount, num_players, action):
    strength = 0.2
    return strength

def predict_A(name, street, bank, amount, num_players, strength):
    action = 'call'
    return action


class SmartPlayer(BasePokerPlayer):
    def declare_action(self, valid_actions, hole_card, round_state):
        community_card = round_state['community_card']
        win_rate = win_rate = estimate_hole_card_win_rate(
            nb_simulation=30,
            nb_player=self.nb_player,
            hole_card=gen_cards(hole_card),
            community_card=gen_cards(community_card)
        )
        if valid_actions[2]['amount']['max'] != -1 and win_rate < self.nb_player ** 0.5:
            flag = True
            for p in self.s:
                if predict_A(self.names[p], round_state['street'], round_state['pot']['main'], valid_actions[2]['amount']['max'], 9, self.s[p]) != 'fold':
                    flag = False
                    break
            if flag == True:
                if valid_actions[2]['amount']['max'] != -1:
                    return  valid_actions[2]['action'], valid_actions[2]['amount']['max']
                else:
                    return valid_actions[1]['action'], valid_actions[1]['amount']

        for p in self.s:
            if self.s[p] > win_rate*win_rate:
                return valid_actions[0]['action'], 0

        if valid_actions[2]['amount']['max'] != -1:
            for p in self.s:
                if predict_A(self.names[p], round_state['street'], round_state['pot']['main'], (valid_actions[2]['amount']['max'] + valid_actions[2]['amount']['min'])/2, 9, self.s[p]) != 'fold':
                    return valid_actions[2]['action'], (valid_actions[2]['amount']['max'] + valid_actions[2]['amount']['min'])/2
            return valid_actions[1]['action'], valid_actions[1]['amount']
        else:
            return valid_actions[1]['action'], valid_actions[1]['amount']

    def receive_game_start_message(self, game_info):
        self.all_in = False
        self.s = {}
        self.names = {}
        self.nb_player = game_info['player_num']

    def receive_round_start_message(self, round_count, hole_card, seats):
        self.all_in = False
        self.s = {}
        self.names = {}
        for seat in seats:
            self.s[seat['uuid']] = 1 / self.nb_player
            self.names[seat['uuid']] = seat['name']

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        if action['action'] == 'fold':
            self.s[action['player_uuid']] = 0
        else:
            self.s[action['player_uuid']] =\
                predict_S(self.names[action['player_uuid']], round_state['street'],round_state['pot']['main'], action['amount'], 9, action['action'])
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass


if __name__ == '__main__':
    player = AllInPlayer()
    # ave = 0
    # for i in range(0,30):
    #     config = setup_config(max_round = 50, initial_stack = 1500, small_blind_amount = 15)
    #     config.register_player(name="TargetBot", algorithm = player)
    #     for j in range(0,8):
    #         config.register_player(name="FishPlayer" + str(j), algorithm=RandomPlayer())
    #     game_result = start_poker(config, verbose=0)
    #     #print(game_result)
    #     print(game_result['players'][0]['stack'])
    #     ave += game_result['players'][0]['stack']
    #     print("Game #" + str(i+1))
    # print(ave/30)
    while True:
        line = sys.stdin.readline().rstrip()
        if not line:
           break
        event_type, data = line.split('\t', 1)
        data = json.loads(data)

        if event_type == 'declare_action':
            action, amount = player.declare_action(data['valid_actions'], data['hole_card'], data['round_state'])
            if amount == -1:
                sys.stdout.write('{}\t{}\n'.format("fold", 0))
            else:
                sys.stdout.write('{}\t{}\n'.format(action, int(amount)))
            sys.stdout.flush()
        elif event_type == 'game_start':
            player.receive_game_start_message(data)
        elif event_type == 'round_start':
            player.receive_round_start_message(data['round_count'], data['hole_card'], data['seats'])
        elif event_type == 'street_start':
            player.receive_street_start_message(data['street'], data['round_state'])
        elif event_type == 'game_update':
            player.receive_game_update_message(data['new_action'], data['round_state'])
        elif event_type == 'round_result':
            player.receive_round_result_message(data['winners'], data['hand_info'], data['round_state'])
        else:
            raise RuntimeError('Bad event type "{}"'.format(event_type))

