library(feather)
library(dplyr)

df = read_feather('/home/tloureiro/projects/arctic-analysis/data/produced-csvs/clean_final.feather')

summary(df$radius0_bin)
barplot(summary(df$radius0_bin))