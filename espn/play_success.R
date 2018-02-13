library(lme4)

pbp = read.csv('E:\\college football\\pbp\\csv\\espn_pbp.csv')

down1 = pbp[(pbp$down == 1) & (pbp$playtype %in% c('pass','rush')) & (pbp$yrd2end > 20),]
down1$succ_est = 0.9718*exp(-0.031*down1$dist)

down2 = pbp[(pbp$down == 2) & (pbp$playtype %in% c('pass','rush')) & (pbp$yrd2end > 20),]
down2$succ_est = 0.9389*exp(-0.055*down2$dist)

down3 = pbp[(pbp$down == 3) & (pbp$playtype %in% c('pass','rush')) & (pbp$yrd2end > 20),]
down3$succ_est = 0.6256**exp(-0.071*down3$dist)

rbind(down3[,c('gameid','driveid','playid','period','clock','')])