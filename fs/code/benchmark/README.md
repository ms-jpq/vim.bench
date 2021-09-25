# Benchmarks

{% for benchmark in BENCHMARKS %}

---

### {{ benchmark.framework }}

**{{ benchmark.data_file }}**

| Key         | Value                        |
| ----------- | ---------------------------- |
| Completions | {{ benchmark.stats.items }}  |
| Mean        | {{ benchmark.stats.mean }}ms |
| Q0          | {{ benchmark.stats.q0 }}ms   |
| Q50         | {{ benchmark.stats.q50 }}ms  |
| Q95         | {{ benchmark.stats.q95 }}ms  |
| Q100        | {{ benchmark.stats.q100 }}ms |

<img src="{{ benchmark.plot | b64_img }}" />

{% endfor %}
