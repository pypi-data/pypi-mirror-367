# Chik Proof of Space
![Build](https://github.com/Chik-Network/chikpos/actions/workflows/build-test-cplusplus.yml/badge.svg)
![Wheels](https://github.com/Chik-Network/chikpos/actions/workflows/build-wheels.yml/badge.svg)
![PyPI](https://img.shields.io/pypi/v/chikpos?logo=pypi)
![PyPI - Format](https://img.shields.io/pypi/format/chikpos?logo=pypi)
![GitHub](https://img.shields.io/github/license/Chik-Network/chikpos?logo=Github)
[![Coverage Status](https://coveralls.io/repos/github/Chik-Network/chikpos/badge.svg?branch=main)](https://coveralls.io/github/Chik-Network/chikpos?branch=main)

Chik's proof of space is written in C++. Includes a plotter, prover, and
verifier. It exclusively runs on 64 bit architectures. Read the
[Proof of Space document](https://www.chiknetwork.com/wp-content/uploads/2022/09/Chik_Proof_of_Space_Construction_v1.1.pdf) to
learn about what proof of space is and how it works.

## C++ Usage Instructions

### Compile

```bash
# Requires cmake 3.14+

mkdir -p build && cd build
cmake ../
cmake --build . -- -j 6
```

## Static Compilation With glibc
### Statically compile ProofOfSpace
```bash
mkdir -p build && cd build
cmake -DBUILD_PROOF_OF_SPACE_STATICALLY=ON ../
cmake --build . -- -j 6
```

### Run tests

```bash
./RunTests
```

### CLI usage

```bash
./ProofOfSpace -k 25 -f "plot.dat" -m "0x1234" create
./ProofOfSpace -k 25 -f "final-plot.dat" -m "0x4567" -t TMPDIR -2 SECOND_TMPDIR create
./ProofOfSpace -f "plot.dat" prove <32 byte hex challenge>
./ProofOfSpace -k 25 verify <hex proof> <32 byte hex challenge>
./ProofOfSpace -f "plot.dat" check <iterations>
```

### Benchmark

```bash
time ./ProofOfSpace -k 25 create
```


### Hellman Attacks usage

There is an experimental implementation which implements some of the Hellman
Attacks that can provide significant space savings for the final file.


```bash
./HellmanAttacks -k 18 -f "plot.dat" -m "0x1234" create
./HellmanAttacks -f "plot.dat" check <iterations>
```

## Python binding

Python bindings are provided in the python-bindings directory.

### Install

```bash
python3 -m venv .venv
. .venv/bin/activate
pip3 install .
```

### Run python tests

Testings uses pytest. Linting uses flake8 and mypy.

```bash
py.test ./tests -s -v
```

# Rust binding

Finally, Rust bindings are provided, but only validation of proofs of space is supported, and it cannot be used to make plots or create proofs for plots.

## ci Building
The primary build process for this repository is to use GitHub Actions to
build binary wheels for MacOS, Linux (x64 and aarch64), and Windows and publish
them with a source wheel on PyPi. See `.github/workflows/build.yml`. CMake uses
[FetchContent](https://cmake.org/cmake/help/latest/module/FetchContent.html)
to download [pybind11](https://github.com/pybind/pybind11). Building is then
managed by [cibuildwheel](https://github.com/joerick/cibuildwheel). Further
installation is then available via `pip install chikpos` e.g.

## Contributing and workflow
Contributions are welcome and more details are available in chik-blockchain's
[CONTRIBUTING.md](https://github.com/Chik-Network/chik-blockchain/blob/main/CONTRIBUTING.md).

The main branch is usually the currently released latest version on PyPI.
Note that at times chikpos will be ahead of the release version that
chik-blockchain requires in it's main/release version in preparation for a
new chik-blockchain release. Please branch or fork main and then create a
pull request to the main branch. Linear merging is enforced on main and
merging requires a completed review. PRs will kick off a GitHub actions ci build
and analysis of chikpos at
[lgtm.com](https://lgtm.com/projects/g/Chik-Network/chikpos/?mode=list). Please
make sure your build is passing and that it does not increase alerts at lgtm.
