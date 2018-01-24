#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
import sqlite3

# read sqlite query results into a pandas dataframe
con = sqlite3.connect('data/bgg.sqlite')
df_all = pd.read_sql_query('SELECT * from boardgames', con)
con.close()

# create working dataframe with fields of interest
df_games = df_all.loc[:,(
    'game.id','game.type',
    'details.name', 'details.description',  'details.yearpublished', 'details.maxplayers', 'details.minplayers', 'details.minage', 'details.maxplaytime', 'details.minplaytime', 'details.playingtime',
    'attributes.boardgamecategory', 'attributes.boardgamemechanic', 'attributes.boardgamepublisher',
    'stats.averageweight', 'stats.average')]

# build new dataframe with just id and category, filling empties with NaN, breaking out comma separated categories
df_category = df_games.loc[:, ['game.id','attributes.boardgamecategory']]
df_category['attributes.boardgamecategory'] = df_category['attributes.boardgamecategory'].fillna("None")
df_category = df_category['attributes.boardgamecategory'].apply(lambda x: pd.Series(x.split(',')))

category_counts = df_category.apply(pd.Series.value_counts).fillna(0)
category_counts['Total'] = category_counts.sum(axis=1)
category_counts = category_counts.sort_values(by='Total', ascending=False)
category_list = category_counts[category_counts['Total']>1000].index.tolist()

df_games['attributes.boardgamecategory'].fillna(0, inplace=True)
for i in category_list:
    df_games.loc[df_games['attributes.boardgamecategory'].str.contains(i) == True, i] = 1
    df_games.loc[df_games['attributes.boardgamecategory'].str.contains(i) == False, i] = 0
    df_games[i].fillna(0, inplace=True)

d = []
for i in category_list:
    score = df_games[df_games[i]==1]['stats.average'].mean()
    d.append({'Avg_Rating': score, 'Game Type': i})
df_categorymean = pd.DataFrame(d).sort_values(by='Avg_Rating', ascending=False)
df_categorymean[:10]

fig, (ax1, ax2) = plt.subplots(nrows=2, sharey=True, sharex=False, figsize=(12,6))
fig.subplots_adjust(hspace=1.0)
sns.set_style("whitegrid")
sns.barplot(x='Game Type', y='Avg_Rating', data=df_categorymean[:15], ax=ax1, palette="muted")
sns.barplot(x='Game Type', y='Avg_Rating', data=df_categorymean[-15:], ax=ax2, palette="muted")
ax1.title.set_text('Highest rated game categories')
ax1.set_xticklabels(ax1.get_xticklabels(), rotation=90)
ax2.title.set_text('Lowest rated game categories')
ax2.set_xticklabels(ax2.get_xticklabels(), rotation=90)