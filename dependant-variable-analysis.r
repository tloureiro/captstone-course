options(java.parameters = "-Xmx24g")

library(feather)
library(dplyr)

balanceDatasetByDV = function(df, lower_limit_fraction) {
  
  lower_limit = min(
    nrow(df[df$radius0_bin == '0-25',]), 
    nrow(df[df$radius0_bin == '25-50',]), 
    nrow(df[df$radius0_bin == '50-75',]), 
    nrow(df[df$radius0_bin == '75-100',])
  )
  
  df = rbind(
    sample_n(df[df$radius0_bin == '0-25',], lower_limit/lower_limit_fraction), 
    sample_n(df[df$radius0_bin == '25-50',], lower_limit/lower_limit_fraction), 
    sample_n(df[df$radius0_bin == '50-75',], lower_limit/lower_limit_fraction), 
    sample_n(df[df$radius0_bin == '75-100',], lower_limit/lower_limit_fraction)
  )
  
  return(df)
}

df = read_feather('/home/tloureiro/projects/arctic-analysis/data/produced-csvs/clean_final.feather')

summary(df$radius0_bin)
barplot(summary(df$radius0_bin))


df_balanced = balanceDatasetByDV(df, 1)

summary(df_balanced$radius0_bin)
barplot(summary(df_balanced$radius0_bin))
