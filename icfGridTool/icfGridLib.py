#!/usr/bin/env python
from types import *
import os,os.path
import ConfigParser
import subprocess
import shutil

global_defaults={
    "jobdir":(StringType,"./jobs","Job storage directory"),
    "email":(StringType,"","Email address for CrabServer"),
}

job_defaults={
    "name":(StringType,"","Name of job"),
    "sample":(StringType,"","Sample dataset path"),
    "script":(StringType,"icfNtuple_cfg.py","Path to CMSSW script"),
    "globaltag":(StringType,"MC_3XY_V18::All","Global Tag to use"),
    "crabtemplate":(StringType,"./crab_tmpl.cfg","Path to CRAB template script"),
    "eventsperjob":(IntType,10000,"Number of events per job."),
    "events":(IntType,-1,"Total number of events to process."),
    "mcinfo":(BooleanType,True,"Flag to generate MC info."),
    "scheduler":(StringType,"glite_slc5","CRAB Scheduler."),
    "servername":(StringType,"legnaro","CrabServer name."),
    "copydata":(BooleanType,True,"Crab copy data to storage."),
    "returndata":(BooleanType,False,"Crab return data to user."),
    "storagepath":(StringType,"/castor/cern.ch","Crab storage path."),
    "userremotedir":(StringType,"","Crab user remote directory."),
    "storageelement":(StringType,"srm-cms.cern.ch","Crab storage element."),
    "status":(StringType,"CREATED","Job status"),
    "crabdir":(StringType,"","Path to CRAB directory")
}

def myInput(vtype,name):
    cool=False
    val=None
    while not cool:
        tmp=raw_input(name)
        if vtype==StringType:
            val=tmp
            cool=True
        elif vtype==IntType:
            try:
                val=int(tmp)
                cool=True
            except ValueError:
                print "Incorrect value for int: %s" % tmp
        elif vtype==BooleanType:
            try:
                val=int(tmp)
                if val<0 or val >1:
                    raise ValueError
                else:
                    val=bool(val)
                cool=True
            except ValueError:
                print "Incorrect value for bool: %s" % tmp
        if not cool:
            print "Please try again."
    return val

def getRaw(val,vtype):
    if vtype==BooleanType:
        if val:
            return 1
        else:
            return 0
    else:
        return val

class CrabJob:
    def __init__(self,job,glob,path):
        f=open(job.get("crabtemplate"),"r")
        crab=f.read()
        for (k,v) in job.params.iteritems():
            crab=crab.replace("__"+k+"__",str(getRaw(v[1],v[0])))
        for(k,v) in glob.iteritems():
            crab=crab.replace("__"+k+"__",str(getRaw(v[1],v[0])))
        f=open(path+"/crab.cfg","w+")
        f.write(crab)
        shutil.copyfile(job.get("script"),
                        path+"/"+os.path.split(job.get("script"))[1])
        self.path=path

    def submit(self):
        p=subprocess.Popen(["crab","-cfg","crab.cfg","-create","-submit","all"],cwd=self.path)
	p.wait()
	return (p.returncode==0)

    def status(self):
        p=subprocess.Popen(["crab","-status"],
                           cwd=self.path,
                           stdout=subprocess.PIPE)
        (out,err)=p.communicate(None)
        return out

class Job:
    def __init__(self,params):
        self.params=params

    def get(self,name):
        if not name in self.params:
            raise KeyError("Parameter not found: %s" % name)
        return self.params[name][1]

    def _set(self,name,value):
        self.params[name]=(self.params[name][0],value,self.params[name][2])

    def set(self,name,value):
        if not name in self.params:
            raise KeyError("Paramater not found: %s" % name)
        if type(value)==self.params[name][0]:
            self._set(name,value)
        elif type(value)=="str":
            if self.params[name][0]=="int":
                self._set(name,int(value))
            elif self.params[name][0]=="bool":
                if value=="1":
                    self._set(name,True)
                elif value=="0":
                    self.set(name,False)
                else:
                    msg="Invalid literal for boolean %s ('%s')" % (name, value)
                    raise ValueError(msg)
        else:
            print str(type(value))
            print self.params[name][0]
            msg="Invalid literal for %s (%s) : '%s'" %(name,
                                                       self.params[name][0],
                                                       value)
            raise ValueError(msg)

    def __repr__(self):
        strs=[]
        for (k,v) in self.params.iteritems():
            strs.append("%s : %s" % (k,v[1]))
            strs.append("\n")
        del strs[len(strs)-1]
        return "".join(strs)

    def crabCreate(self,glob,path):
        if not os.path.exists(path):
            os.mkdir(path)
        c=CrabJob(self,glob,path)
        self.crab_job=c
        self.set("crabdir",path)

    def crabSubmit(self):
        return self.crab_job.submit()

    def crabStatus(self):
        return self.crab_job.status()
class Config:
    def __init__(self,fname):
        self.conf=ConfigParser.RawConfigParser()
        self.conf.read(fname)
        self.job_defaults=job_defaults
        self.globals=global_defaults
        self.fname=fname

    @staticmethod
    def initDefault(fname):
        conf=ConfigParser.RawConfigParser()
        Config.writeSection(conf,job_defaults,"DEFAULT")
        Config.writeSection(conf,global_defaults,"DEFAULT")
        configfile=open(fname, 'wb')
        conf.write(configfile)

    @staticmethod
    def readSection(conf,params,secname):
        for (k,v) in params.iteritems():
            if v[0]==StringType:
                val=conf.get(secname,k)
            elif v[0]==IntType:
                val=conf.getint(secname,k)
            elif v[0]==BooleanType:
                val=False
                tmp=conf.getint(secname,k)
                if(tmp==1):
                    val=True
                elif(tmp==0):
                    val=False
                else:
                    raise ValueError
            params[k]=(params[k][0],val,params[k][2])

    @staticmethod
    def writeSection(conf,params,secname):
        for (k,v) in params.iteritems():
            conf.set(secname,k,getRaw(v[1],v[0]))

    def write(self):
        configfile=open(self.fname, 'wb')
        self.conf.write(configfile)

    def readGlobals(self):
        self.readSection(self.conf,self.job_defaults,"DEFAULT")
        self.readSection(self.conf,self.globals,"DEFAULT")

    def writeGlobals(self):
        self.writeSection(self.conf,self.job_defaults,"DEFAULT")
        self.writeSection(self.conf,self.globals,"DEFAULT")

    def readJobs(self):
        jobs={}
        for s in self.conf.sections():
            job_params=self.job_defaults.copy()
            self.readSection(self.conf,job_params,s)
            job_name=job_params["name"][1]
            if job_name in jobs:
                raise KeyError("Duplicate job names detected")
            jobs[job_name]=Job(job_params)
            if not job_params["crabdir"][1]=="":
                jobs[job_name].crab_job=CrabJob(jobs[job_name],
                                                self.globals,
                                                job_params["crabdir"][1])
        return jobs

    def writeJobs(self,jobs):
        for (k,v) in jobs.iteritems():
            if not self.conf.has_section(k):
                self.conf.add_section(k)
            self.writeSection(self.conf,v.params,k)
        self.write()

    def printGlobals(self):
        for (k,v) in self.job_defaults.iteritems():
            print "%s = %s" % (k,v[1])
        for (k,v) in self.globals.iteritems():
            print "%s = %s" % (k,v[1])

if __name__=="__main__":
    pass
