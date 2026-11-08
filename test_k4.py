import unittest

import k4


class KryptosTests(unittest.TestCase):
    def test_public_crib_alignment(self):
        self.assertEqual(len(k4.CIPHERTEXT), 97)
        self.assertEqual(k4.CIPHERTEXT[21:34], "FLRVQQPRNGKSS")
        self.assertEqual(k4.CIPHERTEXT[63:74], "NYPVTTMZFPK")
        self.assertEqual(sum(len(text) for _, text in k4.CRIBS), 24)

    def test_repeating_key_recovers_a_known_vigenere_example(self):
        result = k4.scan("LXFOPVEFRNHR", ((1, "ATTACKATDAWN"),), ["ONLEM"], repeat=True)
        self.assertIn(
            {"alphabet": "az", "method": "vigenere", "offset": 2, "key": "ONLEM", "plaintext": "ATTACKATDAWN"},
            result["matches"],
        )

    def test_running_key_uses_a_window_and_checks_the_last_crib_letter(self):
        text = "XXXLEMONLEMONLE"
        result = k4.scan("LXFOPVEFRNHR", ((1, "ATTACKATDAWN"),), [text], repeat=False)
        self.assertIn(
            {"alphabet": "az", "method": "vigenere", "offset": 3, "key": "LEMONLEMONLE", "plaintext": "ATTACKATDAWN"},
            result["matches"],
        )
        wrong = k4.scan("LXFOPVEFRNHR", ((1, "ATTACKATDAWO"),), [text], repeat=False)
        self.assertEqual(wrong["matches"], [])

    def test_all_methods_and_alphabets(self):
        result = k4.scan("F", (), ["T"], repeat=True)
        self.assertEqual(
            {(hit["alphabet"], hit["method"]): hit["plaintext"] for hit in result["matches"]},
            {
                ("az", "vigenere"): "M",
                ("az", "beaufort"): "O",
                ("az", "variant-beaufort"): "Y",
                ("kryptos", "vigenere"): "B",
                ("kryptos", "beaufort"): "M",
                ("kryptos", "variant-beaufort"): "J",
            },
        )

    def test_book_experiment(self):
        self.assertEqual(k4.letters("  Les Misérables! 1862"), "LESMISERABLES")
        result = k4.scan(k4.CIPHERTEXT, k4.CRIBS, k4.book_keys(), repeat=True)
        self.assertEqual(result, {"candidates": 71, "settings": 9894, "matches": []})

    def test_clock_experiment_and_period_conflicts(self):
        key = k4.clock_key(23, 1, 0, 1)
        self.assertEqual([key[i] for i in (0, 1, 23, 24, 48)], [23, 0, 22, 24, 25])
        keys = k4.clock_keys()
        self.assertEqual(len(set(keys)), 6240)
        result = k4.scan(k4.CIPHERTEXT, k4.CRIBS, keys, repeat=False)
        self.assertEqual(result, {"candidates": 6240, "settings": 37440, "matches": []})
        self.assertEqual(
            k4.period_24_required_shifts(),
            {"az": {"vigenere": [1, 10], "beaufort": [9, 14], "variant-beaufort": [25, 16]},
             "kryptos": {"vigenere": [1, 9], "beaufort": [23, 1], "variant-beaufort": [25, 17]}},
        )


if __name__ == "__main__":
    unittest.main()
