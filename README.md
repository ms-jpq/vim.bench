# Nvim.Bench

Automated reproducible completion framework benchmarking suite for nvim.

Let's try to make this the fairest possible.

**PR welcome**

## Methodology

### Input

`tmux` is used to send keys to simulate ideal human typing.

The words typed are _naive tokens_ from parsing current document into alphanum + "\_" delimited by whitespaces and symbols.

These tokens should work fairly well for **c family** of languages, which are widely used.

The distribution of spaces and lineseps is also generated from the same buffer.

Note. the same seed is used to generate reproducible randomness.

### Measurement

n keystrokes of `--samples` is performed.

**Have no idea how to best measure time-lapse**

I don't think the current way is the best

### Speed

Using `--avg-word-len`, `--wpm` and `--variance`, a Normal distribution is constructed of the desired delay between keystrokes.

Samples are taken from the distribution, using the same seed each time.

### Data

See `./fs/data/`

### Modularity

Some frameworks will have bydefault, very little sources enabled, if any. Other ones will come with more out of the box.

For a fair comparison: All frameworks tested will have to following enabled, on top of whatever else they come enabled by default:

- buffer

- lsp

- path

The reasoning is that: 1) Almost all authors will have written these sources firsthand, and 2) they seem to be the most useful sources.

No default sources will be disabled, because users don't tend to do that.

## Analysis

Honestly, I think I put alot of work writing this and it ended up being fairly useless.
