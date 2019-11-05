options(java.parameters = "-Xmx24g")

library(feather)
library(dplyr)
library(nnet)
library(caret)
library(rJava)
library(RWeka)

subsample = function(df) {
  #df = df[df$itp < 4 | (df$itp > 45 & df$itp < 50) | df$itp > 107,]
  df = df[df$itp == 3 | df$itp == 47 | df$itp == 108,]
  return(df)
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
#df_subsampled = subsample(df)
remove(df)

indices = createDataPartition(df_balanced$radius0_bin, p= 0.8, list = FALSE)
df_balanced_train = df_balanced[indices,]
df_balanced_test = df_balanced[-indices,]

f = radius0_bin ~ pressure + temperature + salinity + month + freezing_point_delta + season

#multinom
cat('Multinomial Log-linear\n')
model = multinom(f, df_balanced_train)
predictions = predict(model, df_balanced_test)
cat('Confusion matrix\n')
table(df_balanced_test$radius0_bin, predictions)
cat('Accuracy\n')
mean(predictions == df_balanced_test$radius0_bin)


#J48
cat('J48 decision tree\n')
j48_model = J48(f, df_balanced_train)
summary(j48_model)
predictions = predict(j48_model, df_balanced_test)
cat('Confusion matrix\n')
table(df_balanced_test$radius0_bin, predictions)
cat('Accuracy\n')
mean(predictions == df_balanced_test$radius0_bin)

#Random Tree
cat('Random Tree\n')
random_tree = make_Weka_classifier("weka/classifiers/trees/RandomTree")
random_tree_model = random_tree(f, df_balanced_train, control = Weka_control(depth = 4, S = 123))
summary(random_tree_model)
predictions = predict(random_tree_model, df_balanced_test)
cat('Confusion matrix\n')
table(df_balanced_test$radius0_bin, predictions)
cat('Accuracy\n')
mean(predictions == df_balanced_test$radius0_bin)

