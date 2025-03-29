import numpy as np
from scipy.optimize import minimize


def annualize_rets(r, num_per_year):
    price = (1+r).prod()
    n = r.shape[0]
    return price**(num_per_year/n)-1

def portfolio_return(weights, returns):
    return weights.T @ returns

def portfolio_returns(weights, returns):
    return returns @ weights


def portfolio_vol(weights, cov):
    vol = (weights.T @ cov @ weights)**0.5
    return vol

def maximize_ret(target_vol, er, cov, bounds):

    n = er.shape[0]
    init_guess = np.repeat(1/n, n)
    bounds = bounds

    constr_sum = {'type': 'eq',
                        'fun': lambda weights: np.sum(weights) - 1
    }

    constr_vol = {'type': 'ineq',
                        'args': (cov,),
                        'fun': lambda weights, cov: target_vol - portfolio_vol(weights, cov)
    }

    def neg_portfolio_return(weights, returns):
        return - portfolio_return(weights, returns)

    weights = minimize(neg_portfolio_return, init_guess,
                       args=(er,), method='SLSQP',
                       options={'disp': False},
                       constraints=(constr_sum,constr_vol),
                       bounds=bounds)
    return weights.x
