"""
Script Name: test_eq.py
Author: Deniz
Created: 2024-08-18 20:00:09
Description: Script Description
"""


import unittest
from equation import Equation


class TestRV(unittest.TestCase):
    def test_parsing_1(self):
        eq = Equation("2*x + 5*y + 3*z_1 >= 5", name="example")

        """Check initialization"""
        self.assertIsInstance(eq, Equation)
        self.assertEqual(eq.name, "example")

        """Check variable and coefficient read"""

        self.assertDictEqual(eq.var_to_coef, {"x": 2, "y": 5, "z_1": 3})


    def test_parsing_2(self):
        import numpy as np

        """choosing 10 random coefficients, and creting the equation string"""
        eq_str = ""
        rand_coefs = np.linspace(1, 20, 10)
        i = 1
        for coef in rand_coefs:
            eq_str += f"{round(coef)}*x_{i}"
            if i < 10:
                eq_str += " + "
            else:
                eq_str += " <= 250"
            i += 1
        """Testing equation"""
        eq = Equation(eq_str)

        self.assertDictEqual(eq.var_to_coef, {f"x_{i}":round(rand_coefs[i-1]) for i in range(1, 11)})


    def test_invalid_operator(self):
        with self.assertRaises(ValueError):
            Equation("x === 5")


    def test_incomplete_equation(self):
        import sympy
        with self.assertRaises(sympy.SympifyError):
            Equation("3*x_1 + 5*x_2 + ")


if __name__ == '__main__':
    unittest.main()