options(java.parameters = "-Xmx24g")

library(feather)
library(dplyr)
library(nnet)
library(caret)
library(rJava)
library(RWeka)
library(yardstick)
library(effsize)

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
control = trainControl(method="cv", number=10)

df = read_feather('/home/tloureiro/projects/arctic-analysis/data/produced-csvs/clean_final.feather')

df = df[df$pressure <= 10, ]

indices = createDataPartition(df$radius0_bin, p=0.7, list = FALSE)
df_train = df[indices,]
df_test = df[-indices,]

remove(df)

df_balanced_train = balanceDatasetByDV(df_train, 1)

f = radius0_bin ~ temperature + salinity + month + freezing_point_delta + season

#multinom
cat('Multinomial Log-linear\n')

start_time = Sys.time()
multinom_model = train(f, data=df_balanced_train, trControl=control, method="multinom")
end_time = Sys.time()
cat('Training model time:' , round(difftime(end_time, start_time, units = 'secs')), 'seconds\n')

multinom_predictions = predict(multinom_model, df_test)

cat('Model evaluation\n')
df_confusion_matrix = data.frame(df_test$radius0_bin, multinom_predictions)
names(df_confusion_matrix) = c('test', 'predictions')
confusion_matrix = conf_mat(df_confusion_matrix, truth = 'test', estimate = 'predictions')
print(confusion_matrix)
summary(confusion_matrix)


#J48
cat('\nJ48 decision tree\n')

start_time = Sys.time()
j48_model = train(f, data=df_balanced_train, trControl=control, method="J48")
end_time = Sys.time()
cat('Training model time:' , round(difftime(end_time, start_time, units = 'secs')), 'seconds\n')

summary(j48_model)

j48_predictions = predict(j48_model, df_test)

cat('Model evaluation\n')
df_confusion_matrix = data.frame(df_test$radius0_bin, j48_predictions)
names(df_confusion_matrix) = c('test', 'predictions')
confusion_matrix = conf_mat(df_confusion_matrix, truth = 'test', estimate = 'predictions')
print(confusion_matrix)
summary(confusion_matrix)


#Random Forest
cat('\nRandom Forest\n')

start_time = Sys.time()
random_forest_model = train(f, data=df_balanced_train, trControl=control, method="rf")
end_time = Sys.time()
cat('Training model time:' , round(difftime(end_time, start_time, units = 'secs')), 'seconds\n')

summary(random_forest_model)

random_forest_predictions = predict(random_forest_model, df_test)

cat('Model evaluation\n')
df_confusion_matrix = data.frame(df_test$radius0_bin, random_forest_predictions)
names(df_confusion_matrix) = c('test', 'predictions')
confusion_matrix = conf_mat(df_confusion_matrix, truth = 'test', estimate = 'predictions')
print(confusion_matrix)
summary(confusion_matrix)


cat('\nModel performance comparison significance\n')
cat('Multinom vs J48\n')
mcnemar.test(xtabs(data = data.frame(multinom_predictions == df_test$radius0_bin, j48_predictions == df_test$radius0_bin)))


cat('Multinom vs Random Forest\n')
mcnemar.test(xtabs(data = data.frame(multinom_predictions == df_test$radius0_bin, random_forest_predictions == df_test$radius0_bin)))

cat('J48 vs Random Forest\n')
mcnemar.test(xtabs(data = data.frame(j48_predictions == df_test$radius0_bin, random_forest_predictions == df_test$radius0_bin)))