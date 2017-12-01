#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
import sqlite3

# read sqlite query results into dataframe
con = sqlite3.connect('data/bgg.sqlite')
df_all = pd.read_sql_query('SELECT * from boardgames', con)
con.close()

# create working dataframe with fields of interest
df_games = df_all.loc[:,(
    'game.id','game.type', 
    'details.name', 'details.description',  'details.yearpublished','details.maxplayers', 'details.minplayers', 'details.minage', 'details.maxplaytime', 'details.minplaytime', 'details.playingtime',
    'attributes.boardgamecategory', 'attributes.boardgamemechanic', 'attributes.boardgamepublisher',
    'stats.averageweight', 'stats.average')]
numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
df_num = df_games.select_dtypes(include=numerics)
df_num = df_num.dropna(axis=0, how='any')
df_num_var = list(df_num)
graphs = len(df_num_var)-1

# create array with positions for charting
position = []
for i in range(4):
    for j in range(2):
        b = i,j
        position.append(b)

# subplots filled in and charted
fig, axes = plt.subplots(nrows=4, ncols=2, sharey=False, sharex=False, figsize=(8,12))
fig.subplots_adjust(hspace=0.25)
for i in range(graphs):
    sns.distplot(df_num[df_num_var[i]], ax=axes[position[i]], kde=False)

# collect statistics for each quantitative detail and render outliers
for field in df_num_var:
    value_mean = df_games[field].median()
    value_q1 = df_games[field].quantile(0.25)
    value_q3 = df_games[field].quantile(0.75)
    value_qrange = value_q3-value_q1
    lower_outlier = value_q1-(4.5 * value_qrange)
    upper_outlier = value_q3+(4.5 * value_qrange)
    print(field)
    print(len(df_games[df_games[field]>upper_outlier]), 'upper outliers at', upper_outlier)
    print(len(df_games[df_games[field]<lower_outlier]), 'lower outliers at', lower_outlier, '\n')

# correlation and heatmap
fig, ax = plt.subplots(figsize=(6,5))
corr = df_games.corr()
corr = (corr)
sns.heatmap(corr, xticklabels=corr.columns.values, yticklabels=corr.columns.values, linewidths=0.5, ax=ax)
corr['stats.average'].sort_values(ascending=False)