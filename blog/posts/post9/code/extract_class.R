args <- commandArgs(trailingOnly=TRUE)
x <- readxl::read_excel(args[1]); stopifnot(nrow(x)==45, all(complete.cases(x)), all(sapply(x,is.numeric)))
write.csv(x,args[2],row.names=FALSE)
d <- x$portfolio2-x$portfolio1
print(c(n=length(d),mean1=mean(x$portfolio1),mean2=mean(x$portfolio2),difference=mean(d),positive=sum(d>0)))
print(t.test(d))
