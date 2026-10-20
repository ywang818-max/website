# Install only missing dependencies; run once before analysis.
packages <- c('readr','ggplot2','scales','rvest','xml2','stringr')
missing <- packages[!vapply(packages,requireNamespace,logical(1),quietly=TRUE)]
if (length(missing)) install.packages(missing, repos='https://cloud.r-project.org')
message('All required packages are available.')
