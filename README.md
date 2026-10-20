# website

## Blog 2: web scraping and skills analysis

Start with [the Blog 2 README](blog/posts/post2/README.md) for the exact folder map, installation steps, reproduction commands, and expected outputs.

From this website repository root:

```sh
Rscript blog/posts/post2/code/install_packages.R
Rscript blog/posts/post2/code/analyze.R
```

The default reproduces the submitted snapshot offline and saves all results programmatically. Optional `--refresh` uses rvest to collect a new snapshot into separate folders. See [clean-copy reproduction evidence](blog/posts/post2/REPRODUCTION_CHECK.md).
