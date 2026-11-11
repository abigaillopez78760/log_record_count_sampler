import unittest

from log_record_count_sampler import CountSampler


class CountSamplerTests(unittest.TestCase):
    def test_default_interval_is_two(self):
        sampler = CountSampler()
        self.assertEqual(sampler.every, 2)

    def test_emits_on_multiples_of_interval(self):
        sampler = CountSampler(every=3)
        results = [sampler.process("a") for _ in range(7)]
        self.assertEqual(results, [False, False, True, False, False, True, False])

    def test_first_occurrence_emits_when_every_is_one(self):
        sampler = CountSampler(every=1)
        self.assertTrue(sampler.process("a"))
        self.assertTrue(sampler.process("a"))

    def test_first_occurrence_does_not_emit_when_every_is_two(self):
        sampler = CountSampler()
        self.assertFalse(sampler.process("a"))

    def test_messages_are_tracked_independently(self):
        sampler = CountSampler(every=2)
        self.assertFalse(sampler.process("a"))
        self.assertFalse(sampler.process("b"))
        self.assertTrue(sampler.process("a"))
        self.assertTrue(sampler.process("b"))
        self.assertEqual(sampler.count("a"), 2)
        self.assertEqual(sampler.count("b"), 2)

    def test_count_does_not_advance(self):
        sampler = CountSampler(every=2)
        self.assertEqual(sampler.count("a"), 0)
        self.assertEqual(sampler.count("a"), 0)
        sampler.process("a")
        self.assertEqual(sampler.count("a"), 1)
        self.assertEqual(sampler.count("a"), 1)

    def test_count_of_unseen_message_is_zero(self):
        sampler = CountSampler()
        self.assertEqual(sampler.count("never seen"), 0)

    def test_reset_clears_counts_but_keeps_interval(self):
        sampler = CountSampler(every=4)
        for _ in range(3):
            sampler.process("a")
        sampler.reset()
        self.assertEqual(sampler.count("a"), 0)
        self.assertEqual(sampler.every, 4)
        self.assertFalse(sampler.process("a"))

    def test_counts_returns_a_copy(self):
        sampler = CountSampler()
        sampler.process("a")
        snapshot = sampler.counts()
        snapshot["a"] = 999
        snapshot["b"] = 1
        self.assertEqual(sampler.count("a"), 1)
        self.assertEqual(sampler.count("b"), 0)

    def test_empty_message_is_a_valid_key(self):
        sampler = CountSampler(every=2)
        self.assertFalse(sampler.process(""))
        self.assertTrue(sampler.process(""))
        self.assertEqual(sampler.count(""), 2)

    def test_invalid_interval_rejected(self):
        for bad in (0, -1, 1.5, "2", None, True):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    CountSampler(every=bad)

    def test_large_interval_emits_only_at_that_multiple(self):
        sampler = CountSampler(every=1000)
        emitted = [sampler.process("x") for _ in range(1000)]
        self.assertEqual(sum(emitted), 1)
        self.assertTrue(emitted[-1])


if __name__ == "__main__":
    unittest.main()
