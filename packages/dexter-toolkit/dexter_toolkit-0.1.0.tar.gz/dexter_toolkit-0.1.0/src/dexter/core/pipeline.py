"""
Script Name: pipeline.py
Author: Deniz
Created: 2024-06-18 13:21:28
Description: Script Description
"""


class Pipeline: # Extend a regarded pipeline structure
    def __init__(self, processes=None):
        self.processes = processes # Maybe keep them in a dict with names?
        self.inputs = {}
        self.results = {} # result of operations

    def run(self):
        i = 0
        while i < len(self.processes) - 1:
            self.results[f"step_{i}"] = self.processes[i](self.inputs)

    def step(self, i=None):
        processes = self.processes[i] if i else self.processes[0]
