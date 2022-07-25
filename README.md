# bencharts

## Structure

Given a metadata file in JSON format and a data file in JSON format.
A Benchart is composed of

### loader.py
Takes input files from benchmarking tools and normalizes their data and
metadata for consumption and processing.

Primary functionality includes `flatten()`ing nested JSON data and adding keys
will NULL values so that all runs in a group have the same keys.

### metadata.py
Defines `RunMetadata` object.

### benchart.py
Primary processing and group logic. Builds a tree of different `Run`s based on
grouping their metadata.
Defines a `Run`, which has `RunMetadata` and data.
Defines a `Step` -- only used internally for implementation.
Defines a `BenchArt` and `RunGroup`

### renderer.py
Does rendering. Expects processed output from the benchart engine. Can render
output in various ways.
Defines a `Result`. Uses `RunGroup`

### run.py
Takes input files, processes them with the loader, makes a `Benchart`,
partitions it, runs it, defines renderers for it, renders it or prints a tree
version.
