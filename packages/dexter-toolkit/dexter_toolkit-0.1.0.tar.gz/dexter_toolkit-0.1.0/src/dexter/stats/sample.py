"""
Script Name: sample.py
Author: Deniz
Created: 2024-05-22 22:05:13
Description: Script Description
"""


from .utils import *

class Sample:
    def __init__(self, rvs:list["RV"]):
        self.rvs = rvs

    @property
    def expected_value(self, trials=120):
        return np.mean([np.mean(self.observe()) for i in range(trials)])

    def observe(self):
        return np.array([rv.observe() for rv in self.rvs])

    def __str__(self):
        return []
