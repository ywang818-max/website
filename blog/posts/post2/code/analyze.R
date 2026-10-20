# Reproduce from any working directory:
# Rscript /path/to/website/blog/posts/post2/code/analyze.R
# --refresh downloads a NEW snapshot into ignored refresh directories.
args <- commandArgs(trailingOnly = TRUE)
if ('--help' %in% args) {
  cat('Usage: Rscript code/analyze.R [--refresh]\nDefault: offline submitted snapshot -> results/\n--refresh: new public page -> data/refresh/ and results/refresh/\n')
  quit(status = 0)
}
if (length(setdiff(args, '--refresh'))) stop('Unknown option. Use --help.')
script_arg <- grep('^--file=', commandArgs(FALSE), value = TRUE)
if (length(script_arg) != 1L) stop('Run with Rscript, as shown in README.md.')
script <- gsub('~+~', ' ', sub('^--file=', '', script_arg), fixed = TRUE)
root <- dirname(dirname(normalizePath(script, mustWork = TRUE)))
path <- function(...) file.path(root, ...)
refresh <- '--refresh' %in% args
required <- c('readr', 'ggplot2', 'scales')
if (refresh) required <- c(required, 'rvest', 'xml2', 'stringr')
missing <- required[!vapply(required, requireNamespace, logical(1), quietly = TRUE)]
if (length(missing)) stop('Missing R packages: ', paste(missing, collapse=', '), '. Run code/install_packages.R first; see README.md.')

url <- 'https://news.ycombinator.com/item?id=49522897'
if (!refresh) {
  # Immutable inputs; results/ can be removed before a full rebuild.
  input <- path('data', 'processed', 'skill_mentions.csv')
  metadata <- path('data', 'snapshot_metadata.csv')
  manifest <- read.csv(path('data', 'snapshot_checksums.csv'), stringsAsFactors=FALSE)
  for (i in seq_len(nrow(manifest))) {
    f <- path(manifest$file[i])
    if (!file.exists(f) || unname(tools::md5sum(f)) != manifest$md5[i]) {
      stop('Submitted snapshot missing or changed: ', manifest$file[i], '. Restore it from GitHub.')
    }
  }
  features <- read.csv(input, colClasses = c(comment_id='character'), check.names=FALSE)
  summary_input <- read.csv(metadata)
  raw_comments <- summary_input$raw_comments[1]
  retrieved <- summary_input$retrieved[1]
  out <- path('results')
} else {
  # One request after the advertised crawl delay. No login or restriction bypass.
  rawdir <- path('data', 'refresh')
  dir.create(rawdir, recursive=TRUE, showWarnings=FALSE)
  message('Waiting 30 seconds before one public-page request ...')
  Sys.sleep(30)
  page <- rvest::read_html(url)
  title <- rvest::html_text2(rvest::html_element(page, 'title'))
  if (!grepl('Who is hiring', title, fixed=TRUE)) stop('Unexpected page; no analysis written.')
  xml2::write_html(page, file.path(rawdir, 'thread.html'))
  comments <- rvest::html_elements(page, 'tr.comtr')
  ids <- rvest::html_attr(comments, 'id')
  indents <- suppressWarnings(as.integer(rvest::html_attr(rvest::html_element(comments, 'td.ind'), 'indent')))
  texts <- rvest::html_text2(rvest::html_element(comments, '.commtext'))
  keep <- !is.na(indents) & indents==0 & !is.na(texts) & nzchar(trimws(texts)) & !is.na(ids)
  posts <- data.frame(comment_id=ids[keep], text=texts[keep], stringsAsFactors=FALSE)
  posts <- posts[!duplicated(posts$comment_id), ]
  if (!nrow(posts)) stop('No usable posts; inspect the page before trying again.')
  patterns <- c(Python='\\bpython\\b', SQL='\\bsql\\b', JavaScript='\\bjavascript\\b', TypeScript='\\btypescript\\b', React='\\breact\\b', AWS='\\baws\\b', GCP='\\bgcp\\b|google cloud', Azure='\\bazure\\b', Docker='\\bdocker\\b', Kubernetes='\\bkubernetes\\b|\\bk8s\\b', Terraform='\\bterraform\\b', PostgreSQL='\\bpostgresql\\b|\\bpostgres\\b', PyTorch='\\bpytorch\\b', Rust='\\brust\\b', Java='\\bjava\\b', Go='\\bgolang\\b')
  features <- posts['comment_id']
  for (skill in names(patterns)) features[[skill]] <- as.integer(stringr::str_detect(tolower(posts$text), patterns[[skill]]))
  raw_comments <- length(comments)
  retrieved <- format(as.Date(Sys.time(), tz='America/New_York'), '%B %d, %Y')
  readr::write_csv(features, file.path(rawdir, 'skill_mentions.csv'))
  writeLines(c(paste('Source:',url), paste('Retrieved:',retrieved), paste('Raw comment rows:',raw_comments)), file.path(rawdir,'retrieval.txt'))
  out <- path('results', 'refresh')
}

skills <- c('Python','SQL','JavaScript','TypeScript','React','AWS','GCP','Azure','Docker','Kubernetes','Terraform','PostgreSQL','PyTorch','Rust','Java','Go')
if (!identical(names(features), c('comment_id',skills))) stop('Unexpected indicator columns.')
if (!nrow(features) || anyNA(features) || anyDuplicated(features$comment_id)) stop('Missing values or duplicate IDs in inputs.')
if (!all(as.matrix(features[skills]) %in% c(0,1))) stop('Indicators must be 0 or 1.')
n_posts <- nrow(features)
counts <- data.frame(skill=skills, count=as.integer(colSums(features[skills])), stringsAsFactors=FALSE)
counts$share <- counts$count/n_posts
counts <- counts[order(-counts$count, counts$skill), ]
summary <- data.frame(raw_comments=raw_comments, top_level_nonempty_posts=n_posts,
                      python_postgresql=sum(features$Python & features$PostgreSQL),
                      typescript_react=sum(features$TypeScript & features$React))
dir.create(out, recursive=TRUE, showWarnings=FALSE)
readr::write_csv(counts, file.path(out,'skill_counts.csv'))
readr::write_csv(summary, file.path(out,'sample_summary.csv'))

top <- head(counts, 10)
top$skill <- factor(top$skill, levels=rev(top$skill))
p <- ggplot2::ggplot(top, ggplot2::aes(x=skill,y=count)) +
  ggplot2::geom_col(fill='#155ab6',width=.65) +
  ggplot2::geom_text(ggplot2::aes(label=paste0(count,' (',scales::percent(share,accuracy=.1),')')),hjust=-.12,size=3.6) +
  ggplot2::coord_flip() + ggplot2::scale_y_continuous(expand=ggplot2::expansion(mult=c(0,.27))) +
  ggplot2::labs(title='Which technologies appear most often?',subtitle=paste0(n_posts,' nonempty top-level posts · September 2026 HN hiring thread'),x=NULL,y='Number of posts mentioning the technology',caption=paste0('Source: Hacker News. Retrieved ',retrieved,'. Each technology counted once per post.')) +
  ggplot2::theme_minimal(base_size=12) +
  ggplot2::theme(panel.grid.major.y=ggplot2::element_blank(),plot.title=ggplot2::element_text(face='bold'),plot.caption=ggplot2::element_text(hjust=0))
ggplot2::ggsave(file.path(out,'skill_mentions.png'),p,width=9,height=6,dpi=180)
writeLines(capture.output(sessionInfo()),file.path(out,'session-info.txt'))
message('Complete: ',n_posts,' posts; outputs saved to ',out)
print(counts, row.names=FALSE)
