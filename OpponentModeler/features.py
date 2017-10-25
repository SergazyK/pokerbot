
# coding: utf-8

# In[8]:



import copy
import pandas as pd
from src.bot.util.features import *
from src.bot.util.data import *


# In[31]:

tournaments = [
    'games/final/'
]

num_games = 0
max_games = 0

player = GamePlayer()
player.filter_seats(lambda x: x['private_bot_top'])
counter = 0
for tournament_dir in tournaments:
    for game in get_games(tournament_dir, player_names=["fcll"]):
        if (max_games == 0) or (num_games < max_games):
            player.play_game(game)
            num_games += 1
            print(counter)
            counter += 1
        else:
            break

    print('Tournament: ' + tournament_dir + ' Games: ' + str(num_games))

X, y = player.get_features()
X.to_pickle('data/X_final.pickle')
y.to_pickle('data/y_final.pickle')

y.head()

