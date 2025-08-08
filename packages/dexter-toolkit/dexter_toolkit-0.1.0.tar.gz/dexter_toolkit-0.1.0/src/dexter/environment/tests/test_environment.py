import unittest
from grid.grid_environment import GridEnvironment

class TestGridEnvironment(unittest.TestCase):
    def setUp(self):
        self.env = GridEnvironment(10, 10)

    def test_set_cell(self):
        self.env.set_cell(1, 1, 1)
        self.assertEqual(self.env.grid[1, 1], 1)

    def test_set_agent(self):
        self.env.set_agent(2, 2)
        self.assertEqual(self.env.agent_pos, (2, 2))
        self.assertEqual(self.env.grid[2, 2], 1)

if __name__ == '__main__':
    unittest.main()
