"""
Dexter Toolkit - Data Experimentation and Tinkering Kit

A comprehensive Python toolkit for data science, machine learning, optimization, 
simulation, and visualization experiments.
"""

__version__ = "0.1.0"
__author__ = "Deniz"
__email__ = "denizkurtaran00@gmail.com"

# Import all submodules
from . import (
    board,      # Interactive data dashboard
    core,       # Core pipeline and utilities
    data_wrangling,  # Data transformation tools
    environment,     # Environment simulation
    language,        # Language processing
    ml,         # Machine learning
    optimization,    # Mathematical optimization
    simulation,      # Discrete event simulation
    stats,      # Statistical analysis
    visualization    # Visualization tools
)

# Convenience imports for commonly used classes
from .ml.pick import pick_classifier
from .optimization.problem import Problem
from .simulation.sim_manager import SimManager
from .stats.distribution import Normal, Uniform, Binomial, Poisson, Exponential
from .visualization.space import Space
from .environment.grid import Grid, GridApp
from .board.main import IPKernel

__all__ = [
    # Submodules
    'board',
    'core', 
    'data_wrangling',
    'environment',
    'language',
    'ml',
    'optimization',
    'simulation',
    'stats',
    'visualization',
    
    # Common classes
    'pick_classifier',
    'Problem',
    'SimManager', 
    'Normal',
    'Uniform',
    'Binomial',
    'Poisson',
    'Exponential',
    'Space',
    'Grid',
    'GridApp',
    'IPKernel'
]
