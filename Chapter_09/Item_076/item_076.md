# Item 76: Know how to Port Threaded I/O to `asyncio`

- [Notes](#notes)
- [Things to Remember](#things-to-remember)

## Notes

- Given the cleanliness of coroutines, how does one port existing
  *threaded* concurrency to use `aysnc`?
- Since `async` is a language feature, not a library one conversion is
  usually straightforward
- For example, consider a simple TCP server hosting the “guess the
  number” game
  - Server takes a `lower` and `upper` parameter
    - Generates number in this range
  - Server returns guesses as for values as requested by a client
  - Collects report if guess was closer (warmer) or further (colder)
- Standard implementation for a client/server is to use threads to
  handle blocking I/O

``` python
import random


class EOFError(Exception):
    pass


class Connection:
    def __init__(self, connection):
        self.connection = connection
        self.file = connection.makefile("rb")

    def send(self, command):
        line = command + "\n"
        data = line.encode()
        self.connection.send(data)

    def receive(self):
        line = self.file.readline()
        if not line:
            raise EOFError("Connection closed")
        return line[:-1].decode()


WARMER = "warmer"
COLDER = "colder"
SAME = "same"
UNSURE = "unsure"
CORRECT = "correct"


class UnknownCommandError(Exception):
    pass


class ServerSession(Connection):
    def __init__(self, *args):
        super().__init__(*args)
        self.clear_state()

    def loop(self):
        while command := self.receive():
            match command.split(" "):
                case "PARAMS", lower, upper:
                    self.get_params(lower, upper)
                case ["NUMBER"]:
                    self.send_number()
                case "REPORT", decision:
                    self.receive_report(decision)
                case ["CLEAR"]:
                    self.clear_state()
                case _:
                    raise UnknownCommandError(command)

    def set_params(self, lower, upper):
        self.clear_state()
        self.lower = int(lower)
        self.upper = int(upper)

    def next_guess(self):
        if self.secret is not None:
            return self.secret

        while True:
            guess = random.randint(self.lower, self.upper)
            if guess not in self.guesses:
                return guess

    def send_number(self):
        guess = self.next_guess()
        self.guesses.append(guess)
        self.send(format(guess))

    def receive_report(self):
        last = self.guesses[-1]
        if decision == CORRECT:
            self.secret = last

        print(f"Server: {last} is {decision}")

    def clear_state(self):
        self.lower = None
        self.upper = None
        self.secret = None
        self.guesses = []
```

- We define a basic helper class `Connection` that can handle sending
  and receiving messages
  - We define a line to represent a command to be processed
- Server is then implemented as a class that handles a connection
  - Maintains some internal state
  - `loop` handles incoming commands and dispatches them to the required
    internal function
    - Use a `match` statement to destructure the commands (See [Item
      9](../../Chapter_01/Item_009/item_009.qmd))
  - First command `set_params`
    - Bounds the `lower` and `upper` numbers the server will try to
      guess
  - Second command `send_number`
    - Makes a guess based on the current state
    - Defers to `next_guess`
      - Ensures that the server never guesses a number it’s already
        guessed
  - Third command `receive_report`
    - Receives decision from client noting if guess is warmer, colder,
      the same or correct
    - Then updates it’s internal state
  - Last command clears the state and ends a game
- We then run a game using a context manager via a `with` statement
  - Ensures the server state is managed correctly (See [Item
    78](../Item_078/item_078.qmd))
  - We do this with a function `new_game`
    - Sends first and last commands to the server
    - Provides a context object
      - Can be used for the duration of the game

## Things to Remember
