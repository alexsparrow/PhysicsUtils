from gct_pat_test import *
conf=Config()

conf.NewTauAlgo=True
conf.NewTauAlgoThresh=15
conf.NewTauRespectTauVeto=False
conf.placement=[ (12,0,1) , (12,2,0) , (12,2,1) ,
                 (12,1,1) , (12,3,0) , (12,3,1) ,
                 (13,0,1) , (13,2,0) , (13,2,1) ]
conf.gct_pat_maker="/home/alex/GCTPatternMakerAddon/exe/master_pattern_generator"
conf.out_dir="./patterns"
conf.ecmd="rc"

v9=100
v0=0
v1=10
v2=conf.NewTauAlgoThresh
v3=20
