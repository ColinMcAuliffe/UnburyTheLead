import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.special import logit,expit
import pymc3 as pm
import theano.tensor as tt
sns.set(color_codes=True)

def hierarchical_normal(name, shape, mu=0.,scale=1.):
    delta = pm.Normal('delta_{}'.format(name), 0., 1., shape=shape)
    sigma = pm.HalfNormal('sigma_{}'.format(name), sd=scale)
    
    return pm.Deterministic(name, mu + delta * sigma)

SEED = 4260026 
np.random.seed(SEED)

#Generate fake data
#Group 1, 4 members
mu1,sd1 = 0.5,.2
p1 = expit(np.random.normal(loc=mu1,scale=sd1,size=4))
g1 = [0]*4
#Group 2, 4 members
mu2,sd2 = 1.5,.5
p2 = expit(np.random.normal(loc=mu2,scale=sd2,size=4))
g2 = [1]*4
#Group 3, 4 members
mu3,sd3 = 0.0,.1
p3 = expit(np.random.normal(loc=mu3,scale=sd3,size=4))
g3 = [2]*4
#Group 4, 4 members
mu4,sd4 = -.5,.4
p4 = expit(np.random.normal(loc=mu4,scale=sd4,size=4))
g4 = [3]*4
#Group 5, 1 member
mu5,sd5 = 0.0,.4
p5 = expit(np.random.normal(loc=mu5,scale=sd5,size=1))
g5 = [4]

probs  = np.concatenate((p1,p2,p3,p4,p5))
groups = np.concatenate((g1,g2,g3,g4,g5))

n   = 100
N   = np.ones(np.size(probs))*n
obs = np.array([np.random.binomial(n,p) for p in probs])

nIndiv   = len(N)
indivIdx = np.array(range(nIndiv))

print obs

NUTS_KWARGS = {'target_accept': 0.99,'max_treedepth':30}

ndraws = 1000
ntune  = 500


skip = np.ones((nIndiv,), dtype=int)
skip[nIndiv-1] = 0
with pm.Model() as model:
    #Baseline intercept
    a0   = pm.Normal('baseline',mu=0.,sd=5.)

    #group level predictors
    a_group       = hierarchical_normal('group',5)
    mu_individual = a_group[groups]
    
    sigma_indiv_upp = pm.HalfNormal('sigma_individual_upper', sd=1.)
    sigma_indiv     = pm.HalfNormal('sigma_individual',sd=sigma_indiv_upp,shape=5)
    delta = pm.Normal('delta_individual', 0., 1.,shape=nIndiv)
    a_individual = pm.Deterministic('individual', a_group[groups] + delta * sigma_indiv[groups]*skip)
    #a_individual = []
    #for i in range(nIndiv):
    #    if i in skip:
    #        a_individual.append(pm.Deterministic('individual_{}'.format(i), mu_individual[i]))
    #    else:
    #        delta = pm.Normal('delta_individual_{}'.format(i), 0., 1.)
    #        a_individual.append(pm.Deterministic('individual_{}'.format(i), mu_individual[i] + delta * sigma_indiv[groups[i]]))
    #a_individual = tt.as_tensor_variable(a_individual)
    

    eta        = a0 + a_individual[indivIdx]
    p          = pm.math.sigmoid(eta)
    likelihood = pm.Binomial("obs",N,p,observed=obs)

    trace = pm.sample(draws=ndraws,tune=ntune,njobs=3, random_seed=SEED,nuts_kwargs=NUTS_KWARGS)

    plt.figure()
    hcp5  = pm.HalfNormal.dist(sd=1.)
    axs = pm.traceplot(trace,varnames=["sigma_group","sigma_individual","sigma_individual_upper"],priors=[hcp5,hcp5,hcp5])
    plt.savefig("TraceV.png")
    plt.close()

plt.figure()
s = sns.jointplot(trace["group"][:,-1],trace["individual"][:,-1])
plt.savefig("Correlation.png")

plt.figure()
axs = pm.forestplot(trace,varnames=["sigma_individual"])
plt.savefig("forest.png")
plt.close()
    
plt.figure()
axs = pm.traceplot(trace)
plt.savefig("Trace.png")
plt.close()

