"""
Script Name: sim_manager.py
Author: Deniz
Created: 2024-06-18 22:29:59
Description: Sim Manager for dynamic sim
"""



import simpy
import random

class SimManager:
    def __init__(self, env=None):
        self.env = env if env else simpy.Environment()
        self.resources = {}
        self.processes = {}
        self.active_processes = {}
        self.simulation_running = True
        self.step_mode = False

    def add_resource(self, name, resource):
        self.resources[name] = resource

    def add_process(self, name, process_func):
        self.processes[name] = process_func

    def activate_process(self, name, *args, **kwargs):
        if name not in self.processes:
            raise ValueError(f"Process {name} does not exist.")
        
        process_func = self.processes[name]
        process = self.env.process(process_func(self.env, *args, **kwargs))
        self.active_processes[name] = process

    def deactivate_process(self, name):
        if name not in self.active_processes:
            raise ValueError(f"Process {name} is not active.")
        
        process = self.active_processes[name]
        process.interrupt()  # Interrupt the process to deactivate it
        del self.active_processes[name]

    def run(self, until=None):
        self.simulation_running = True
        self.env.run(until=until)

    def step(self):
        self.simulation_running = True
        self.env.step()
        self.simulation_running = False

    def log_event(self, message):
        print(message)  # Placeholder for a more advanced logging mechanism

    def get_resource(self, name):
        return self.resources.get(name, None)

def customer(env, res1):
    print("Going to line")
    with res1.request() as req:
        yield req
        print("Giving order")
        yield env.timeout(2)
        print(f"{env.now}")



if __name__ == "__main__":
    import simpy

    env = simpy.Environment()

    bakery = simpy.Resource(env, capacity=2)
    env.process(customer(env, bakery))

    env.run(until=10)
