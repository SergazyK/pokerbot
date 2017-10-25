import copy
import pandas as pd
from pypokerengine.players import BasePokerPlayer
from bot.util.features import *
from bot.util.model import MergeModel
from catboost import CatBoostClassifier, CatBoostRegressor
import pickle
from bot.v6final.bot_emulator import BotEmulatorPlayer

class CounterPlayer(BasePokerPlayer):
    def __init__(self):
        super().__init__()
    def declare_action(self, valid_actions, hole_card, round_state):
        # valid_actions format => [raise_action_info, call_action_info, fold_action_info]
        action = random.choice(valid_actions)["action"]
        if action == "raise":
            action_info = valid_actions[2]
            amount = random.randint(action_info["amount"]["min"], action_info["amount"]["max"])
            if amount == -1: action = "call"
        if action == "call":
            action_info = valid_actions[1]
            amount = action_info["amount"]
        if action == "fold":
            action_info = valid_actions[0]
            amount = action_info["amount"]
        return action, amount  # action returned here is sent to the poker engine

    def receive_game_start_message(self, game_info):
        self.player_model = {}
        for seat in game_info['seats']:
            self.player_model[seat['name']] = BotEmulatorPlayer(bot_name = seat['name'])

        for p in self.player_model:
            p.receive_game_start_message(game_info)
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        for p in self.player_model:
            p.receive_round_start_message(round_count, hole_card, seats)
        pass

    def receive_street_start_message(self, street, round_state):

        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        for p in self.player_model:
            p.receive_round_result_message(winners, hand_info, round_state)
        pass
