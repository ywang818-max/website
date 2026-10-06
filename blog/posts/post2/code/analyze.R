# Run from post2: Rscript code/analyze.R [--download]
suppressPackageStartupMessages({library(rvest);library(dplyr);library(stringr);library(ggplot2);library(readr)})
args <- commandArgs(trailingOnly=FALSE)
script <- sub('^--file=', '', args[grepl('^--file=',args)][1])
script <- gsub('~+~',' ',script,fixed=TRUE)
root <- dirname(dirname(normalizePath(script)))
path <- function(...) file.path(root,...)
for(d in c('data/raw','data/processed','results')) dir.create(path(d),recursive=TRUE,showWarnings=FALSE)
url <- 'https://news.ycombinator.com/item?id=49522897'
cache <- path('data/raw/thread.html')
frozen <- path('data/processed/skill_mentions.csv')
use_frozen <- !file.exists(cache) && file.exists(frozen) && !('--download' %in% commandArgs(trailingOnly=TRUE))
if(use_frozen) {
  features <- read_csv(frozen,show_col_types=FALSE)
  original_summary <- read_csv(path('results/sample_summary.csv'),show_col_types=FALSE)
  raw_comments <- original_summary$raw_comments[1]
  n_posts <- nrow(features)
} else {
if('--download' %in% commandArgs(trailingOnly=TRUE) || !file.exists(cache)) {
  # One public-page request; no login, pagination, parallel fetching, or bypasses.
  Sys.sleep(30) # Honor the crawl delay published in robots.txt.
  page <- read_html(url)
  stopifnot(grepl('Who is hiring', html_text2(html_element(page,'title'))))
  xml2::write_html(page,cache)
  writeLines(c(paste('Source:',url),paste('Downloaded:',Sys.time())),path('data/raw/retrieval.txt'))
} else page <- read_html(cache)
comments <- html_elements(page,'tr.comtr')
posts <- tibble(id=html_attr(comments,'id'),indent=html_element(comments,'td.ind') |> html_attr('indent') |> as.integer(),text=html_element(comments,'.commtext') |> html_text2()) |>
  filter(indent==0,!is.na(text),str_trim(text)!='') |> distinct(id,.keep_all=TRUE)
# Keep the original list for comparability. Go is conservatively matched as 'golang'.
patterns <- c(Python='\\bpython\\b',SQL='\\bsql\\b',JavaScript='\\bjavascript\\b',TypeScript='\\btypescript\\b',React='\\breact\\b',AWS='\\baws\\b',GCP='\\bgcp\\b|google cloud',Azure='\\bazure\\b',Docker='\\bdocker\\b',Kubernetes='\\bkubernetes\\b|\\bk8s\\b',Terraform='\\bterraform\\b',PostgreSQL='\\bpostgresql\\b|\\bpostgres\\b',PyTorch='\\bpytorch\\b',Rust='\\brust\\b',Java='\\bjava\\b',Go='\\bgolang\\b')
features <- tibble(comment_id=posts$id)
for(skill in names(patterns)) features[[skill]] <- as.integer(str_detect(str_to_lower(posts$text),regex(patterns[[skill]],ignore_case=TRUE)))

raw_comments <- length(comments)
n_posts <- nrow(posts)
}
write_csv(features,path('data/processed/skill_mentions.csv'))
counts <- tibble(skill=names(features)[-1],count=as.integer(colSums(features[-1])),share=as.integer(colSums(features[-1]))/n_posts) |> arrange(desc(count),skill)
write_csv(counts,path('results/skill_counts.csv'))
write_csv(tibble(raw_comments=raw_comments,top_level_nonempty_posts=n_posts,python_postgresql=sum(features$Python & features$PostgreSQL),typescript_react=sum(features$TypeScript & features$React)),path('results/sample_summary.csv'))
top <- head(counts,10)
plot <- ggplot(top,aes(x=reorder(skill,count),y=count))+geom_col(fill='#155ab6',width=.65)+geom_text(aes(label=paste0(count,' (',scales::percent(share,accuracy=.1),')')),hjust=-.12,size=3.6)+coord_flip()+scale_y_continuous(expand=expansion(mult=c(0,.27)))+labs(title='Which technologies appear most often?',subtitle=paste0(n_posts,' nonempty top-level posts · September 2026 HN hiring thread'),x=NULL,y='Number of posts mentioning the technology',caption='Source: Hacker News. Retrieved Oct 6, 2026. Each technology counted once per post.')+theme_minimal(base_size=12)+theme(panel.grid.major.y=element_blank(),plot.title=element_text(face='bold'),plot.caption=element_text(hjust=0))
ggsave(path('results/skill_mentions.png'),plot,width=9,height=6,dpi=180)
writeLines(capture.output(sessionInfo()),path('results/session-info.txt'))
print(counts);print(read_csv(path('results/sample_summary.csv'),show_col_types=FALSE))
