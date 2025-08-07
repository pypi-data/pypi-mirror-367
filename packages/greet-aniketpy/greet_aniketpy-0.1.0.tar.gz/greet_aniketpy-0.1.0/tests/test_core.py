import unittest
from greetpy import greet, greet_formal, greet_casual

class TestGreetpy(unittest.TestCase):
    def test_greet(self):
        self.assertEqual(greet("Alice"), "Hello, Alice!")

    def test_greet_formal(self):
        self.assertEqual(greet_formal("Bob"), "Good day, Mr. Bob.")

    def test_greet_casual(self):
        self.assertEqual(greet_casual("Charlie"), "Hey Charlie, what's up?")

if __name__ == "__main__":
    unittest.main()