import pymongo
import json
import pandas as pd
import datetime
import time

db = pymongo.MongoClient('mongodb://guest:sberbank2017@data.sberbank.ai/holdem_games').get_database('holdem_games')

def get_table(name):
    uuid_user = None
    curr_date = datetime.datetime.now()
    delta = datetime.timedelta(minutes = 30)
    features_names = ['action', 'amount', 'street', 'winrate']
    dict_action = {key:[] for key in features_names}
    results = db.games.find( {'label': 'default', 'seats.name': name}).where('this.timestamp>' + str((curr_date - delta).timestamp()))
    for result in results:
        for player in result['seats']:
            if player['name'] == name:
                uuid_user = player['uuid']
        for curr_round in result['rounds']:
            action_histories = curr_round['round_state']['action_histories']
            community_card = curr_round['round_state']['community_card']
            hole_card = None
            for key in curr_round['round_state']:
                print(key)
            print()
            for player in curr_round['round_state']['seats']:
                if player['uuid'] != uuid_user:
                    continue
                hole_card = player['hole_card']
            pot = 0
            for street in ['preflop', 'flop', 'turn', 'river']:
                if street in action_histories and action_histories[street]:
                    if street == 'preflop':
                        community_card = []
                    elif street == 'flop':
                        community_card = community_card[:3]
                    elif street == 'turn':
                        community_card = community_card[:4]
                    else:
                        community_card = community_card
                    for action in action_histories[street]:
                        if action['uuid'] != uuid_user:
                            continue
                        if action['action'] == 'SMALLBLIND' or action['action'] == 'BIGBLIND':
                            continue
                        win_rate = fast_eval(
                                    hole_card=gen_cards(hole_card),
                                    public_card=gen_cards(community_card)
                        )
                        dict_action['winrate'] += [win_rate]
                        dict_action['action'] += [action['action']]
                        if 'amount' in action:
                            dict_action['amount'] += [action['amount']]
                        else:
                            dict_action['amount'] += [0]
                        dict_action['street'] += [street]

    user_data = pd.DataFrame()
    for key in features_names:
        user_data[key] = dict_action[key]

    return user_data

startTime = time.time()
data = get_table('v_lfvjaCeJfpbPhayTvKow')
endTime = time.time()
print(endTime - startTime)