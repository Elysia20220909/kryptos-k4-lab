# Kryptos K4 Lab

A small, offline toolkit for testing candidate keys against the 24 published crib
letters of Jim Sanborn's Kryptos K4. It checks letter positions as printed, using
Vigenère, Beaufort, and variant Beaufort with both A–Z and Kryptos alphabet order.

## Run

Use Python 3.7 or newer with the standard library. The examples were verified
with Python 3.13.15. From the repository directory:

```console
python k4.py books
python k4.py clock
python k4.py repeat "The Gold-Bug"
python k4.py running path/to/local-text.txt
python -m unittest -v
```

`repeat` checks all starting offsets in a repeating text key. `running` checks
every contiguous 97-letter window of a local UTF-8 file. Both uppercase text,
decompose accents and retain A–Z. Match offsets are zero-based positions in
the normalized input. A match contains the key or key window and all 97
decoded letters. A full crib match is a necessary condition under the
tested model. Evaluating the rest of the plaintext remains a separate step.

## Reproduce the experiments

| Command | Candidate inputs | Settings checked | Full crib matches |
|---|---:|---:|---:|
| `books` | 71 distinct text keys | 9,894 | 0 |
| `clock` | 6,240 numeric keys | 37,440 | 0 |

- `books.json` contains the author, short name, title and source for each
  bibliographic record. The keys use the name, short name, title, and both
  orders of name plus title. The search deduplicates normalized keys.
- `clock` uses hours 0–23, both directions, every starting hour, an overall
  shift of 0–25, and a change of 0, ±1 or ±24 per 24-character block.
  Positions 22 and 70 require different key values in every model. They
  are 48 positions apart, so a key that repeats every 24 characters fails
  with these letter positions.
- The counts are configurations checked by these commands. Reproducing
  the city inscription experiments requires their own fixtures. The
  transposition experiments also need a permutation step. Running-key
  results depend on the particular text and edition.

## Sources and license

The puzzle transcription is listed on the public [K4 challenge](https://www.paradigm.xyz/kryptos/k4).
The two anchors at positions 22–34 and 64–74 are Sanborn's published clues,
collected on [Elonka Dunin's Kryptos page](https://elonka.com/kryptos/).
The 24-segment structure is documented by [the City of Berlin](https://www.berlin.de/sehenswuerdigkeiten/3561749-3558930-weltzeituhr.html).
The repository includes bibliographic facts and source links. Supply your
own copy of a text to test it with `running`.

The original software and documentation are available under the [MIT License](LICENSE).
