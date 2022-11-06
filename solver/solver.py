import time
from dataclasses import dataclass
from typing import Optional

import mouse
import win32gui
from PIL import Image, ImageGrab

from .card_recognition import CardRecognizer


class Point:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def as_tuple(self) -> tuple[int, int]:
        return (self.x, self.y)

    def __add__(self, other: "Point") -> "Point":
        assert isinstance(other, Point)
        return Point(self.x + other.x, self.y + other.y)

    def __matmul__(self, other: "Point") -> tuple[int, int, int, int]:
        assert isinstance(other, Point)
        return (self.x, self.y, self.x + other.x, self.y + other.y)


@dataclass
class WindowInfo:
    hwnd: int
    rect: tuple[int, int, int, int]
    name: str


def get_open_windows() -> list[WindowInfo]:
    def _reduce(hwnd: int, result: list[WindowInfo]):
        name = win32gui.GetWindowText(hwnd)
        if not win32gui.IsWindowVisible(hwnd) or not name:
            return

        rect = win32gui.GetWindowRect(hwnd)
        window_info = WindowInfo(
            hwnd=hwnd,
            rect=rect,
            name=name,
        )
        result.append(window_info)

    windows: list[WindowInfo] = []
    win32gui.EnumWindows(_reduce, windows)
    return windows


def get_game_window(title="Solitaire Collection") -> WindowInfo:
    windows = get_open_windows()
    matching_names = [x for x in windows if title in x.name]

    if not len(matching_names):
        print(*windows, sep="\n")
        raise Exception(f"Window {title} not found")

    return matching_names[0]


TOP = Point(41, 289)
CARD_SIZE = Point(104, 138)

DECKS_X = [
    41,
    173,
    304,
    435,
    567,
    698,
    830,
]

DECK_BASE_Y = 289
DECK_OFFSET_Y = 14

PICK_COORD = Point(173, 109)
STACK_COORD = Point(41, 109)

GLOBAL_PICK_CNT = 94


class Game:
    def __init__(self) -> None:
        self.game_window = get_game_window()
        print("Found game window:", self.game_window)

        self.card_recognizer = CardRecognizer()

    def run_cycle(self) -> None:
        global GLOBAL_PICK_CNT
        while True:
            data = ImageGrab.grab(self.game_window.rect)
            new_card_coord = self.get_new_card_x(data)

            if new_card_coord is None:
                break

            card_img = data.crop(new_card_coord @ CARD_SIZE)
            card = self.card_recognizer.recognize(card_img)

            card_img.show()
            print(card)

            time.sleep(2)

            mouse.move(
                self.game_window.rect[0] + STACK_COORD.x + CARD_SIZE.x // 2,
                self.game_window.rect[1] + STACK_COORD.y + CARD_SIZE.y // 2,
            )
            mouse.click()

    def get_new_card_x(self, img: Image.Image) -> Optional[Point]:
        bands = img.getpixel((314, 173))
        # print(bands, sum(bands))
        if sum(bands) > 750:
            return Point(216, 109)

        bands = img.getpixel((292, 173))
        # print(bands, sum(bands))
        if sum(bands) > 750:
            return Point(194, 109)

        bands = img.getpixel((271, 173))
        # print(bands, sum(bands))
        if sum(bands) > 750:
            return Point(173, 109)

        return None
