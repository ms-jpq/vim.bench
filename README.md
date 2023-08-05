# Vim.Bench

# This is flawed

I realized after some time that this repo as it is just a bad way of measuring speed because well, not everybody uses the same API. Especially with some frameworks switching to their own completion besides the vim native one.

I don't have the time & energy to make a nice benchmark for now. So this repo is on hold.

---

Reproducible nvim completion framework benchmarks.

Runs inside Docker. Fair and balanced

---

## Methodology

Note: All "randomness" are generated from the same seed for each run, and therefore "fair".

### Input

`tmux` is used to send keys to simulate ideal human typing.

#### Tokens

The words typed are _naive tokens_ from parsing some document into (alphanum + "\_") delimited by whitespaces and symbols.

This tokenization should work fairly well for **c family** of languages, which are the industry standard.

A uniform distribution of whitespaces is also generated from the same document.

#### LSP

For LSP sources, due to difficulty of coaxing existing servers into predictable behaviour, a mock LSP is written specifically to spit out predefined results per-response.

This LSP is configurable to have a controlled delay before each response as well as controlled number of items.

A gaussian model is used to generate the two parameters.

### Measurement

n keystrokes of `--samples` is performed.

### Speed

Using `--avg-word-len`, `--wpm` and `--variance`, a normal distribution is constructed of the desired delay between keystrokes.

### Data

See `./fs/data/`

### Modularity

Some frameworks will have by default, very little sources enabled, if any.

Others will come with more out of the box.

For a fair comparison: All frameworks tested will have to following enabled, on top of whatever else they come enabled by default:

- buffer

- lsp

- path

The reasoning is that: 1) Almost all authors will have written these sources firsthand, and 2) they seem to be the most useful sources.

No default sources will be disabled, because users don't tend to do that.

---

## [Cool, pictures](https://github.com/ms-jpq/vim.bench/tree/main/plots)

The plots are [kernel density estimations](https://en.wikipedia.org/wiki/Kernel_density_estimation).

They are an estimate of the true [probability density function](https://en.wikipedia.org/wiki/Probability_density_function).

### Q0, 50, 95, 100?

Mean `min`, `median`, `1 in 20`, `max`, respectively.

Without assuming any statistical distribution:

**`Q50` is a more robust measure than `avg`**, and `Q95` is a decent measure of a common `bad` value.

---

## Analysis

Please keep in mind that this is purely a synthetic benchmark, which definitely is one of those **need context to interpret** type of things.

There is **no good way** to measure _real speed_ across frameworks, raw numbers here come with big caveats.

### Study design limitations

#### LSPs do not follow any particular prior distribution

There are two independent dimensions to LSP slowness

1. Waiting for LSP results

2. Parsing of LSP results (ie. some LSPs will require parsing for thousands of rows)

However, due to the diversity and internal complexity of LSP servers, it precludes this study from being able to assume generalizable models for these two parameters.

Consequently, the gaussian model used here is almost certainly not representative of real LSP delays.

Anecdata suggests many LSPs are prone to mostly "good" behaviour, interspersed with occasional "lag spikes", which could indicate some poisson distribution of lag events.

#### Streaming completion

Streaming completion is very good for time to first result _(TTFR)_, but it presents us with an issue:

While the fast sources will return right away, the slower ones might never make it before the next keystroke.

This has the funny effect of removing the influence of slower sources entirely, which is _disastrous_ for study integrity.

The mitigation is actually to **set typing speed unrealistically slow**, enough so that we have confidence that the LSP servers can catch up.

This is obviously not ideal.

### Fast on paper != fast IRL

The most responsive frameworks are not necessarily the fastest ones, because **humans still have to choose the results**.

For example the streaming completion approach actually has **severe trade offs** infavor of faster _TTFR_:

#### Ranking

Having suboptimal ranking is BAD, it pushes work **from fast machines onto slow humans**.

The streaming approach has to be additive, because its too disruptive to shift existing menu items around.

Therefore it is limited to sorting only within stream batches, and to make things worse, _slower batches typically contain higher quality results_.

That means better results will often end up at the bottom, necessitating more work for humans.

#### Limiting

This is a direct consequence of limited ranking optimizations.

Because the framework have no idea how much each source will send, it has the dilemma of either sending too many results or too little.

Sending too many results in early batches from likely inferior sources will waste the users time, and sending too little will obscure potentially useful completions.

#### Clarity on when / if results will come in

This is a HCI thing:

Having higher quality results come in slower is likely to **inadvertently train users** to wait for them. This is evidently bad for input speed.

## Conclusion

There is never going to be a closed form solution to "what is the fastest framework", because of the trade offs detailed above.

A toy example of a degenerate framework that returns a single fixed `👌` emoji will probably beat anything out there in terms of raw speed, but it is utterly useless.

Before you reach your own conclusion, the results of this repo **must be considered alongside inextricably human measure**.
