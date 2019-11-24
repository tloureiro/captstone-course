options(java.parameters = "-Xmx28g")

library(feather)
library(FSelector)
library(dplyr)
library(caret)

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

set.seed(2019)

f = radius0_bin ~ pressure + temperature + salinity + month + freezing_point_delta + season

df = read_feather('/home/tloureiro/projects/arctic-analysis/data/produced-csvs/clean_final.feather')

#subsample keeping the proportions (limited memory to run cfs)
indices = createDataPartition(df$radius0_bin, p=0.7, list = FALSE)
df = df[indices,]

#CFS
cat('Running CFS against the subsampled dataset', '\n')
testCFS(df)

#Information Gain
cat('Running Information Gain against the subsampled dataset', '\n')
information.gain(f, df)

#Chi Square
cat('Running Chi Squared against the subsampled dataset', '\n')
chi.squared(f, df)


#comparison
barplot(c(3, 3, 2, 2, 2, 1), names.arg = c('month', 'season', 'fpd', 'temperature', 'salinity', 'pressure'), main = 'CFS (by reverse order)')
barplot(c(0.14, 0.09, 0.02, 0.01, 0.01, 0), names.arg = c('month', 'season', 'fpd', 'temperature', 'salinity', 'pressure'), main = 'Information Gain')
barplot(c(0.31, 0.22, 0.13, 0.12, 0.11, 0.01), names.arg = c('month', 'season', 'fpd', 'temperature', 'salinity', 'pressure'), main = 'Chi-squared')

