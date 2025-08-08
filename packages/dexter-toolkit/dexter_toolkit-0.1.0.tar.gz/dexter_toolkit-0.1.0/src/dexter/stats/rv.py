"""
Script Name: rv.py
Author: Deniz
Created: 2024-05-15 14:33:20
Description: Random variable class that supports abstract r.v.s,
Variables a
"""

class RV:
    _ids = 0

    def __init__(self, distribution:"Distribution"=None, name=None):
        RV._ids += 1

        self._id = RV._ids
        self.distribution = distribution
        self.name = name if name else self._id

        # actually either a pdf and support, OR the distribution is required

    @property
    def expected_value(self):
        return self.distribution.expectation

    def observe(self):
        return self.distribution.dist.rvs()
    
    def __add__(self, other):
        lhs, rhs = self.distribution, other.distribution
        match (lhs, rhs):
            case (None, None):
                pass
            case _:
                return RV(lhs.__add__(rhs)) # can be wrong
            

    def __str__(self):
        return self.name
    

if __name__ == "__main__":
    from distribution import Binomial
    
    X = RV(Binomial(10, 0.4))
    print(X.expected_value)