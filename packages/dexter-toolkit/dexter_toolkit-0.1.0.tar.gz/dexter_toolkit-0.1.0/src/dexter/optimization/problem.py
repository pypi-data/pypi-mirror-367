#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 14 20:32:12 2024

@author: deniz
"""

import numpy as np
import pyomo.environ as pyo
import re

from .equation import Equation
from .solution import Solution

class SolverNotInstalled(Exception): pass
class UnrecognizedTerm(Exception): pass


class Problem:

    def __init__(self, objective:str, constraints:list[str], solver="glpk"):
        self.model = self.construct_model(objective, constraints)

        try:
            self.solver = pyo.SolverFactory(solver)
        except:
            raise SolverNotInstalled


    def __str__(self):
        return self.definition
    

    def __repr__(self):
        return f"Problem(objective={self.objective!r}, constraints={self.constraints})"
    

    def construct_model(self, objective, constraints) -> pyo.ConcreteModel:
        model = pyo.ConcreteModel()

        obj_split = re.split(r"(?<=^m[a-zA-Z]{2})", objective.lower(), maxsplit=1)
        goal, objective_equation = obj_split[0], obj_split[1] ###CHANGE GOAL

        self.objective = Equation(objective_equation, name=f"objective {goal}")

        self.constraints = [Equation(c, f"constraint {str(i)}") for i, c in enumerate(constraints)]
        self.constraint_matrix = np.vstack([const.to_numpy_array() for const in self.constraints])
        self.definition = str(self.objective) + "\n" + "\n".join(str(constraint) for constraint in self.constraints)

        #Do the following conversion from equation to pyomo constraint
        #in the Equation classes method instead of doing here
        set_vars = set()
        for eq in self.constraints:
            for var in eq.variables:
                set_vars.add(var)

        self.variables = sorted(set_vars)

        for var in self.variables:
            setattr(model, var, pyo.Var(domain=pyo.NonNegativeReals))

        obj_expr = re.sub(r"([a-zA-Z])", r"*model.\1", self.objective.expr)
        model.objective = pyo.Objective(expr=eval(obj_expr), sense=eval(f"pyo.{goal}imize"))

        for eq in self.constraints:
            expr = re.sub(r"([a-zA-Z])", r"*model.\1", eq.expr)
            expr = re.sub(r"(?<![\><=])=", "==", expr)
            setattr(model, eq.name.replace(" ", "_"), pyo.Constraint(expr=eval(expr)))

        return model
    
            
    def solve(self) -> "Solution":
        self.solver.solve(self.model)

        optimal_solution = {}
        print("--------- OPTIMAL VALUES ---------")

        for variable in self.variables:
            optimal_val = getattr(getattr(self.model, variable), "value")
            print(f"{variable}:", optimal_val)
            optimal_solution[variable] = optimal_val

        [print("--------------------------------")]

        self.solution = Solution.from_dict(optimal_solution)

        return self.solution
    

    def __call__(self, solution:"Solution or dict"):
        if isinstance(solution, dict):
            solution = Solution(solution)
            # Add try except for other types of variables        

        value = np.sum(self.objective.to_numpy_array() * solution.to_numpy_array())
        return value
    

    def sensitivity(self, b_i:int, solution:"Solution or dict"=None):
        match solution:
            case dict():
                solution = Solution(solution)
            case None:
                solution = getattr(self, "solution", self.solve())
            case Solution():
                pass
            case _:
                raise UnrecognizedTerm("Unrecognized Solution format")
        
        basis = solution.basis

        A_basic = self.constraint_matrix[:, basis]
        A_inv = np.linalg.inv(A_basic)
        beta_i = A_inv[:, b_i]

        c_basic = self.objective.to_numpy_array()[basis]
        basic_value = np.sum(c_basic * solution.to_numpy_array()[basis])

        low_bounds, up_bounds = [], []
        decide_append = lambda beta_ij: low_bounds.append(boundary) if beta_ij > 0 else up_bounds.append(boundary)
        for j in range(len(beta_i)):
            print(beta_i[j])
            boundary = round(-solution[j]/beta_i[j], 2)
            print(boundary)
            decide_append(boundary)

        print("Solution remains in the optimal basis while")
        print(f"Delta is within the range: [{max(low_bounds)}, {min(up_bounds)}]")

        # fix the inverted places

        
        return

