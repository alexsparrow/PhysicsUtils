#!/usr/bin/env python

import cmd,sys,readline,os,os.path

class CrabJob:
    def __init__(self,job):
        self.job=job

    def create(self):
        pass

class Job:
    def __init__(self,name,sample):
        self.name=name
        self.sample=sample

    def setup_dir(self,path):
        if not os.path.exists(path):
            os.mkdir(path)
        else:
            raise Exception("Directory already exists")
        self.path=path

class ICFGridTool(cmd.Cmd):
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt="icf> "
        self.jobs={}
        self.header_eq="========================================"
        self.job_dir="./jobs"

    def do_create(self,name="",sample=""):
        if name == "":
            name = raw_input("Enter job name: ")
        if sample == "":
            sample=raw_input("Enter sample path: ")
        job=Job(name,sample)
        try:
            job.setup_dir(self.job_dir+"/"+name)
        except Exception as e:
            print e
            return
        self.jobs[name]=job
        print "Job %s created in directory %s" % (name,job.path)

    def help_create(self):
        print "Creates a grid job"

    def do_list(self,name=""):
        print "Jobs:"
        print self.header_eq
        if not len(self.jobs):
            print "No jobs yet!"
        for (name,j) in self.jobs.iteritems():
            print "%s\t%s" % (name,j.sample)
        print self.header_eq

    def help_list(self):
        print "List jobs"

    def do_crab_create(self,name):
        if not name in self.jobs:
            print "ERROR: No such job"
            return
        j=self.jobs[name]
        crab=CrabJob(j)
        j.crab=crab
        try:
            crab.create()
        except Exception as e:
            print e


    def help_EOF(self):
        print "Quits the program"

    def do_EOF(self, line):
        sys.exit()

if __name__=="__main__":
    icf=ICFGridTool()
    icf.cmdloop()
