# website

## Blog 2: web scraping and skills analysis

Start with [the Blog 2 README](blog/posts/post2/README.md) for the exact folder map, installation steps, reproduction commands, and expected outputs.

From this website repository root:

```sh
Rscript blog/posts/post2/code/install_packages.R
Rscript blog/posts/post2/code/analyze.R
```

The default reproduces the submitted snapshot offline and saves all results programmatically. Optional `--refresh` uses rvest to collect a new snapshot into separate folders. See [clean-copy reproduction evidence](blog/posts/post2/REPRODUCTION_CHECK.md).

## Blog 3: CPS education and labor-market outcomes

Start with [the Blog 3 README](blog/posts/post3/README.md) for the full directory map, expected outputs, data definitions, and both reproduction modes.

From this website repository root:

```sh
Rscript blog/posts/post3/code/install_packages.R
Rscript blog/posts/post3/code/analyze.R
```

Default reproduction uses committed grouped CPS inputs and works offline. The optional `--microdata FILE` mode reconstructs all calculations from an authorized local IPUMS extract; see the [raw-data instructions](blog/posts/post3/data/raw/README.md). All four figures and tables are generated and saved programmatically. See [verification evidence](blog/posts/post3/REPRODUCTION_CHECK.md).

## Blog 5: GIS and rental affordability

Start with [the Blog 5 README](blog/posts/post5/README.md) for the full file map, archived public data, definitions, source hashes and offline replication instructions.

```sh
python -m pip install -r blog/posts/post5/code/requirements.txt
python blog/posts/post5/code/analyze.py
```

The script generates all maps and county tables from archived ACS and Census TIGERweb inputs. See [clean-copy verification](blog/posts/post5/REPRODUCTION_CHECK.md) and the [published article](https://ywang818-max.github.io/website/blog/posts/post5/).

## Blog 6: PSID parent–child matching with Python and SQL

Start with [the Blog 6 README](blog/posts/post6/README.md) for the exact input requirements, folder map, SQL matching steps and replication commands. The [published tutorial](https://ywang818-max.github.io/website/blog/posts/post6/) compares single-year and multi-year IGE estimates and age at measurement on the same 3,108 pairs.

Public files include code, variable metadata, CPI inputs and aggregate outputs. PSID microdata and individual matches are not distributed; replication requires independently authorized local inputs. See [the input guide](blog/posts/post6/data/README.md) and [clean-copy verification](blog/posts/post6/REPRODUCTION_CHECK.md).

## Blog 7: Interactive Plotly county rent-budget explorer

Start with [the Blog 7 README](blog/posts/post7/README.md) for source definitions, exact file paths, reproduction commands and tested interactions. The [published article](https://ywang818-max.github.io/website/blog/posts/post7/) uses budget and market-size filters, county inspection, rent uncertainty and a synchronized table.

Run `python3 blog/posts/post7/code/build.py` from this repository root. The archived ACS response and pinned local Plotly.js runtime are included; the standard-library build runs offline.
