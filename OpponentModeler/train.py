
# coding: utf-8

# In[1]:



import pandas as pd
from src.bot.util.features import clean_features
from src.bot.util.model import ModelPool, MergeModel
from src.bot.util.data import *
from catboost import CatBoostClassifier, CatBoostRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score

data_dir = 'data/';
model_dir = 'src/model/final/';


# In[5]:

#X, y = stack_Xy(data_dir, 0)


# In[2]:

X = pd.read_pickle(data_dir + 'X_final.pickle')
y = pd.read_pickle(data_dir + 'y_final.pickle')
names = y['private_bot_name'].value_counts().index.sort_values().tolist()
names


# # TRAIN MERGE

# In[6]:

# def train_call_model():
#     model_call_pool = ModelPool(len(names), model_dir + 'pool/call/')
#     y_call = y['private_bot_action'].replace({'FOLD': 0, 'CALL': 1, 'RAISE': 1})
#     X_call = model_call_pool.predict(X)
#
#     X_train, X_test, y_train, y_test = train_test_split(X_call, y_call, test_size=0.1, random_state=1234)
#
#     model = CatBoostClassifier(iterations=200, learning_rate=0.1, depth=2, thread_count=4,
#                                    verbose=True, use_best_model=True)
#     model.fit(X_train, y_train, eval_set=(X_test, y_test))
#     model.save_model(model_dir + 'call.model')
#
# train_call_model()
#
#
# # In[7]:
#
# def train_raise_model():
#     model_raise_pool = ModelPool(len(names), model_dir + 'pool/raise/')
#     idx = y['private_bot_action'] != 'FOLD'
#     y_raise = y[idx]['private_bot_action'].replace({'CALL': 0, 'RAISE': 1})
#     X_raise = model_raise_pool.predict(X[idx])
#
#     X_train, X_test, y_train, y_test = train_test_split(X_raise, y_raise, test_size=0.1, random_state=1234)
#
#     model = CatBoostClassifier(iterations=200, learning_rate=0.1, depth=2, thread_count=4,
#                                    verbose=True, use_best_model=True)
#     model.fit(X_train, y_train, eval_set=(X_test, y_test))
#     model.save_model(model_dir + 'raise.model')
#
# train_raise_model()
#
#
# # In[8]:
#
# def train_raise_amount_model():
#     model_raise_amount_pool = ModelPool(len(names), model_dir + 'pool/raise_amount/', classifier=CatBoostRegressor)
#     idx = y['private_bot_action'] == 'RAISE'
#     y_raise = y[idx]['private_bot_action_amount']
#     X_raise = model_raise_amount_pool.predict(X[idx])
#
#     X_train, X_test, y_train, y_test = train_test_split(X_raise, y_raise, test_size=0.1, random_state=1234)
#
#     model = CatBoostRegressor(iterations=200, learning_rate=0.1, depth=2, thread_count=4,
#                                    verbose=True, use_best_model=True)
#     model.fit(X_train, y_train, eval_set=(X_test, y_test))
#     model.save_model(model_dir + 'raise_amount.model')
#
# train_raise_amount_model()


# TRAIN POOLS

#In[3]:

def train_call_models():
    for i, name in enumerate(names):
        print(i, name)
        y_bot = y[y['private_bot_name'] == name]
        X_game = X.loc[y_bot.index]
        y_game = y_bot['private_bot_action'].replace({'FOLD': 0, 'CALL': 1, 'RAISE': 1})

        X_train, X_test, y_train, y_test = train_test_split(X_game, y_game, test_size=0.1, random_state=1234)

        model = CatBoostClassifier(iterations=200, learning_rate=0.1, depth=8, thread_count=4,
                                   verbose=True, use_best_model=True)
        model.fit(X_train, y_train, eval_set=(X_test, y_test))

        model.save_model(model_dir + 'pool/call/' + str(i) + '.model')

train_call_models()


# In[4]:

def train_raise_models():
    for i, name in enumerate(names):
        print(i, name)
        y_bot = y[(y['private_bot_name'] == name) & (y['private_bot_action'] != 'FOLD')]
        X_game = X.loc[y_bot.index]
        y_game = y_bot['private_bot_action'].replace({'CALL': 0, 'RAISE': 1})

        X_train, X_test, y_train, y_test = train_test_split(X_game, y_game, test_size=0.1, random_state=1234)

        if len(y_game.value_counts()) == 1:
            y_train.iloc[0] = 0
            y_train.iloc[1] = 1
            y_test.iloc[0] = 0
            y_test.iloc[1] = 1

        model = CatBoostClassifier(iterations=200, learning_rate=0.1, depth=8, thread_count=4,
                                   verbose=True, use_best_model=True)
        model.fit(X_train, y_train, eval_set=(X_test, y_test))

        model.save_model(model_dir + 'pool/raise/' + str(i) + '.model')

train_raise_models()


# In[5]:

def train_raise_amount_models():
    for i, name in enumerate(names):
        print(i, name)
        y_bot = y[(y['private_bot_name'] == name) & (y['private_bot_action'] == 'RAISE')]
        X_game = X.loc[y_bot.index]
        y_game = y_bot['private_bot_action_amount']

        X_train, X_test, y_train, y_test = train_test_split(X_game, y_game, test_size=0.1, random_state=1234)

        model = CatBoostRegressor(iterations=200, learning_rate=0.1, depth=8, thread_count=4,
                                   verbose=True, use_best_model=True)
        model.fit(X_train, y_train, eval_set=(X_test, y_test))

        model.save_model(model_dir + 'pool/raise_amount/' + str(i) + '.model')

train_raise_amount_models()

