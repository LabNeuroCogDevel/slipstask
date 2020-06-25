#!/usr/bin/env Rscript
library(dplyr)
library(ggplot2)
library(cowplot)
theme_set(theme_cowplot())

# 20200624WF - init
#   read in fruit and side pairs


d <-
   read.csv('txt/ages.csv') %>%
   merge(read.table('txt/fruit_survey.tsv',header=T)) %>%
   mutate(correct=correct=='true') %>%
   group_by(subjID, age, survey_type) %>%
   summarise(cor=sum(correct)/n(), conf=mean(confidence))

   #tidyr::spread(survey_type,cor)

p <- d %>%
    tidyr::gather(mes,val,-age,-subjID,-survey_type) %>%
    ggplot() + aes(x=age, y=val, color=survey_type) +
    #geom_line(aes(group=subjID), color='black', alpha=.2, size=1) +
    #geom_jitter(alpha=.8, width=.1, height=0) +
    geom_point() +
    geom_smooth(se=F, linetype=2) +
    facet_grid(mes~., scales="free_y") +
    ggtitle('learned assoc.') 

ggsave(p,file='survey_learn.png')

# non are sig. (all ~ .25)
split(d,d$survey_type) %>% sapply(function(x) summary(lm(age~cor,x))$coeff['cor','Pr(>|t|)'])
