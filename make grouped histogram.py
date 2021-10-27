import pandas as pd
import matplotlib.pyplot as plt
import statistics
import math
import scipy.stats as stats

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

ko = pd.Series(ko)
wt = pd.Series(wt)

fig, ax = plt.subplots(figsize=(14, 8), dpi=100)

plt.hist(wt, bins=34, color='#656565', alpha=0.6, density=True, label='WT')
plt.hist(ko, bins=34, color='#6d1b7b', alpha=0.7, density=True, label='KO')

font = {'fontname': 'Arial'}

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_visible(True)
ax.spines['left'].set_visible(True)

for axis in ['top', 'bottom', 'left', 'right']:
    ax.spines[axis].set_linewidth(1.5)

ax.tick_params(width=2, length=7)
plt.xticks(fontsize=18)
ax.tick_params(axis='both', which='major', labelsize=18)
ax.tick_params(axis='both', which='minor', labelsize=18)

plt.xlim(-0.02, 1)
plt.xlabel('Density of GFAP', fontsize=24, **font)
plt.ylabel('Normalized Frequency', fontsize=24, **font)
plt.title('Distribution of Retinal GFAP Density', fontsize=36, **font)
ax.legend(fontsize=20, frameon=True, framealpha=1, edgecolor='none')

# Inset Plot
inset = plt.axes([.55, .40, .35, .35], facecolor='white')
inset.spines['top'].set_visible(False)
inset.spines['right'].set_visible(False)
inset.spines['bottom'].set_visible(True)
inset.spines['left'].set_visible(True)

for axis in ['top', 'bottom', 'left', 'right']:
    inset.spines[axis].set_linewidth(1.2)

wt.plot(kind='kde', label='WT KDE', color='#656565', alpha=1)
ko.plot(kind='kde', label='KO KDE', color='#6d1b7b', alpha=1)

inset.tick_params(width=1.5, length=5)
inset.tick_params(axis='both', which='major', labelsize=13)
inset.tick_params(axis='both', which='minor', labelsize=13)

plt.xlim(-0.02, 1)
plt.xlabel('', fontsize=15, **font)
plt.ylabel('', fontsize=15, **font)

plt.show()

# Z statistic
ko_mean = statistics.mean(ko)
wt_mean = statistics.mean(wt)
ko_sd = statistics.stdev(ko)
wt_sd = statistics.stdev(wt)

Z = (wt_mean - ko_mean) / (math.sqrt((ko_sd ** 2) + (wt_sd ** 2)))
print(Z)


def mann_whitney_u_test(distribution_1, distribution_2):
    """
    Perform the Mann-Whitney U Test, comparing two different distributions.
    Args:
       distribution_1: List.
       distribution_2: List.
    Outputs:
        u_statistic: Float. U statisitic for the test.
        p_value: Float.
    """
    u_statistic, p_value = stats.mannwhitneyu(distribution_1, distribution_2)
    return u_statistic, p_value


#### MAIN FUNCTION ####
# Perform the Mann-Whitney U Test on the two distributions
print(mann_whitney_u_test(wt, ko))
