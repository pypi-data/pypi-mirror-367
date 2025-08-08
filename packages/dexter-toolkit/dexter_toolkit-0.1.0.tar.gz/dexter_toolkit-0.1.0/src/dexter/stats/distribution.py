"""
Script Name: distribution.py
Author: Deniz
Created: 2024-05-10 20:34:05
Description: Abstract distributions
"""

import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)


from .utils import *

# Everything assumes independence

class Distribution:
    
    def plot_pdf(self):
        pass

    def plot_cdf(self):
        pass

    def draw(self, n=1):
        from .rv import RV
        from .sample import Sample

        if n==1:
            return RV(distr=self)
        else:
            return Sample([RV(distr=self) for i in range(n)])
        
    def __add__(self, other):
        pass # CONTINUE for identically distributed r.v.s


class Normal(Distribution):
    def __init__(self, mean:float, var:float):
        self.mean = mean
        self.var = var
        self.std = np.sqrt(self.var) #Add Handling negative variance
        self.dist = sci.norm(loc=self.mean, scale=self.std)
        self.support = (-np.inf, np.inf)

    def __str__(self):
        return f"N(mean={self.mean}, variance={self.var})"
    
    def pdf(self, x):
        return self.dist.pdf(x)
    
    def cdf(self, x):
        return self.dist.cdf(x)
    
    def mgf(self, t):
        return self.dist.mgf(t)
    
    def __add__(self, other):
        lhs, rhs = self.distribution, other.distribution
        match rhs.distribution:
            case Normal():
                return Normal(self.mean + other.mean, self.var + other.var)

    def __mul__(self, other):
        if not isinstance(other, (float, int)):
            raise NotImplementedError("Hard stuff")
        
        self.mean *= other
        self.var *= other**2

class Uniform(Distribution):
    def __init__(self, a, b):
        self.a, self.b = a, b
        self.E = (self.a+self.b)/2
        self.dist = sci.uniform(loc=a, scale=b-a)
    
    def pdf(self, x):
        return self.dist.pdf(x)
    
    def cdf(self, x):
        return self.dist.cdf(x)
    
    def mgf(self, x):
        return self.dist.mgf(x)


class Binomial(Distribution):
    def __init__(self, n:int, p:float):
        self.n = n
        self.p = p
        self.dist = sci.binom(n=self.n, p=self.p)
        self.expectation = self.n * self.p

    def pdf(self, x):
        return self.dist.pmf(x)
    
    def cdf(self, x):
        return self.dist.cdf(x)
    
    def __add__(self, other):
        lhs, rhs = self, other
        print("Binomial Addition")
        match rhs:
            case Binomial() if lhs.p == rhs.p: # Case Binomial doesn't
                return Binomial(n=lhs.n+rhs.n, p=lhs.p)
                # check whether it's true also consider the case of unequal p's


class Geometric(Distribution):
    def __init__(self, p):
        self.p = p
        self.dist = sci.geom(p)
        self.expectation = 1/self.p

    def pdf(self, x):
        return self.dist.pmf(x)
    
    def cdf(self, x):
        return self.dist.cdf(x)
    
    def __add__(self, other):
        lhs, rhs = self, other
        print("Geometric Addition")

        match rhs:
            case Poisson() if lhs.p == rhs.p:
                return NegativeBinomial(r=2, p=lhs.p)
            
            ##


class NegativeBinomial(Distribution):
    def __init__(self, r, p):
        self.r = r
        self.p = p
        self.dist = sci.nbinom(self) # Need to refine the parameters for passing to nbinom

    def pdf(self, x):
        return self.dist.pmf(x)
    
    def cdf(self, x):
        return self.dist.cdf(x)


class Poisson(Distribution):
    def __init__(self, mu):
        self.mu = mu
        self.dist = sci.poisson(mu)
        self.expectation = self.mu

    def pdf(self, x):
        return self.dist.pmf(x)
    
    def cdf(self, x):
        return self.dist.cdf(x)
    
    def __add__(self, other):
        lhs, rhs = self, other
        print("Poisson Addition")
        match rhs:
            case Poisson():
                return Poisson(mu=lhs.mu + rhs.mu)


class Exponential(Distribution):
    def __init__(self, intensity: float):
        self.intensity = intensity
        self.dist = sci.expon(scale=1/intensity)
        self.expectation = 1/self.intensity

    def pdf(self, x):
        return self.dist.pdf(x)
    
    def cdf(self, x):
        return self.dist.cdf(x)
    
    def __add__(self, other):
        lhs, rhs = self, other
        print("Exponential Addition")

        match rhs:
            case Exponential() if lhs.intensity == rhs.intensity:
                return Gamma(1/lhs.intensity, 2)
            
            # Check the one below
            case Gamma() if lhs.intensity == 1/rhs.theta:
                return Gamma(rhs.theta, rhs.r + 1)

    def mgf(self, t):
        return self.intensity / (self.intensity - t)


class Gamma(Distribution):
    def __init__(self, theta, r:int):
        self.theta = theta
        self.r = r
        self.dist = sci.gamma(0, 1) # Change the parameters

    def pdf(self, x) -> float:
        return self.dist.pdf(x)
    
    def cdf(self, x) -> float:
        return self.dist.cdf(x)
    
    def __add__(self, other):
        match other.distribution:
            case Gamma() if self.theta == other.theta:
                # Wouldn't it be fancy to check with case Gamma(self.intensity)
                return Gamma(theta=self.theta, r=self.r + other.r)
            
class ChiSquare(Distribution):
    def __init__(self, df:int):
        self.df = df
        self.dist

    def pdf(self, x) -> float:
        return self.dist
            

class Unknown(Distribution):
    def __init__(self, mean:float, variance:float, pdf:"function"):
        self.mean = mean
        self.variance = variance
        self.pdf = pdf


Distr = Distribution
N = Normal

