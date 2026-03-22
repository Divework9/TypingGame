from conf.speed import (
    SPAWN_INTERVAL_BASE,
    SPAWN_INTERVAL_MIN,
    FALL_SPEED_BASE,
    FALL_SPEED_MAX,
)

from test.common import TypingGameBaseTestCase


class DifficultySpeedTestCase(TypingGameBaseTestCase):
    def test_get_difficulty_by_score(self):
        self.game.score = 0
        self.assertEqual(self.game.get_difficulty(), "easy")

        self.game.score = 100
        self.assertEqual(self.game.get_difficulty(), "medium")

        self.game.score = 300
        self.assertEqual(self.game.get_difficulty(), "hard")

    def test_spawn_interval_and_fall_speed_bounds(self):
        self.game.score = 0
        self.assertAlmostEqual(self.game.get_spawn_interval(), SPAWN_INTERVAL_BASE)
        self.assertAlmostEqual(self.game.get_fall_speed(), FALL_SPEED_BASE)

        self.game.score = 10_000
        self.assertAlmostEqual(self.game.get_spawn_interval(), SPAWN_INTERVAL_MIN)
        self.assertAlmostEqual(self.game.get_fall_speed(), FALL_SPEED_MAX)
