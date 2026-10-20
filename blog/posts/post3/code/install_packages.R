packages <- c('readr','ggplot2','scales')
missing <- packages[!vapply(packages,requireNamespace,logical(1),quietly=TRUE)]
if (length(missing)) install.packages(missing,repos='https://cloud.r-project.org')
message('All analysis dependencies are available.')
