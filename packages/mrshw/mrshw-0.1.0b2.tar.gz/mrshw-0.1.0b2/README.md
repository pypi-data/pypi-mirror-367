# mrsh

Thin, ctypes-based Python bindings for the [mrsh CLI tool](https://github.com/w4term3loon/mrsh).

---

## Installation

Install from PyPI:

```bash
pip install mrshw
```

Or directly from GitHub (tagged release `v0.1.0b1`):

```bash
pip install git+https://github.com/w4term3loon/mrsh.git@v0.1.0b1
```

---

## Quickstart

```python
import mrshw as mrsh

# Single-fingerprint API
fp = mrsh.fp("path/to/file.bin")
print(str(fp))            # metadata + hex-encoded Bloom filters
print(fp.meta())          # namedtuple: (name, filesize, filter_count)

# Fingerprint-list API
fpl = mrsh.fpl()
fpl.add("a.bin")
fpl.add(("b.bin", "label_b"))
print(str(fpl))           # multiple lines, one per fingerprint

# Compare all fingerprints in the list
results = fpl.compare_all(threshold=10)
for cmp in results:
    print(cmp.hash1, cmp.hash2, cmp.score)
```

---

## License

* **Wrapper:** MIT License (see [LICENSE](LICENSE)).
* **Underlying C code:** Apache License 2.0 (see github repository for details).

