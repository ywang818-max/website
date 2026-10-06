# Blog 2: Technical skill mentions in Hacker News hiring posts

## Question and source

Which technologies appear frequently in the September 2026 HN hiring thread, and how can job seekers use this to investigate learning priorities?

Source: https://news.ycombinator.com/item?id=49522897
Snapshot: October 6, 2026. The page had 404 comment rows, including 263 top-level rows. Excluding missing/empty text and duplicate IDs leaves 253 analyzed posts. Replies are excluded. A top-level comment may cover multiple positions; it is not a count of individual vacancies or verified mandatory requirements.

## Files

- `index.qmd`: readable article, without executable code or printed data.
- `code/analyze.R`: rvest scraping, comment filtering, keyword matching, summaries, and saved chart.
- `data/raw/retrieval.txt`: source and snapshot provenance.
- `data/raw/thread.html`: local HTML cache, excluded from Git by `.gitignore`.
- `data/processed/skill_mentions.csv`: frozen public replication dataset with one row per comment ID and one binary indicator per predefined technology. No full posting text or contact information is included.
- `results/skill_counts.csv`, `results/sample_summary.csv`: aggregate counts, shares, and two co-mention totals.
- `results/skill_mentions.png`: saved substantive chart.
- `results/session-info.txt`: R/package versions used.

## Reproduction

Requires R and `rvest`, `dplyr`, `stringr`, `ggplot2`, `readr`, `scales`, and `xml2`.

```r
install.packages(c('rvest','dplyr','stringr','ggplot2','readr','scales','xml2'))
```

From the website repository root:

```sh
cd blog/posts/post2
Rscript code/analyze.R
```

When local raw HTML exists, the script reconstructs indicators with rvest. In a fresh clone without HTML, it uses the frozen indicators to reproduce the October 6 results offline. To collect a new snapshot with rvest:

```sh
Rscript code/analyze.R --download
```

The live thread changes, so a new download can change counts. Labels currently document the October 6 snapshot; update the chart, article, and provenance together if refreshing later. Each technology is counted at most once per post; shares use the same denominator of 253. Co-mentions are intersections of the two binary indicators. The top ten are selected deterministically by count and then alphabetically. The conservative Go pattern matches only 'golang'; SQL and JavaScript counts likewise do not automatically include every related database or framework name.

## Access practices

The source page is public and its robots.txt does not disallow the item URL; it specifies a 30-second crawl delay. The download mode waits 30 seconds and makes one request, caches the response, and avoids parallel fetching. It does not access login, vote, reply, or other disallowed routes and does not bypass authentication, CAPTCHAs, paywalls, or rate limits. Stop if the server denies access. Cached/offline analysis makes no web requests. Robots reference: https://news.ycombinator.com/robots.txt

The predefined keyword list is in the script. These indicators measure text mentions, not requirements, worker demand, proficiency, job placement, or salary effects. This recruiting channel is not representative of the whole labor market.
