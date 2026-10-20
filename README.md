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
