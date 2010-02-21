#!/usr/bin/env python
import random

def tau_energy():
    if(random.random()>0.9):
        return random.randint(50,200)
    else:
        return random.randint(4,12)

def tau_veto():
    if random.random()>0.9:
        return 1
    else:
        return 0
if __name__=="__main__":
    for evt in range(2000):
        f=open("patterns/pattern_%d.txt" % evt,'w')
        print "Generating pattern %d" % evt
        for crate in range(18):
            for i in range(7):
                for j in range(2):
                    f.write("rc %d %d %d %d\n" % (crate,i,j,tau_energy()))
                    f.write("rctau %d %d %d %d\n" % (crate,i,j,tau_veto()))
        f.close()
