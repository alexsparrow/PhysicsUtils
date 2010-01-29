#!/usr/bin/env python
from gct_pat_test import *
from config import *
from utils import *

pats=permute([v3],1,True)
l1=PatternList("OneAboveThreshold",conf)
i=0
for p in pats:

    l1+=Pattern("1_"+str(i),
               Taus=1,
               Jets=0,
               EPattern=p[0:4]+[v9]+p[4:8]
               )
    i+=1

pats=permute([v3,v3],2,True)

l2=PatternList("TwoAboveThreshold",conf)
i=0
for p in pats:

    l2+=Pattern("2_"+str(i),
               Taus=0,
               Jets=1,
               EPattern=p[0:4]+[v9]+p[4:8]
               )
    i+=1

pats=permute([v3,v3,v3],3,True)
l3=PatternList("ThreeAboveThreshold",conf)
i=0
for p in pats:

    l3+=Pattern("3_"+str(i),
               Taus=0,
               Jets=1,
               EPattern=p[0:4]+[v9]+p[4:8]
               )
    i+=1

pats=permute([v3,v3,v3,v3],4,True)
l4=PatternList("FourAboveThreshold",conf)
i=0
for p in pats:

    l4+=Pattern("4_"+str(i),
               Taus=0,
               Jets=1,
               EPattern=p[0:4]+[v9]+p[4:8]
               )
    i+=1

pats=permute([v3,v3,v3,v3,v3],5,True)
l5=PatternList("FiveAboveThreshold",conf)
i=0
for p in pats:

    l5+=Pattern("5_"+str(i),
               Taus=0,
               Jets=1,
               EPattern=p[0:4]+[v9]+p[4:8]
               )
    i+=1

pats=permute([v3,v3,v3,v3,v3,v3],6,True)
l6=PatternList("SixAboveThreshold",conf)
i=0
for p in pats:

    l6+=Pattern("6_"+str(i),
               Taus=0,
               Jets=1,
               EPattern=p[0:4]+[v9]+p[4:8]
               )
    i+=1

pats=permute([v3,v3,v3,v3,v3,v3,v3],7,True)
l7=PatternList("SevenAboveThreshold",conf)
i=0
for p in pats:
    l7+=Pattern("7_"+str(i),
               Taus=0,
               Jets=1,
               EPattern=p[0:4]+[v9]+p[4:8]
               )
    i+=1

pats=permute([v3,v3,v3,v3,v3,v3,v3,v3],8,True)
l8=PatternList("EightAboveThreshold",conf)
i=0
for p in pats:

    l8+=Pattern("8_"+str(i),
               Taus=0,
               Jets=1,
               EPattern=p[0:4]+[v9]+p[4:8]
               )
    i+=1

master=l1+l2+l3+l4+l5+l6+l7+l8
master.name="newtaualgo"
master.Compile()

master_tau_veto1=PatternList("newtaualgo_tau_veto1",conf)
for pat in master.patterns:
    for tau_pos in [0,1,2,3,4]:
        pat2=Pattern(pat.name+"Tau"+str(tau_pos))
        pat2.EPattern=pat.EPattern
        pat2.TauPattern=[0,0,0,0,0,0,0,0,0]
        pat2.TauPattern[tau_pos]=1

        pat2.Taus=0
        pat2.Jets=1
        master_tau_veto1+=pat2

master_tau_veto1.Compile()

master_tau_veto2=PatternList("newtaualgo_tau_veto2",conf)
for pat in master.patterns:
    for tau_pos in [5,6,7,8]:
        pat2=Pattern(pat.name+"Tau"+str(tau_pos))
        pat2.EPattern=pat.EPattern
        pat2.TauPattern=[0,0,0,0,0,0,0,0,0]
        pat2.TauPattern[tau_pos]=1

        pat2.Taus=0
        pat2.Jets=1
        master_tau_veto2+=pat2
master_tau_veto2.Compile()
