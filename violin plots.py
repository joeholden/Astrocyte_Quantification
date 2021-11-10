import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import math
import seaborn as sns


Young_KO = []
Young_WT = []

ko_headers = ['a', 'b', 'c']
wt_headers = ['d', 'e', 'f']

df = pd.read_excel('areas.xlsx')

for i in range(3):
    x = df[ko_headers[i]]
    x.dropna(axis='rows', inplace=True)
    series_list = list(x)
    for element in series_list:
        Young_KO.append(element)

for j in range(3):
    x = df[wt_headers[j]]
    x.dropna(axis='rows', inplace=True)
    series_list = list(x)
    for element in series_list:
        Young_WT.append(element)

Young_KO = pd.Series(Young_KO)
Young_WT = pd.Series(Young_WT)

# ////////////////////////////////////////////////////////////////
Old_KO = []
Old_WT = []

ko_headers_ = ['a', 'b', 'c', 'd']
wt_headers_ = ['e', 'f', 'g']

df = pd.read_excel('areas old.xlsx')

for i in range(4):
    x = df[ko_headers_[i]]
    x.dropna(axis='rows', inplace=True)
    series_list = list(x)
    for element in series_list:
        Old_KO.append(element)

for j in range(3):
    x = df[wt_headers_[j]]
    x.dropna(axis='rows', inplace=True)
    series_list = list(x)
    for element in series_list:
        Old_WT.append(element)

Old_KO = pd.Series(Old_KO)
Old_WT = pd.Series(Old_WT)

# //////////////////////////////////////////////////////////////

font = {'fontname': 'Arial'}

data_set = [Young_WT, Young_KO, Old_WT, Old_KO]
color_set = ['#555555', '#6d1bAb', '#A9A9A9', '#CA09BC']
# color_set = ['#6d1bAb', '#CA09BC', '#3535F5', '#3995D3']

df = pd.DataFrame(data_set).transpose()
df.columns = ['Young WT', 'Young KO', 'Old WT', 'Old KO']

fig, axes = plt.subplots(figsize=(10,7))
sns.set(style="whitegrid")
plot = sns.violinplot(data=df, ax = axes, orient ='h', palette=color_set)
plt.setp(axes.collections, alpha=.8)

sns.despine()

plt.title('Retinal GFAP Density Distributions', fontsize=18, **font)
plt.xlabel('Density of GFAP', fontsize=15, **font)
plt.ylabel('', **font)

plot.set_yticklabels(df.columns)
plt.xticks(fontsize=12, **font)
plt.yticks(fontsize=15)
plt.tick_params(width=1.1, length=7)

plt.setp(axes.spines.values(), linewidth=1.1)
plt.show()




