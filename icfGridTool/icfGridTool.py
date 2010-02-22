#!/usr/bin/env python
import cmd,readline,os,os.path,sys
from icfGridLib import *

header_eq="="*50
header80="="*80

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
        self.config.readGlobals()
        self.jobs=self.config.readJobs()
        print "Config:"
        print header_eq
        self.config.printGlobals()
        print header_eq

    def emptyline(self):
        pass

    def completedefault(self,text,line,begidx,endidx):
        j=[]
        for (k,v) in self.jobs.iteritems():
            if k.startswith(text):
                j.append(k)
        return j

    def do_create(self,name=""):
        print "Create Job:"
        name=myInput(StringType,"Name:")
        if name in self.jobs:
            print "ERROR: Job already exists with name: %s" %name
            return
        sample=myInput(StringType,"Dataset Path:")
        mcinfo=myInput(BooleanType,"Generate MC:")
        remotedir=myInput(StringType,"Remote Dir:")
        j=Job(self.config.default_job.params.copy())
        print name
        j.set("name",name)
        j.set("sample",sample)
        j.set("mcinfo",mcinfo)
        j.set("userremotedir",remotedir)
        self.jobs[name]=j

    def do_castor(self,folder):
        if "CASTOR_HOME" in os.environ:
            folder=folder.replace("~",os.environ["CASTOR_HOME"])
        yn=raw_input("Create CASTOR directory '%s'? (y/n) :" %folder)
        if yn=="y":
            castorCreate(folder)

    def do_dir(self,name):
        if not name in self.jobs:
            print "ERROR: Unknown job: %s" % name
            return
        castorDir(self.jobs[name].get("storagepath")[:-1]+self.jobs[name].get("userremotedir"))

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

    def do_crab(self,name):
        if not name in self.jobs:
            print "ERROR: Unknown job: %s" % name
            return
        crab_path=self.config.globals["jobdir"][1]+"/"+name
        if os.path.exists(crab_path):
            yn=raw_input("Path exists. Continue anyway? (y/n)")
            if(yn!="y"):
                return
        self.jobs[name].crabCreate(self.config.globals,
                                   self.config.globals["jobdir"][1]+
                                   "/"+name)
	self.jobs[name].set("status","CRAB Created")

    def do_submit(self,name):
        if not name in self.jobs:
            print "ERROR: Unknown job: %s" % name
            return
        print "Running CRAB..."
	print header_eq
	ret=self.jobs[name].crabSubmit()
	print header_eq
	if ret:
	    print "CRAB submit completed successfully."
	    self.jobs[name].set("status","CRAB Submitted")
            self.jobs[name].crab_job.submitted=True
            self.do_save()
	else:
	    print "CRAB submit error. Please try again."

    def do_status(self,name):
        if name=="":
            print "Global Status:"
            print header_eq
            if len(self.jobs)==0:
                print "No Jobs!"
            for (n,j) in self.jobs.iteritems():
                if not j.crab_job is None:
                    print "%s\t%s" %(n,j.crab_job.getStatus())
            print header_eq
            return
        if not name in self.jobs:
            print "ERROR: Unknown job: %s" % name
            return
        print "Running CRAB..."
        jobs=self.jobs[name].crabStatus()
        print "CRAB Jobs:"
        print header80
        for j in jobs:
	    print "%s [%s]\t%s\t%s %s" % (j[0],j[1],j[2],j[3],j[4])
        print header80

    def do_stat(self,name):
        if not name in self.jobs:
            print "ERROR: Unknown job: %s" % name
            return
        if self.jobs[name].crab_job==None:
            print "Not yet submitted"
            return
        self.jobs[name].crabStatus()
        print "%s\t%s" %(name,self.jobs[name].crab_job.getStatus())

    def do_list(self,name=""):
        print "Jobs:"
        print header_eq
        if not len(self.jobs):
            print "No jobs yet!"
        for (name,j) in self.jobs.iteritems():
            print "%s\t%s\t%s" % (j.get("name"),j.get("sample"),j.get("status"))
        print header_eq

    def do_watch(self,arg=""):
	while True:
	    try:
            	for (name,j) in self.jobs.iteritems():
	    	     if j.get("status")=="CRAB Submitted":
		     	j.crabStatus()
			if not j.crab_job is None:
				print "%s\t%s" % (name,j.crab_job.getStatus())
	    except KeyboardInterrupt:
		break

    def help_list(self):
        print "List jobs"

    def do_rm(self,name):
        if not name in self.jobs:
            print "ERROR: Unknown job: %s" % name
            return
        del self.jobs[name]

    def do_config(self,param):
        if param=="":
            print "Config:"
            print header_eq
            self.config.printGlobals()
            print header_eq
            return
        print "Edit Config:"
        if param in self.config.default_job.params:
            value=myInput(self.config.default_job.params[param][0],
                      "New value (previous='%s'):" % getRaw(self.config.default_job.params[param][1],self.config.default_job.params[param][0]))
            self.config.default_job.set(param,value)

        elif param in self.config.globals:
            value=myInput(self.config.globals[param][0],
                          "New value (previous='%s'):" % getRaw(self.config.globals[param][1],self.config.globals[param][0]))
            self.config.globals[param]=(self.config.globals[param][0],
                                           setRaw(value,self.config.globals[param][0]),
                                           self.config.globals[param][2])
        else:
            print "Configuration paramater '%s' not found" % param

    def do_EOF(self, line):
        self.quit()

    def help_EOF(self):
        print "Quits the program"

    def do_save(self,arg=""):
	self.config.writeGlobals()
        self.config.writeJobs(self.jobs)

    def quit(self):
        yn=raw_input("Save state before quitting? (y/n/c)")
        if(yn=="y" or yn=="n"):
            if(yn=="y"):
                print "Saving state..."
                self.do_save()
            print "Bye!"
            sys.exit()
        else:
            return

if __name__=="__main__":
    tool=ICFGridTool()
    tool.cmdloop()
