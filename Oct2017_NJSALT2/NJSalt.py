
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.ticker import FormatStrFormatter
from matplotlib.ticker import MaxNLocator
import seaborn as sns
sns.set(color_codes=True)

df = pd.read_csv("15zp31nj.csv",dtype={"Zip":object})

df = df[~df["Zip"].isnull()]
df = df[df["Categoty"].isnull()]


df = df[["Zip","(1)","(17)","(62)","(63)","(64)","(65)","(66)","(67)"]]

cols = ["(1)","(17)","(62)","(63)","(64)","(65)","(66)","(67)"]
for col in cols:
    df[col] = df[col].str.replace(",","")
    df[col] = df[col].astype(np.float64)

df["IncomePC"] = df["(17)"]/df["(1)"]
df["IncomePCL"] = np.log(df["IncomePC"])
df["SALTPC"] = (df["(63)"] + df["(65)"] + df["(67)"])/df["(1)"]


print df.sort_values("IncomePC")
#g.axvline(df["IncomePC"].mean(),color='r')
#g.axvline(np.exp(df["IncomePCL"].mean()),color='g')
plt.figure()
percentiles = [50,60,70,80,90,99,99.9]
colors = [plt.cm.jet(i) for i in np.linspace(0, 1, len(percentiles))]

g = sns.distplot(df["IncomePC"],kde=False)
ps = np.percentile(df["IncomePC"],percentiles)
for p,pl,c in zip(ps,percentiles,colors):
    g.axvline(p,color=c,label=str(pl)+"th")
lgd = g.legend(title="Percentiles:",bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
g.set_xlabel("Total Income per Capita in NJ Zip Codes, Thousands of Dollars")
g.set_ylabel("Number of NJ Zip Codes")
plt.savefig("IncomeDist.png", bbox_extra_artists=(lgd,), bbox_inches='tight')

plt.figure()
g = sns.jointplot("IncomePC","SALTPC",data=df,kind='reg')
g.ax_joint.set_xlim((0.,800.))
g.ax_joint.set_ylim((0.,100.))

g.ax_joint.set_xlabel("Income per Capita, Thousands of Dollars")
g.ax_joint.set_ylabel("SALT Deductions per Capita, Thousands of Dollars")

plt.savefig("IncomeVsSALT.png")
