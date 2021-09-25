# Nvim.Bench

Automated reproducible completion framework benchmarking suite for nvim.

This whole thing runs inside Docker, so anybody can reproduce it easily.

---

## Methodology

### Input

`tmux` is used to send keys to simulate ideal human typing.

The words typed are _naive tokens_ from parsing current document into (alphanum + "\_") delimited by whitespaces and symbols.

This tokenization should work fairly well for **c family** of languages, which are widely used.

The uniform distribution of spaces and lineseps is also generated from the same buffer.

Note. the same seed is used to generate reproducible randomness.

### Measurement

n keystrokes of `--samples` is performed.

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

---

## Cool, pictures

---

## Analysis

Please keep in mind that this is purely a synthetic benchmark, which definitely is one of those **need context to interpret** type of things.

There is **no good way** to measure _real speed_ across frameworks, raw numbers here come with big caveats.

### Study design limitations

#### Streaming completion

Streaming completion is very good for time to first result (_TTFR_), but it presents us with an issue:

While the fast sources will return right away, the slower ones might never make it before the next keystroke.

This has the funny effect of removing the influence of slower sources entirely, which is disastrous for study integrity.

The mitigation is actually to set the script to **type unrealistically slow**, enough so that the LSP servers can catch up, which is quite unfortunate.

### Fast on paper != fast IRL

The most responsive frameworks are not necessarily the fastest ones, because **humans still have to pick the results**.

For example the streaming completion approach actually has severe trade offs infavor of faster _TTFR_:

#### Ranking

Having suboptimal ranking is BAD, it pushes work _from fast machines onto slow humans_.

The streaming approach has to be additive, because its too disruptive to shift existing menu items around.

Therefore it is limited to sorting only within stream batches, and to make things worse, _slower batches typically contain higher quality results_.

That means better results will often end up at the bottom, necessitating more work for humans.

#### Limiting

This is a direct consequence of limited ranking optimizations.

Because the framework have no idea how much each source will send, it has the dilemma of either sending too many results or too little.

Sending too many results in early batches from likely inferior sources will waste the users time, and sending too little will obscure potentially useful completions.

#### Clarity on when / if results will come in

Having streaming completions also means that the framework is likely to inadvertently train the users to wait for more complex and therefore slower sources.

### Conclusion

There is never going to be a closed form solution to "what is the fastest framework", because of the trade offs outlined above.

A toy example of a degenerate framework that returns a single fixed `👌` emoji will probably beat anything out there in terms of raw speed, but it is utterly useless.

**The results of this repo must be considered alongside inextricably human measure to be useful**
