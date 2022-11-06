import enum


class CardSuite(enum.Enum):
    hearts = 0
    diamonds = 1
    spades = 2
    clubs = 3


class CardValue:
    def __init__(self, num: str) -> None:
        self._num = num

    def __str__(self) -> str:
        if self._num == 0:
            return "ace"
        if self._num == 10:
            return "jack"
        if self._num == 11:
            return "queen"
        if self._num == 12:
            return "king"
        return str(self._num + 1)


class Card:
    def __init__(self, suite: int, value: int) -> None:
        self.suite = CardSuite(suite)
        self.value = CardValue(value)

    def __str__(self) -> str:
        return f"{self.value} of {self.suite.name}"
