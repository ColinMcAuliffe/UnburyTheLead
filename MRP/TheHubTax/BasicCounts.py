import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy as sp
import seaborn as sns
from scipy.special import logit,expit
sns.set(color_codes=True)

import us

def joinFig(name):
    return os.path.join("Figures",name)

df = pd.read_csv(os.path.join("GSG Tax Survey - April 2017 - National","TheHub.csv"))
df = df[df["S1"]==1]
print df

plt.figure()
ax = sns.countplot(x="D101",data=df)
plt.savefig(joinFig("Count_AgeCat.png"))
plt.close()

plt.figure()
ax = sns.countplot(x="D100",data=df)
plt.savefig(joinFig("Count_Gender.png"))
plt.close()

plt.figure()
ax = sns.countplot(x="D300",data=df)
plt.savefig(joinFig("Count_Race.png"))
plt.close()

plt.figure()
ax = sns.countplot(x="D102",data=df)
plt.savefig(joinFig("Count_Education.png"))
plt.close()

plt.figure()
ax = sns.countplot(x="D900",data=df)
plt.savefig(joinFig("Count_Income.png"))
plt.close()

plt.figure()
ax = sns.countplot(x="BAT5R1",data=df)
plt.savefig(joinFig("Count_CorpCut.png"))
plt.close()
