import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import math
from pylab import *


ko = []
wt = []

ko_headers = ['a', 'b', 'c', 'd']
wt_headers = ['e', 'f', 'g']

df = pd.read_excel('areas.xlsx')

for i in range(4):
    x = df[ko_headers[i]]
    x.dropna(axis='rows', inplace=True)
    series_list = list(x)
    for element in series_list:
        ko.append(element)

for j in range(3):
    x = df[wt_headers[j]]
    x.dropna(axis='rows', inplace=True)
    series_list = list(x)
    for element in series_list:
        wt.append(element)

print(len(ko), len(wt))
ko = pd.Series(ko)
wt = pd.Series(wt)


font = {'fontname': 'Arial'}
fig, ax = plt.subplots(figsize=(16,9))

plt.hist(wt, bins=34, color='#656565', alpha=.6, density=True, label='WT')
wt.plot(kind='kde', label='WT KDE', color='#656565', alpha=1)

plt.hist(ko, bins=34, color='#6d1b7b', alpha=0.6, density=True, label = 'KO')
ko.plot(kind='kde', label='KO KDE', color='#6d1b7b', alpha=1)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_visible(True)
ax.spines['left'].set_visible(True)

plt.xlim(-0.02, 1)
plt.xlabel('Density of GFAP', fontsize=20, **font)
plt.ylabel('Frequency', fontsize=20, **font)
plt.title('Distribution of Retinal GFAP Density', fontsize=24, **font)
plt.xticks(fontsize=18)
ax.tick_params(axis='both', which='major', labelsize=18)
ax.tick_params(axis='both', which='minor', labelsize=18)


ax.legend(fontsize=18)
plt.show()


