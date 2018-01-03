library(lme4)

match_results = read.csv('espn\\csv\\espn_game_info.csv')
team_info = read.csv('espn\\csv\\espn_team_info.csv')

reg_season = match_results[(match_results$season_type == 2),]
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
rand = ranef(model, condVar = T)

off = rand$off_id
off$var = attr(rand$off_id, "postVar")[1, 1, ]
def = rand$def_id
def$var = attr(rand$def_id, "postVar")[1, 1, ]

out = data.frame(cbind(off,def))
colnames(out) = c('off_int','off_var','def_int','def_var')
out$season = sapply(rownames(out), function(x) as.numeric(substr(x,1,4)))
out$id = sapply(rownames(out), function(x) as.numeric(substr(x,6,9)))

out = merge(out,team_info[,c('espn_teamid','team_schoolname')], by.x = 'id', by.y = 'espn_teamid',all.x = T)

write.csv(out,file = 'model_output.csv')