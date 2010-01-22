import os
import subprocess
from datetime import datetime
from optparse import OptionParser

class Config:
    def __init__(self):
        self.NewTauAlgo=False
        self.NewTauAlgoThresh=15
        self.NewTauAlgoRespectTauVeto=False
	self.conf_dir=""

class PatternList:
    def __init__(self,name,conf):
        self.name=name
        self.NewTauAlgo=conf.NewTauAlgo
        self.NewTauAlgoThresh=conf.NewTauAlgoThresh
        self.NewTauAlgoRespectTauVeto=conf.NewTauAlgoRespectTauVeto
        self.patterns=[]
        self.placement=conf.placement
        self.ecmd=conf.ecmd
        self.gct_pat_maker=conf.gct_pat_maker
	self.out_dir=conf.out_dir
        parser = OptionParser()
        parser.add_option("-n","--no-compile",action="store_true",default=False)
        parser.add_option("-d","--dont-test",action="store_true",default=False)
        (self.options, self.args) = parser.parse_args()
        self.conf=conf

    def __iadd__(self,pat):
        self.patterns.append(pat)
        return self

    def __add__(self,other):
        p=PatternList(self.name,self.conf)
        p.patterns.extend(self.patterns)
        p.patterns.extend(other.patterns)
        return p

    def OutputPattern(self,pat):
        pstr="# Pattern File: %s, Pattern: %s\n" %(self.name,pat.name)
        i=0
        for e_val in pat.EPattern:
            pstr+="%s %d %d %d %d\n" %(self.ecmd,
                                    self.placement[i][0],
                                    self.placement[i][1],
                                    self.placement[i][2],
                                    e_val)
            i+=1
        return pstr

    def OutputPatterns(self):
	if not os.path.exists(self.out_dir):
	    os.mkdir(self.out_dir)
        if not os.path.exists(self.out_dir+"/"+self.name):
            os.mkdir(self.out_dir+"/"+self.name)
	jets=taus=0
        for p in self.patterns:
            f=open(self.out_dir+"/"+self.name+"/"+p.name+".txt",'w')
            pat_str=self.OutputPattern(p)
            f.write(pat_str)
	    f.close()
	    jets+=p.Jets
	    taus+=p.Taus
	f=open(self.out_dir+"/"+self.name+".log",'w')
	f.write("Pattern File: %s\n" % self.name)
	f.write("==================================================\n")
	f.write("Generated: %s\n" % datetime.now())
	f.write("Pattern Count: %d\n" % len(self.patterns))
	f.write("Taus Expected: %s\n" % taus)
	f.write("Jets Expected: %s\n" % jets)
        for p in self.patterns:
            f.write("Pattern: %s\n" % p.name)
            f.write(str(p))
	f.close()

    def Compile(self):
        if not self.options.dont_test:
            if not self.TestPatterns():
                print "Checks Failed. Not Compiling."
                return False
        self.OutputPatterns()
        if not self.options.no_compile:
            args=[self.gct_pat_maker,self.name+".dat"]
            for p in self.patterns:
                args.append("./%s/%s.txt" % (self.name,p.name))
            subprocess.call(args)
            print args
        print "Patterns output in directory: %s" % self.name+"/"

    def TestPatterns(self):
        good=True
        for pat in self.patterns:
            good = good and self.CheckPattern(pat)
        if good:
            print "%d Patterns OK" % len(self.patterns)
            print "Pattern Expects:"
            jets=taus=0
            for p in self.patterns:
                jets+=p.Jets
                taus+=p.Taus
            print "Jets: %d" % jets
            print "Taus: %d" % taus
        else:
            print "Bad Patterns"
        return good

    def CheckPattern(self,pat):
        res=self.Eval3x3(pat)
        good=True
        print "Pattern: %s" % pat.name
        if not pat.Taus==res["Taus"]:
            print "Pattern results don't match spec: Taus. Specified: %d, Expected: %d" % (pat.Taus,res["Taus"])
            good=False
        if not pat.Jets==res["Jets"]:
            print "Pattern results don't match spec: Jets. Specified: %d, Expected: %d" % (pat.Jets,res["Jets"])
            good=False
        return good

    def Eval3x3(self,pat):
        central=pat.getE(1,1)
        nw=pat.getE(0,0)
        n=pat.getE(1,0)
        ne=pat.getE(2,0)
        w=pat.getE(0,1)
        e=pat.getE(2,1)
        sw=pat.getE(0,2)
        s=pat.getE(1,2)
        se=pat.getE(2,2)
        central_max=False
        if central > max([nw,n,ne,w,e,sw,s,se]):
            central_max=True
        if self.NewTauAlgo:
            tau_ticker=0
            for e_val in [nw,n,ne,w,e,sw,s,se]:
                if e_val>self.NewTauAlgoThresh:
                    tau_ticker+=1
            if tau_ticker>1:
                tau_veto=True
            else:
                tau_veto=False
            if self.NewTauAlgoRespectTauVeto:
                for veto_val in pat.TauPattern:
                    if veto_val==1:
                        tau_veto=True
                        break
        ret={}
        if central_max:
            if tau_veto:
                ret["Jets"]=1
                ret["Taus"]=0
            else:
                ret["Taus"]=1
                ret["Jets"]=0
        else:
            ret["Taus"]=ret["Jets"]=0
        return ret

class Pattern:
    def __init__(self,name,Taus=0,Jets=0,
                 EPattern=[0,0,0,0,0,0,0,0,0],
                 TauPattern=[0,0,0,0,0,0,0,0,0],
                 OVFPattern=[0,0,0,0,0,0,0,0,0]):
        self.name=name
        self.Taus=Taus
        self.Jets=Jets
        self.EPattern=EPattern
        self.TauPattern=TauPattern
        self.OVFPattern=OVFPattern
        self.size=3

    def getE(self,x,y):
        if self.size==3:
            return self.EPattern[(y*3)+x]

    def __str__(self):
        ostr=""
        i=0
        for e in self.EPattern:
            ostr+=str(e)
            if self.TauPattern[i]==1:
                ostr+="T"
            elif self.OVFPattern[i]==1:
                ostr+="^"
            else:
                ostr+=" "
            if ((i+1) % self.size)==0:
                ostr+="\n"
            else:
                ostr+="\t"
            i+=1

        return ostr
