library(gsw)
library(feather)

# back to official work, removing outliers
df = read.csv('/home/tloureiro/projects/arctic-analysis/data/produced-csvs/final.csv', col.names = c('itp', 'profile', 'timestamp', 'latitude', 'longitude', 'pressure', 'temperature', 'salinity', 'radius0', 'radius1', 'radius2', 'radius5', 'radius10'), header = FALSE )

#removing na's
df = df[(!is.na(df$salinity)) & (!is.na(df$temperature)), ]
df = df[df$radius0 >= 0,]

#removing bad itps
df = df[(df$itp != 31 & df$itp != 39 & df$itp != 40 & df$itp != 45 & df$itp != 46),]

#removing bad salinity and temp
df = df[df$salinity < 40,]
df = df[df$temperature < 30 & df$temperature > -10,]


#adding months
df$month = as.factor(format(as.Date(as.POSIXct(df$timestamp, origin="1970-01-01")), '%m'))

#adding freezing_point_delta
df$freezing_point_delta = df$temperature - gsw_t_freezing(gsw_SA_from_SP(df$salinity, df$pressure, df$longitude, df$latitude), df$pressure)

#adding season 
df$season = as.factor(
  ifelse((df$month == '12' | df$month == '01' | df$month == '02'), 'W',
    ifelse( (df$month == '03' | df$month == '04' | df$month == '05'), 'SP',
      ifelse( (df$month == '06' | df$month == '07' | df$month == '08'), 'SU',
        ifelse( (df$month == '09' | df$month == '10' | df$month == '11'), 'F', NA))))
)


#discretizing radius0
df$radius0_bin = cut(df$radius0, breaks = 4, labels = c('0-25', '25-50', '50-75', '75-100'))


write_feather(df, '/home/tloureiro/projects/arctic-analysis/data/produced-csvs/clean_final.feather')
write.table(df, '/home/tloureiro/projects/arctic-analysis/data/produced-csvs/clean_final.csv', sep=",",  col.names=TRUE, row.names=FALSE)


