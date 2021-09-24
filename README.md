# Nvim.Bench

Automated reproducible completion framework benchmarking suite for nvim.

(**PR welcome** to tweak each framework to run as fast as possible)

## Methodology

It uses `tmux` to send keys at a randomized regular intervals to simulate ideal human typing.

The input tokens are _naive_, they are just the text of the current buffer parsed into whitespace delimited tokens.

This is to ensure there is always some matches possible for the vast majority of input.

The distribution of spaces and lineseps is also generated from the same buffer.

Time lapse between latest keypress and completion event is measured and stored.

## Data set?

In `./data`, each piece of text is transformed into a pool of whitespace delimited tokens
