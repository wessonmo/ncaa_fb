library(lme4)

match_results = read.csv('espn\\csv\\espn_game_info.csv')

reg_season = match_results[(match_results$season_type == 2) & (match_results$season != 2017),]
reg_season$homeid = paste0(reg_season$season,'_',reg_season$homeid)
reg_season$awayid = paste0(reg_season$season,'_',reg_season$awayid)
reg_season$season = paste0('year_',reg_season$season)

home_off = reg_season[,-c(3:6,11)]
names(home_off)[c(4:6)] = c('off_id','def_id','points')
home_off$field = ifelse(home_off$neutral == T,'neutral','home')

away_off = reg_season[,-c(3:6,10)]
names(away_off)[c(4:6)] = c('def_id','off_id','points')
away_off$field = ifelse(home_off$neutral == T,'neutral','away')

comb = rbind(home_off,away_off)

attach(comb)

off_id = as.factor(off_id)
def_id = as.factor(off_id)
season = relevel(as.factor(season),'year_2009')
field = relevel(as.factor(field),'neutral')
gameid = as.factor(gameid)

formula = points ~ season + field + (1|off_id) + (1|def_id) + (1|gameid)

model = lmer(formula, data = comb)
summary(model)
anova(model)

# relgrad <- with(model@optinfo$derivs,solve(Hessian,gradient))
# max(relgrad)

fixed = fixef(model)
rand = ranef(model)

write.csv(rand$off_id,file = 'off_est.csv')
write.csv(rand$def_id,file = 'def_est.csv')