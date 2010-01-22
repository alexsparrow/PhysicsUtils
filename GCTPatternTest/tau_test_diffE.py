#!/usr/bin/env python
from gct_pat_test import *
from config import *
from utils import *

v3=10
v4=256
v5=512
v9=700
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

pats=permute([v3,v4],2,True)

l2=PatternList("TwoAboveThreshold",conf)
i=0
for p in pats:
    l2+=Pattern("2_"+str(i),
               Taus=1,
               Jets=0,
               EPattern=p[0:4]+[v9]+p[4:8]
               )
    i+=1


pats=permute([v3,v4,v5],3,True)
l3=PatternList("ThreeAboveThreshold",conf)
i=0
for p in pats:

    l3+=Pattern("3_"+str(i),
               Taus=0,
               Jets=1,
               EPattern=p[0:4]+[v9]+p[4:8]
               )
    i+=1


pats=permute([v3,v3,v4,v5],4,True)
l4=PatternList("FourAboveThreshold",conf)
i=0
for p in pats:

    l4+=Pattern("4_"+str(i),
               Taus=0,
               Jets=1,
               EPattern=p[0:4]+[v9]+p[4:8]
               )
    i+=1


pats=permute([v3,v3,v4,v5,v3],5,True)
l5=PatternList("FiveAboveThreshold",conf)
i=0
for p in pats:

    l5+=Pattern("5_"+str(i),
               Taus=0,
               Jets=1,
               EPattern=p[0:4]+[v9]+p[4:8]
               )
    i+=1


pats=permute([v3,v3,v4,v5,v3,v3],6,True)
l6=PatternList("SixAboveThreshold",conf)
i=0
for p in pats:

    l6+=Pattern("6_"+str(i),
               Taus=0,
               Jets=1,
               EPattern=p[0:4]+[v9]+p[4:8]
               )
    i+=1


pats=permute([v3,v3,v3,v4,v5,v3,v3],7,True)
l7=PatternList("SevenAboveThreshold",conf)
i=0
for p in pats:
    l7+=Pattern("7_"+str(i),
               Taus=0,
               Jets=1,
               EPattern=p[0:4]+[v9]+p[4:8]
               )
    i+=1


pats=permute([v3,v3,v3,v4,v5,v3,v3,v3],8,True)
l8=PatternList("EightAboveThreshold",conf)
i=0
for p in pats:

    l8+=Pattern("8_"+str(i),
               Taus=0,
               Jets=1,
               EPattern=p[0:4]+[v9]+p[4:8]
               )
    i+=1


master2=l1+l2+l3
master3=l4+l5
master4=l6+l7+l8
master2.name="master2_10_256_512_700"
master2.Compile()
master3.name="master3_10_256_512_700"
master3.Compile()
master4.name="master4_10_256_512_700"
master4.Compile()
