options(java.parameters = "-Xmx24g")

library(feather)
library(FSelector)
library(dplyr)

subsample = function(df) {
  #df = df[df$itp < 4 | (df$itp > 45 & df$itp < 50) | df$itp > 107,]
  df = df[df$itp == 3 | df$itp == 47 | df$itp == 108,]
  return(df)
}

testCFS = function(df) {
  cat('Most important variables are displayed first:', '\n')
  independent_variables = c('pressure', 'temperature', 'salinity', 'month', 'freezing_point_delta', 'season')

    while(length(independent_variables) > 0) {
      f = as.formula(
        paste('radius0_bin ~ ', paste(independent_variables, collapse = '+'), sep='')
      )
      
      variables = cfs(f, df)
      
      cat('Selected variables', '\n')
      cat(variables, '\n')
      cat('\n')
      
      independent_variables = independent_variables[! independent_variables %in% variables]
    }
    
    cat('Done', '\n')
}

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

set.seed(2019)

df = read_feather('/home/tloureiro/projects/arctic-analysis/data/produced-csvs/clean_final.feather')

df_balanced = balanceDatasetByDV(df, 1)
df_subsampled = subsample(df)

remove(df)

#CFS
cat('Running CFS against the subsampled dataset', '\n')
testCFS(df_subsampled)

cat('Running CFS against balanced dataset', '\n')
testCFS(df_balanced)

#Information Gain
cat('Running Information Gain against the subsampled dataset', '\n')
information.gain(radius0_bin ~ pressure + temperature + salinity + month + freezing_point_delta + season, df_subsampled)

cat('Running Information Gain against the balanced dataset', '\n')
information.gain(radius0_bin ~ pressure + temperature + salinity + month + freezing_point_delta + season, df_balanced)

#Chi Square
cat('Running Chi Squared against the subsampled dataset', '\n')
chi.squared(radius0_bin ~ pressure + temperature + salinity + month + freezing_point_delta + season, df_subsampled)

cat('Running Chi Squared against the balanced dataset', '\n')
chi.squared(radius0_bin ~ pressure + temperature + salinity + month + freezing_point_delta + season, df_balanced)


