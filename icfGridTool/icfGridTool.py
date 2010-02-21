#!/usr/bin/env python
import cmd,readline,os,os.path
from icfGridLib import *

header_eq="="*50

class ICFGridTool(cmd.Cmd):
    def __init__(self,config="./icf.cfg"):
        cmd.Cmd.__init__(self)
        self.prompt="icf> "
        self.jobs={}
        if not os.path.exists(config):
            print "No file icf.cfg found"
            print "Generating defaults."
            Config.initDefault(config)
        self.config=Config(config)
        print "Config:"
        print header_eq
        self.config.printGlobals()
        print header_eq

    def emptyline(self):
        pass

    def do_create(self,name=""):
        print "Create Job:"
        name=myInput(StringType,"Name:")
        if name in self.jobs:
            print "ERROR: Job already exists with name: %s" %name
            return
        sample=myInput(StringType,"Dataset Path:")
        mcinfo=myInput(BooleanType,"Generate MC:")
        j=Job(self.config.job_defaults)
        print name
        j.set("name",name)
        j.set("sample",sample)
        j.set("mcinfo",mcinfo)
        self.jobs[name]=j

    def help_create(self):
        print "Create a job"

    def do_edit(self,name):
        if not name in self.jobs:
            print "ERROR: Unknown job: %s" % name
            return
        print "Edit Job:"
        param=myInput(StringType,"Parameter:")
        if not param in self.jobs[name].params:
            print "Unknown paramater: %s" % param
            return
        value=myInput(self.jobs[name].params[param][0],
                      "New value (previous=%s):" % self.jobs[name].get(param))
        self.jobs[name].set(param,value)

    def help_edit(self,name):
        print "Edit a job"

    def do_show(self,name):
        if not name in self.jobs:
            print "ERROR: Unknown job: %s" % name
            return
        print header_eq
        print "Job : %s" % name
        print "Status : %s "%self.jobs[name].get("status")
        print header_eq
        print self.jobs[name]

    def help_show(self):
        print "Show an individual job"

    def do_crab_create(self,name):
        if not name in self.jobs:
            print "ERROR: Unknown job: %s" % name
            return
        self.jobs[name].crabCreate(self.config.globals,
                                   self.config.globals["jobdir"][1]+
                                   "/"+name)

    def do_list(self,name=""):
        print "Jobs:"
        print header_eq
        if not len(self.jobs):
            print "No jobs yet!"
        for (name,j) in self.jobs.iteritems():
            print "%s\t%s\t%s" % (j.get("name"),j.get("sample"),j.get("status"))
        print header_eq

    def help_list(self):
        print "List jobs"


    def do_EOF(self, line):
        sys.exit()

    def help_EOF(self):
        print "Quits the program"

if __name__=="__main__":
    tool=ICFGridTool()
    tool.cmdloop()
