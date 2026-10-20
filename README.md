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
