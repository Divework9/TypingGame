import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import typing_game


class TypingGameBaseTestCase(unittest.TestCase):
    def setUp(self):
        self.game = typing_game.TypingGame()
        self.game.state = self.game.STATE_PLAYING
