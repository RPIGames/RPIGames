"""
Simple default generator for a random username.
"""

import random

from .lists import adjective_list, noun_list

def random_username() -> str:
    """Returns a random username consisting of an adjective and a noun."""
    return random.choice(adjective_list).capitalize() + " " + random.choice(noun_list).capitalize()

# Also doubles as a tool for generating random usernames for testing and such
if __name__ == "__main__":
    print(f"A random username: {random_username()}")
