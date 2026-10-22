# Default: reproduce published aggregate inputs offline from any working directory.
# Full pipeline: Rscript code/analyze.R --microdata /path/to/ipums.csv.gz
args <- commandArgs(trailingOnly=TRUE)
if ('--help' %in% args) {
  cat('Usage: Rscript code/analyze.R [--microdata FILE]\nDefault -> results/ from public aggregate cells\n--microdata -> results/microdata/ from a local IPUMS extract\n');quit(status=0)
}
if (length(args) && !(length(args)==2 && args[1]=='--microdata')) stop('Use --help for supported arguments.')
script <- sub('^--file=','',grep('^--file=',commandArgs(FALSE),value=TRUE))
if (length(script)!=1) stop('Run with Rscript; see README.md.')
script <- gsub('~+~',' ',script,fixed=TRUE)
root <- dirname(dirname(normalizePath(script,mustWork=TRUE)))
path <- function(...) file.path(root,...)
packages <- c('readr','ggplot2','scales')
missing <- packages[!vapply(packages,requireNamespace,logical(1),quietly=TRUE)]
if (length(missing)) stop('Missing packages: ',paste(missing,collapse=', '),'. Run code/install_packages.R.')
education_labels <- c('Less than high school','High school','Some college / Associate',"Bachelor's or higher")
valid_status <- c(10,12,21,22,32,34,36)

# This function is also the complete derivation of the committed aggregate cells.
aggregate_microdata <- function(input) {
  d <- readr::read_csv(input,show_col_types=FALSE)
  fields <- c('YEAR','MONTH','AGE','EDUC99','EMPSTAT','LABFORCE','WTFINL')
  if (!all(fields %in% names(d))) stop('Missing required IPUMS variables; see data/raw/README.md.')
  raw_n <- nrow(d)
  keep <- with(d,YEAR==2026 & MONTH==7 & AGE>=25 & AGE<=64 & EDUC99 %in% c(1,4:11,13:18) & EMPSTAT %in% valid_status & LABFORCE %in% c(1,2) & is.finite(WTFINL) & WTFINL>0)
  d <- d[!is.na(keep) & keep, ]
  if (!nrow(d)) stop('No eligible July 2026 adults. Check the selected extract.')
  stopifnot(all((d$LABFORCE==2)==(d$EMPSTAT %in% c(10,12,21,22))))
  edu <- ifelse(d$EDUC99<10,1L,ifelse(d$EDUC99==10,2L,ifelse(d$EDUC99<=14,3L,4L)))
  cells <- aggregate(data.frame(unweighted_n=rep(1,nrow(d)),weight_sum=d$WTFINL),by=list(education_code=edu,EMPSTAT=d$EMPSTAT),FUN=sum)
  grid <- expand.grid(education_code=1:4,EMPSTAT=valid_status)
  cells <- merge(grid,cells,all.x=TRUE)
  cells$unweighted_n[is.na(cells$unweighted_n)] <- 0
  cells$weight_sum[is.na(cells$weight_sum)] <- 0
  cells <- cells[order(cells$education_code,cells$EMPSTAT), ]
  attr(cells,'source_rows') <- raw_n
  cells
}

if (!length(args)) {
  manifest <- read.csv(path('data/snapshot_checksums.csv'),stringsAsFactors=FALSE)
  for (i in seq_len(nrow(manifest))) {
    f <- path(manifest$file[i])
    if (!file.exists(f) || unname(tools::md5sum(f))!=manifest$md5[i]) stop('Aggregate snapshot missing or changed: ',manifest$file[i])
  }
  cells <- read.csv(path('data/processed/education_status_cells.csv'))
  out <- path('results')
} else {
  input <- normalizePath(args[2],mustWork=TRUE)
  cells <- aggregate_microdata(input)
  out <- path('results/microdata')
}
stopifnot(nrow(cells)==28,!anyNA(cells),!anyDuplicated(cells[c('education_code','EMPSTAT')]),all(cells$education_code %in% 1:4),all(cells$EMPSTAT %in% valid_status),all(cells$weight_sum>=0),all(cells$unweighted_n>=0))
dir.create(out,recursive=TRUE,showWarnings=FALSE)
readr::write_csv(cells,file.path(out,'education_status_cells.csv'))

