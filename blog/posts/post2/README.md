# Blog Post 2: Hacker News Technical Skills

This project analyzes technical skills mentioned in the September 2026 Hacker News "Who is hiring?" thread.

## Data Source

The data comes from the September 2026 Hacker News "Who is hiring?" thread.

## Method

The analysis uses the R package `rvest` to scrape publicly available job-posting text from Hacker News.

At the time of analysis, the page contained 409 comments. Replies were filtered out by keeping only top-level comments, leaving 268 job postings for analysis.

The text was cleaned and searched for a predefined set of technical skills. Each skill was counted at most once per job posting.

## Required R Packages

- rvest
- dplyr
- stringr
- ggplot2

## Reproduction

Open `index.qmd` in RStudio and render the document.

The scraping, data cleaning, skill-count analysis, and visualization are generated programmatically from the code in `index.qmd`.