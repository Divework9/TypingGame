from test.common import TypingGameBaseTestCase
import typing_game
from conf import game_constants as gc
from conf.word_bank import LETTER_STAGE_CONFIGS


class ProgressionStateTestCase(TypingGameBaseTestCase):
    def test_letter_stage_advances_when_mastery_combo_reached(self):
        self.game.mode = "letter"
        self.game.letter_stage = 1
        self.game.letter_stage_combo = gc.LETTER_STAGE_MASTERY_COMBO - 1
        self.game.letter_stage_clear_progress = gc.LETTER_STAGE_MASTERY_CLEAR_STEP - 1
        self.game.combo = gc.LETTER_STAGE_ADVANCE_COMBO_GT
        word = typing_game.FallingWord("a", "a", 100, 0, typing_game.TEXT_WHITE)

        self.game.clear_word(word)

        self.assertEqual(self.game.letter_stage, 2)
        self.assertEqual(self.game.letter_stage_combo, 0)

    def test_letter_stage_not_advance_when_mastery_reached_but_combo_not_enough(self):
        self.game.mode = "letter"
        self.game.letter_stage = 1
        self.game.letter_stage_combo = gc.LETTER_STAGE_MASTERY_COMBO - 1
        self.game.letter_stage_clear_progress = gc.LETTER_STAGE_MASTERY_CLEAR_STEP - 1
        self.game.combo = gc.LETTER_STAGE_ADVANCE_COMBO_GT - 1
        word = typing_game.FallingWord("a", "a", 100, 0, typing_game.TEXT_WHITE)

        self.game.clear_word(word)

        self.assertEqual(self.game.letter_stage, 1)
        self.assertEqual(self.game.letter_stage_combo, gc.LETTER_STAGE_MASTERY_COMBO)

    def test_letter_mastery_increases_only_every_five_clears(self):
        self.game.mode = "letter"
        self.game.letter_stage_combo = 0
        self.game.letter_stage_clear_progress = 0

        word = typing_game.FallingWord("a", "a", 100, 0, typing_game.TEXT_WHITE)
        for _ in range(gc.LETTER_STAGE_MASTERY_CLEAR_STEP - 1):
            self.game.clear_word(word)
            word.active = True

        self.assertEqual(self.game.letter_stage_combo, 0)
        self.assertEqual(self.game.letter_stage_clear_progress, gc.LETTER_STAGE_MASTERY_CLEAR_STEP - 1)

        self.game.clear_word(word)
        self.assertEqual(self.game.letter_stage_combo, 1)
        self.assertEqual(self.game.letter_stage_clear_progress, 0)

    def test_letter_stage_combo_resets_after_miss(self):
        self.game.mode = "letter"
        self.game.letter_stage_combo = 8
        self.game.letter_stage_clear_progress = 3
        word = typing_game.FallingWord("a", "a", 100, 0, typing_game.TEXT_WHITE)

        self.game.miss_word(word)

        self.assertEqual(self.game.letter_stage_combo, 0)
        self.assertEqual(self.game.letter_stage_clear_progress, 0)

    def test_letter_stage_does_not_overflow_final_stage(self):
        self.game.mode = "letter"
        self.game.letter_stage = len(LETTER_STAGE_CONFIGS)
        self.game.letter_stage_combo = gc.LETTER_STAGE_MASTERY_COMBO
        word = typing_game.FallingWord("a", "a", 100, 0, typing_game.TEXT_WHITE)

        self.game.clear_word(word)

        self.assertEqual(self.game.letter_stage, len(LETTER_STAGE_CONFIGS))
        self.assertEqual(self.game.letter_stage_combo, gc.LETTER_STAGE_MASTERY_COMBO)

    def test_letter_stage_advance_clears_existing_falling_letters(self):
        self.game.mode = "letter"
        self.game.letter_stage = 1
        self.game.letter_stage_combo = gc.LETTER_STAGE_MASTERY_COMBO - 1
        self.game.letter_stage_clear_progress = gc.LETTER_STAGE_MASTERY_CLEAR_STEP - 1
        self.game.combo = gc.LETTER_STAGE_ADVANCE_COMBO_GT

        cleared_word = typing_game.FallingWord("a", "a", 100, 0, typing_game.TEXT_WHITE)
        leftover_word = typing_game.FallingWord("s", "s", 200, 0, typing_game.TEXT_WHITE)
        self.game.words = [cleared_word, leftover_word]

        self.game.clear_word(cleared_word)

        self.assertEqual(self.game.letter_stage, 2)
        self.assertEqual(len(self.game.words), 0)
        self.assertFalse(leftover_word.active)

    def test_letter_stage_advance_resets_fall_speed_to_base(self):
        self.game.mode = "letter"
        self.game.letter_stage = 1
        self.game.letter_stage_combo = gc.LETTER_STAGE_MASTERY_COMBO - 1
        self.game.letter_stage_clear_progress = gc.LETTER_STAGE_MASTERY_CLEAR_STEP - 1
        self.game.combo = gc.LETTER_STAGE_ADVANCE_COMBO_GT
        self.game.score = 500
        self.game.letter_stage_speed_anchor_score = 0
        self.assertGreater(self.game.get_fall_speed(), typing_game.FALL_SPEED_BASE)

        word = typing_game.FallingWord("a", "a", 100, 0, typing_game.TEXT_WHITE)
        self.game.clear_word(word)

        self.assertEqual(self.game.letter_stage, 2)
        self.assertEqual(self.game.letter_stage_speed_anchor_score, self.game.score)
        self.assertEqual(self.game.get_fall_speed(), typing_game.FALL_SPEED_BASE)

    def test_clear_word_updates_combo_score_and_level(self):
        self.game.score = 145
        word = typing_game.FallingWord("apple", "apple", 100, 0, typing_game.TEXT_WHITE)

        self.game.clear_word(word)

        self.assertFalse(word.active)
        self.assertEqual(self.game.combo, 1)
        self.assertEqual(self.game.max_combo, 1)
        self.assertEqual(self.game.words_cleared, 1)
        expected_score = 145 + len(word.type_text) * 10 + min(1, 10) * 5
        self.assertEqual(self.game.score, expected_score)
        self.assertEqual(self.game.level, 2)

    def test_clear_word_combo_bonus_is_capped_at_ten(self):
        # combo already at 10; bonus should be min(11,10)*5 = 50, not 55
        self.game.combo = 10
        self.game.score = 0
        word = typing_game.FallingWord("hi", "hi", 100, 0, typing_game.TEXT_WHITE)

        self.game.clear_word(word)

        bonus = min(self.game.combo, 10) * 5  # combo is now 11, capped to 10
        base = len(word.type_text) * 10
        self.assertEqual(self.game.score, base + bonus)

    def test_miss_word_reduces_life_and_ends_game(self):
        word = typing_game.FallingWord("cat", "cat", 100, 0, typing_game.TEXT_WHITE)
        self.game.lives = 1

        self.game.miss_word(word)

        self.assertFalse(word.active)
        self.assertEqual(self.game.lives, 0)
        self.assertEqual(self.game.state, self.game.STATE_OVER)

    def test_update_removes_inactive_words(self):
        self.game.words = [typing_game.FallingWord("cat", "cat", 100, 0, typing_game.TEXT_WHITE)]
        self.game.words[0].active = False
        self.game.spawn_timer = 999

        self.game.update(0.016)

        self.assertEqual(len(self.game.words), 0)

    def test_update_is_noop_when_state_is_not_playing(self):
        self.game.state = self.game.STATE_MENU
        self.game.game_time = 0.0

        self.game.update(0.1)

        self.assertAlmostEqual(self.game.game_time, 0.0)

    def test_update_triggers_spawn_when_timer_reaches_zero(self):
        self.game.words = []
        self.game.spawn_timer = 0  # already expired

        self.game.update(0)  # dt=0 so no movement, just timer logic

        self.assertEqual(len(self.game.words), 1)

    def test_update_auto_misses_word_that_falls_past_boundary(self):
        boundary = typing_game.SCREEN_H - (typing_game.BOTTOM_UI_HEIGHT + 15)
        word = typing_game.FallingWord("cat", "cat", 100, 0, typing_game.TEXT_WHITE)
        word.y = boundary + 1  # already past boundary
        self.game.words = [word]
        self.game.spawn_timer = 999  # prevent new spawns
        initial_lives = self.game.lives

        self.game.update(0.016)

        self.assertEqual(self.game.lives, initial_lives - 1)
        self.assertEqual(self.game.words_missed, 1)
        self.assertEqual(len(self.game.words), 0)

    def test_miss_word_resets_combo_and_increments_missed_count(self):
        word = typing_game.FallingWord("cat", "cat", 100, 0, typing_game.TEXT_WHITE)
        self.game.combo = 5
        self.game.lives = 3

        self.game.miss_word(word)

        self.assertEqual(self.game.combo, 0)
        self.assertEqual(self.game.words_missed, 1)
        self.assertFalse(word.active)

    def test_miss_word_continues_game_when_lives_remain(self):
        word = typing_game.FallingWord("cat", "cat", 100, 0, typing_game.TEXT_WHITE)
        self.game.lives = 2

        self.game.miss_word(word)

        self.assertEqual(self.game.lives, 1)
        self.assertEqual(self.game.state, self.game.STATE_PLAYING)

    # R2-06: miss_word sets shake_timer
    def test_miss_word_sets_shake_timer(self):
        word = typing_game.FallingWord("cat", "cat", 100, 0, typing_game.TEXT_WHITE)
        self.game.shake_timer = 0.0
        self.game.lives = 3

        self.game.miss_word(word)

        self.assertGreater(self.game.shake_timer, 0)

    # R2-07: clear_word sets flash_timer
    def test_clear_word_sets_flash_timer(self):
        word = typing_game.FallingWord("hi", "hi", 100, 0, typing_game.TEXT_WHITE)
        self.game.flash_timer = 0.0

        self.game.clear_word(word)

        self.assertGreater(self.game.flash_timer, 0)

    # R2-08: update() decrements shake_timer and flash_timer
    def test_update_decrements_shake_and_flash_timers(self):
        self.game.shake_timer = 0.5
        self.game.flash_timer = 0.5
        self.game.spawn_timer = 999
        self.game.words = []

        self.game.update(0.1)

        self.assertAlmostEqual(self.game.shake_timer, 0.4, places=5)
        self.assertAlmostEqual(self.game.flash_timer, 0.4, places=5)

    def test_update_timers_clamp_at_zero(self):
        self.game.shake_timer = 0.05
        self.game.flash_timer = 0.05
        self.game.spawn_timer = 999
        self.game.words = []

        self.game.update(1.0)  # dt >> remaining timer

        self.assertEqual(self.game.shake_timer, 0.0)
        self.assertEqual(self.game.flash_timer, 0.0)

    # R2-04: clear_word no-level-up path
    def test_clear_word_no_level_up_when_score_below_threshold(self):
        self.game.score = 0
        self.game.level = 1
        word = typing_game.FallingWord("hi", "hi", 100, 0, typing_game.TEXT_WHITE)
        # "hi" is 2 chars: score = 0 + 2*10 + min(1,10)*5 = 25; new_level = 1+25//150 = 1

        self.game.clear_word(word)

        self.assertEqual(self.game.level, 1)  # no level-up

    # R2-05: max_combo stays when combo is below existing max
    def test_max_combo_not_updated_when_combo_below_current_max(self):
        self.game.combo = 2
        self.game.max_combo = 5  # existing max is higher
        word = typing_game.FallingWord("hi", "hi", 100, 0, typing_game.TEXT_WHITE)

        self.game.clear_word(word)

        self.assertEqual(self.game.max_combo, 5)  # unchanged
        self.assertEqual(self.game.combo, 3)

    # R2-05: max_combo updates when combo exceeds existing max
    def test_max_combo_updates_when_combo_exceeds_current_max(self):
        self.game.combo = 4
        self.game.max_combo = 4
        word = typing_game.FallingWord("hi", "hi", 100, 0, typing_game.TEXT_WHITE)

        self.game.clear_word(word)

        self.assertEqual(self.game.combo, 5)
        self.assertEqual(self.game.max_combo, 5)

    # R3-01: miss_word must NOT touch max_combo
    def test_miss_word_does_not_reset_max_combo(self):
        self.game.combo = 5
        self.game.max_combo = 5
        self.game.lives = 3
        word = typing_game.FallingWord("cat", "cat", 100, 0, typing_game.TEXT_WHITE)

        self.game.miss_word(word)

        self.assertEqual(self.game.combo, 0)
        self.assertEqual(self.game.max_combo, 5)  # max_combo must survive miss

    # R3-02: level-up inside clear_word must NOT reset combo
    def test_levelup_via_clear_word_does_not_reset_combo(self):
        # score=140, combo=3; clear "apple"(5): total=140+50+20=210 → level=1+210//150=2
        self.game.score = 140
        self.game.combo = 3
        word = typing_game.FallingWord("apple", "apple", 100, 0, typing_game.TEXT_WHITE)

        self.game.clear_word(word)

        self.assertEqual(self.game.level, 2)   # level-up happened
        self.assertEqual(self.game.combo, 4)   # combo incremented, NOT reset by apply_keyboard_config

    # R3-03: spawn_timer must be reset after spawn to prevent every-frame spawning
    def test_spawn_timer_reset_prevents_double_spawn_per_tick(self):
        self.game.words = []
        self.game.spawn_timer = 0

        self.game.update(0)   # first tick: spawns 1 word, resets spawn_timer
        self.assertEqual(len(self.game.words), 1)

        self.game.update(0)   # second tick dt=0: timer stays positive, no spawn
        self.assertEqual(len(self.game.words), 1)

    # R3-04: update() must be noop when state is STATE_OVER
    def test_update_is_noop_when_state_is_over(self):
        self.game.state = self.game.STATE_OVER
        self.game.game_time = 0.0

        self.game.update(0.5)

        self.assertAlmostEqual(self.game.game_time, 0.0)

    # R4-02: update() increments game_time when PLAYING
    def test_update_increments_game_time_when_playing(self):
        self.game.game_time = 0.0
        self.game.spawn_timer = 999
        self.game.words = []

        self.game.update(0.25)

        self.assertAlmostEqual(self.game.game_time, 0.25)
