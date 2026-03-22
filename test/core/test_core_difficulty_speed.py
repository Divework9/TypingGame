from conf.speed import (
    SPAWN_INTERVAL_BASE,
    SPAWN_INTERVAL_MIN,
    FALL_SPEED_BASE,
    FALL_SPEED_MAX,
)
from conf.speed import (
    SPAWN_INTERVAL_SCORE_REDUCTION,
    FALL_SPEED_SCORE_INCREASE,
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

    # R2-02: fencepost — values just below thresholds must stay in the lower bucket
    def test_get_difficulty_just_below_thresholds(self):
        self.game.score = 99
        self.assertEqual(self.game.get_difficulty(), "easy")

        self.game.score = 299
        self.assertEqual(self.game.get_difficulty(), "medium")

    # R2-03: intermediate formula — not just floor/ceiling
    def test_get_fall_speed_intermediate_value(self):
        self.game.score = 100
        expected = min(FALL_SPEED_MAX, FALL_SPEED_BASE + 100 * FALL_SPEED_SCORE_INCREASE)
        self.assertAlmostEqual(self.game.get_fall_speed(), expected)

    def test_get_spawn_interval_intermediate_value(self):
        self.game.score = 100
        expected = max(SPAWN_INTERVAL_MIN, SPAWN_INTERVAL_BASE - 100 * SPAWN_INTERVAL_SCORE_REDUCTION)
        self.assertAlmostEqual(self.game.get_spawn_interval(), expected)
