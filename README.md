# Nvim.Bench

Automated reproducible completion framework benchmarking suite for nvim.

(**PR welcome** to tweak each framework to run as fast as possible)

## Methodology

### Input

`tmux` is used to send keys to simulate ideal human typing.

The words typed are _naive tokens_ from parsing current document into alphanum + "\_" delimited by whitespaces and symbols.

This should work fairly well for **c family** of languages, which are widely used.

The distribution of spaces and lineseps is also generated from the same buffer.

Note. the same seed is used to generate reproducible randomness.

### Measurement

Time lapse between latest keypress and completion event is measured and stored.

n `--samples=n` is taken.

### Speed

Assuming `--avg-word-len=9` and `--wpm=99`, a persecond input rate is calculated with `--variance=0.15`.

## Data set?

In `./data`, each piece of text is transformed into a pool of whitespace delimited tokens
