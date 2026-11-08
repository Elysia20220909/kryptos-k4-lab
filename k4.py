"""Check candidate keys against the public Kryptos K4 crib positions."""

import argparse
import json
import unicodedata
from itertools import product
from pathlib import Path


CIPHERTEXT = (
    "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJK"
    "LUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
)
CRIBS = ((22, "EASTNORTHEAST"), (64, "BERLINCLOCK"))
ALPHABETS = {
    "az": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "kryptos": "KRYPTOSABCDEFGHIJLMNQUVWXZ",
}
# K = cipher_sign * C + plain_sign * P, modulo 26.
RULES = {
    "vigenere": (1, -1),
    "beaufort": (1, 1),
    "variant-beaufort": (-1, 1),
}


def letters(text):
    normalized = unicodedata.normalize("NFD", text).upper()
    return "".join(letter for letter in normalized if "A" <= letter <= "Z")


def known_letters(cribs):
    return {
        start - 1 + offset: letter
        for start, text in cribs
        for offset, letter in enumerate(text)
    }


def book_keys():
    records = json.loads(Path(__file__).with_name("books.json").read_text(encoding="utf-8"))
    keys = {
        letters(value)
        for author, surname, title, _ in records
        for value in (author, surname, title, title + author, author + title)
    }
    return sorted(keys)


def clock_key(start, direction, shift, drift):
    return tuple(
        ((start + direction * index) % 24 + shift + (index // 24) * drift) % 26
        for index in range(len(CIPHERTEXT))
    )


def clock_keys():
    return [
        clock_key(start, direction, shift, drift)
        for start, direction, shift, drift in product(
            range(24), (-1, 1), range(26), (0, 1, -1, 24, -24)
        )
    ]


def period_24_required_shifts():
    known = known_letters(CRIBS)
    return {
        name: {
            method: [
                (cipher_sign * alphabet.index(CIPHERTEXT[index])
                 + plain_sign * alphabet.index(known[index])) % 26
                for index in (21, 69)
            ]
            for method, (cipher_sign, plain_sign) in RULES.items()
        }
        for name, alphabet in ALPHABETS.items()
    }


def scan(ciphertext, cribs, keys, *, repeat):
    known = known_letters(cribs)
    size = len(ciphertext)
    matches = []
    settings = 0

    for alphabet_name, alphabet in ALPHABETS.items():
        indices = {letter: index for index, letter in enumerate(alphabet)}
        cipher = tuple(indices[letter] for letter in ciphertext)
        requirements = {
            method: tuple(
                (index, (cipher_sign * cipher[index] + plain_sign * indices[plain]) % 26)
                for index, plain in known.items()
            )
            for method, (cipher_sign, plain_sign) in RULES.items()
        }
        for key in keys:
            values = tuple(indices[letter] for letter in key) if isinstance(key, str) else key
            starts = len(values) if repeat else len(values) - size + 1
            if starts <= 0:
                minimum = "one A-Z letter" if repeat else f"{size} A-Z letters"
                raise ValueError(f"Key needs at least {minimum}.")
            if repeat:
                values = values * (2 + (size - 1) // starts)
            settings += starts * len(RULES)

            for method, (cipher_sign, plain_sign) in RULES.items():
                required = requirements[method]
                for offset in range(starts):
                    if any(values[offset + index] != shift for index, shift in required):
                        continue
                    plaintext = "".join(
                        alphabet[(plain_sign * (values[offset + index] - cipher_sign * value)) % 26]
                        for index, value in enumerate(cipher)
                    )
                    matches.append({
                        "alphabet": alphabet_name,
                        "method": method,
                        "offset": offset,
                        "key": key if repeat else key[offset:offset + size],
                        "plaintext": plaintext,
                    })

    return {"candidates": len(keys), "settings": settings, "matches": matches}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("books", help="reproduce the bibliographic candidate experiment")
    commands.add_parser("clock", help="reproduce the 24-hour numeric key experiment")
    repeating = commands.add_parser("repeat", help="try every rotation of a text key")
    repeating.add_argument("key")
    running = commands.add_parser("running", help="scan 97-letter windows in a UTF-8 text file")
    running.add_argument("file", type=Path)
    args = parser.parse_args()

    try:
        if args.command == "books":
            keys = book_keys()
        elif args.command == "clock":
            keys = clock_keys()
        elif args.command == "repeat":
            keys = [letters(args.key)]
        else:
            keys = [letters(args.file.read_text(encoding="utf-8"))]
        result = scan(CIPHERTEXT, CRIBS, keys, repeat=args.command in ("books", "repeat"))
    except (OSError, ValueError) as error:
        parser.error(str(error))

    if args.command == "clock":
        result["period_24_required_shifts_at_22_and_70"] = period_24_required_shifts()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
