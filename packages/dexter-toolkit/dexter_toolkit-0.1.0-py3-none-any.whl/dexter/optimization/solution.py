#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 30 17:16:19 2024

@author: deniz
"""

import numpy as np
import pyomo.environ as pyo

class Solution:
    def __init__(self, variables:list[str], values:list[float|int]):
        self.variables = variables
        self.values = values
        self.basis = [i for i in range(len(self.values)) if self.values[i] > 0]

    @classmethod
    def from_dict(cls, map_dict):
        return cls(list(map_dict.keys()), list(map_dict.values()))
    
    def __str__(self):
        vars_str = ",".join(var for var in self.variables)
        values_str = ",".join(str(val) for val in self.values)
        return f"({vars_str}) = ({values_str})"

    def __getitem__(self, ind:int|str) -> float:
        match ind:
            case str():
                return self.variables.index(ind)
            case int():
                return self.values[ind]

    def feasibility(self):
        # Check the feasibility of solution
        feasible = True
        for value in value:
            if value < 0:
                feasible = False

        return feasible

    def optimality(self):
        # Check the optimality of the solution
        pass

    def validate(self):
        # Ensure solution is feasible
        # Compute value for the solution parameters
        
        pass

    def to_numpy_array(self) -> np.array:
        return np.array(self.values)