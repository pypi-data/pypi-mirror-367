# Clothoids Python Bindings

This directory contains the Python bindings for the Clothoids library.

## Installation

Simply install via pip:

```bash
pip install Clothoids
```

### Build from source

If a pip package isn't available, or you simply want to, you can build from source. Note that you need to have the following installed on your system:

- ruby >=2.6 with the following gems: rake, colorize, rubyzip;
- CMake with ninja;
- python 3.8-13 (other versions are untested).

Once those requirements are installed, simply:

```bash
git clone --branch stable --depth 1 https://github.com/SebastianoTaddei/Clothoids.git
cd Clothoids
ruby setup.rb
rake
pip install -e .
```

## Usage

The Python bindings provide a simple interface to the Clothoids C++ library. Look at the `example.py` file for a simple example.

## Authors

These binding were brought to you by:

- [Sebastiano Taddei](https://github.com/SebastianoTaddei)
- [Gabriele Masina](https://github.com/masinag)