rates <- do.call(rbind,lapply(1:4,function(g) {
  s <- cells[cells$education_code==g,];total <- sum(s$weight_sum)
  lf <- sum(s$weight_sum[s$EMPSTAT %in% c(10,12,21,22)])
  emp <- sum(s$weight_sum[s$EMPSTAT %in% c(10,12)])
  unemp <- sum(s$weight_sum[s$EMPSTAT %in% c(21,22)])
  stopifnot(total>0,lf>0)
  data.frame(education=education_labels[g],unweighted_n=sum(s$unweighted_n),population_weight=total,labor_force_weight=lf,labor_force_participation=lf/total,employment_rate=emp/total,unemployment_rate=unemp/lf)
}))
stopifnot(all(abs(rates$employment_rate-rates$labor_force_participation*(1-rates$unemployment_rate))<1e-12))
readr::write_csv(rates,file.path(out,'education_rates.csv'))
reason_labels <- c('Unable to work','Other NILF','Retired')
reasons <- do.call(rbind,lapply(1:4,function(g) {
  s <- cells[cells$education_code==g,];total <- sum(s$weight_sum);nilf <- sum(s$weight_sum[s$EMPSTAT %in% c(32,34,36)])
  x <- s[match(c(32,34,36),s$EMPSTAT),]
  data.frame(education=education_labels[g],EMPSTAT=x$EMPSTAT,status=reason_labels,unweighted_n=x$unweighted_n,weighted_count=x$weight_sum,group_population=total,nilf_population=nilf,share_all_adults=x$weight_sum/total,share_nonparticipants=x$weight_sum/nilf)
}))
for (g in education_labels) stopifnot(abs(sum(reasons$share_all_adults[reasons$education==g])-(1-rates$labor_force_participation[rates$education==g]))<1e-12)
readr::write_csv(reasons,file.path(out,'nonparticipation_status.csv'))
gap <- reasons$share_all_adults[reasons$education==education_labels[1]]-reasons$share_all_adults[reasons$education==education_labels[4]]
participation_gap <- rates$labor_force_participation[4]-rates$labor_force_participation[1]
stopifnot(abs(sum(gap)-participation_gap)<1e-12)
readr::write_csv(data.frame(status=reason_labels,contribution_pp=100*gap,fraction_of_participation_gap=gap/participation_gap),file.path(out,'participation_gap_accounting.csv'))

# Same denominator for participation and employment; unemployment uses participants.
rates$education <- factor(rates$education,levels=education_labels)
plot_rate <- function(variable,title,subtitle,file,upper) {
  p <- ggplot2::ggplot(rates,ggplot2::aes(x=education,y=.data[[variable]])) + ggplot2::geom_col(fill='#155ab6',width=.6) + ggplot2::geom_text(ggplot2::aes(label=scales::percent(.data[[variable]],accuracy=.1)),hjust=-.15,size=4) + ggplot2::coord_flip() + ggplot2::scale_y_continuous(labels=scales::label_percent(),limits=c(0,upper),expand=ggplot2::expansion(mult=c(0,0))) + ggplot2::scale_x_discrete(limits=rev(education_labels)) + ggplot2::labs(title=title,subtitle=subtitle,x=NULL,y='Weighted share',caption='Source: IPUMS CPS, July 2026. Civilian adults ages 25–64. WTFINL person weights.') + ggplot2::theme_minimal(base_size=12) + ggplot2::theme(panel.grid.major.y=ggplot2::element_blank(),plot.title=ggplot2::element_text(face='bold'),plot.caption=ggplot2::element_text(hjust=0),plot.margin=ggplot2::margin(t=10,r=32,b=10,l=10))
  ggplot2::ggsave(file.path(out,file),p,width=9,height=4.8,dpi=180)
}
plot_rate('labor_force_participation','Labor-force participation by education','Denominator: all eligible adults in each education group','participation.png',1)
plot_rate('employment_rate','Employment-to-population ratio by education','Denominator: all eligible adults in each education group','employment.png',1)
plot_rate('unemployment_rate','Unemployment by education','Denominator: employed plus unemployed adults in each group','unemployment.png',.065)

reasons$education <- factor(reasons$education,levels=education_labels)
reasons$status <- factor(reasons$status,levels=c('Unable to work','Retired','Other NILF'))
p <- ggplot2::ggplot(reasons,ggplot2::aes(x=education,y=share_all_adults,fill=status)) + ggplot2::geom_col(width=.6,position=ggplot2::position_stack(reverse=TRUE)) + ggplot2::geom_text(ggplot2::aes(label=scales::percent(share_all_adults,accuracy=.1)),position=ggplot2::position_stack(vjust=.5,reverse=TRUE),size=3.4,color='#182335') + ggplot2::coord_flip() + ggplot2::scale_x_discrete(limits=rev(education_labels)) + ggplot2::scale_y_continuous(labels=scales::label_percent(),limits=c(0,.43),expand=ggplot2::expansion(mult=c(0,.01))) + ggplot2::scale_fill_manual(values=c('Unable to work'='#8fb8e8','Retired'='#efb76d','Other NILF'='#cbd2da')) + ggplot2::labs(title='Nonparticipation status by education',subtitle='Percent of ALL adults in each group; segments sum to the nonparticipation rate',x=NULL,y='Share of adults outside the labor force',fill=NULL,caption='Source: IPUMS CPS, July 2026. Ages 25–64; WTFINL. Other NILF does not identify caregiving.') + ggplot2::theme_minimal(base_size=12) + ggplot2::theme(panel.grid.major.y=ggplot2::element_blank(),legend.position='top',plot.title=ggplot2::element_text(face='bold'),plot.caption=ggplot2::element_text(hjust=0))
ggplot2::ggsave(file.path(out,'nonparticipation.png'),p,width=10,height=5.5,dpi=180)
writeLines(capture.output(sessionInfo()),file.path(out,'session-info.txt'))
message('Complete: ',sum(rates$unweighted_n),' eligible respondents; four saved figures. Outputs: ',out)
print(rates);print(data.frame(status=reason_labels,gap_pp=100*gap))
