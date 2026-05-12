import random

from .lists import adjective_list, noun_list

def random_username() -> str:
    return random.choice(adjective_list).capitalize() + " " + random.choice(noun_list).capitalize()

if __name__ == "__main__":
    print(f"A random username: {random_username()}")
