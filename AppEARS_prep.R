##########   Description   ##########
#' Goal: Chunk data into 1000-row segments for AppEARS input
#' Date: Oct 25, 2022
#' Author: Savannah Cooley 
##########   Prep   ##########
suppressPackageStartupMessages({
  library(ggplot2)
  library(data.table)
  library(dplyr)
})
#options(warn=-1) # Turn off warnings globally. To turn warnings back on, use: options(warn=0)

####  1. Read in data   ##########
root="/Users/Sscooley/Documents/Columbia/Ch3/Data"
outPath<-paste(root, "/L4A/processed_csvs/_no_edges/",sep="")
setwd(outPath)
dt_all<-fread(paste(outPath,"dt_allVars_agg_1_879.csv", sep=""))

# Plot histogram of AGB data
par(mfrow=c(1,1));hist(dt_all$AGB, breaks = 30, freq = FALSE, col = "grey", xlab = "Aboveground Biomass (Mg ha-1)", main = " ") #, ylim = c(0, 1)

####  2. Separate into 1,000 row chunks    ##########
dt<-subset(dt_all, select = c("lat", "lon"))
names(dt)<- c("Latitude", "Longitude")
dt$Latitude<-round(dt$Latitude, digits = 15)
dt$Longitude<-round(dt$Longitude, digits = 15)
length.out<- 340# 170 # 186/100*x = 318 # 1.46*x  = 465 ## 8,400

# 1.75*x = 600 --> x = 340
n=as.integer(nrow(dt)/length.out)
k=0
for(i in 1:n){ # up through 318
  j=k+1
  k=i*length.out
  df<-dt[j:k,]
  write.csv(df, paste(root, "/ECOSTRESS/AppEARS_input_pts/_length.out_340/",j,"_",k,"_AGB_pts.csv", sep=""))
}

j=k+1
k=nrow(dt)
df<-dt[j:k,]
write.csv(df, paste(root, "/ECOSTRESS/AppEARS_input_pts/_length.out_340/",j,"_",k,"_AGB_pts.csv", sep=""))


####  3. Separate into equal length chunks (fewer rows than 1000)    ##########


nr <- nrow(dt)
n=6
tmp<-split(dt, rep(1:ceiling(nr), each=nr/n, length.out=nr))

for(i in 1:n){
  df<-tmp[[i]]
  write.csv(df, paste(i,"_Meta_analysis_search_501_1000.csv", sep=""))
}




