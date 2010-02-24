#!/usr/bin/env python

"""icfGridTool support functions

Much of the logic of the code is in here
"""

from types import *
import os
import os.path
import ConfigParser
import subprocess
import shutil

global_defaults = {
    "jobdir": (StringType, "./jobs", "Job storage directory"),
    "email": (StringType, "", "Email address for CrabServer"),
}

job_defaults = {
    "name": (StringType, "", "Name of job"),
    "sample": (StringType, "", "Sample dataset path"),
    "script": (StringType, "icfNtuple_cfg.py", "Path to CMSSW script"),
    "globaltag": (StringType, "MC_3XY_V18::All", "Global Tag to use"),
    "crabtemplate": (StringType, "./crab_tmpl.cfg",
                     "Path to CRAB template script"),
    "eventsperjob": (IntType, 10000, "Number of events per job."),
    "events": (IntType, -1, "Total number of events to process."),
    "mcinfo": (BooleanType, True, "Flag to generate MC info."),
    "scheduler": (StringType, "glite_slc5", "CRAB Scheduler."),
    "servername": (StringType, "legnaro", "CrabServer name."),
    "copydata": (BooleanType, True, "Crab copy data to storage."),
    "returndata": (BooleanType, False, "Crab return data to user."),
    "storagepath": (StringType, "/castor/cern.ch", "Crab storage path."),
    "userremotedir": (StringType, "", "Crab user remote directory."),
    "storageelement": (StringType, "srm-cms.cern.ch", "Crab storage element."),
    "status": (StringType, "CREATED", "Job status"),
    "crabdir": (StringType, "", "Path to CRAB directory"),
    "outfile": (StringType, "", "Final produced ntuple file")}


def myInput(vtype, name):
    cool = False
    val = None
    while not cool:
        tmp = raw_input(name)
        if vtype == StringType:
            val = tmp
            cool = True
        elif vtype == IntType:
            try:
                val = int(tmp)
                cool = True
            except ValueError:
                print "Incorrect value for int: %s" % tmp
        elif vtype == BooleanType:
            try:
                val = int(tmp)
                if val < 0 or val > 1:
                    raise ValueError
                else:
                    val = bool(val)
                cool = True
            except ValueError:
                print "Incorrect value for bool: %s" % tmp
        if not cool:
            print "Please try again."
    return val


def getRaw(val, vtype):
    if vtype == BooleanType:
        if val:
            return 1
        else:
            return 0
    else:
        return val


def setRaw(val, vtype):
    if type(val) == vtype:
        return val
    elif type(val) == StringType:
        if vtype == IntType:
            return int(val)
        elif vtype == BooleanType:
            if val == "1":
                return True
            elif val == "0":
                return False
            else:
                msg = "Invalid literal for boolean ('%s')" %  val
                raise ValueError(msg)
        else:
            print str(type(val))
            print str(vtype)
            msg = "Invalid literal (%s) : '%s'" % (str(vtype), val)
            raise ValueError(msg)

def castorReplace(path):
    tmp=path
    if "CASTOR_HOME" in os.environ:
        tmp = tmp.replace("~", os.environ["CASTOR_HOME"])
    return tmp

def castorCreate(path):
    try:
        p = subprocess.Popen(["rfmkdir", path])
        p.wait()
        if p.returncode == 0:
            p = subprocess.Popen(["rfchmod", "775", path])
            p.wait()
            if p.returncode == 0:
                return True
        return False
    except Exception, e:
        print e
        return False


def castorDir(path):
    try:
        p = subprocess.Popen(["rfdir", path])
        p.wait()
    except Exception, e:
        print e


def rfcp(src, dest):
    p = subprocess.Popen(["rfcp", src, dest])
    p.wait()
    return (p.returncode == 0)


def rfrm(path):
    p = subprocess.Popen(["rfrm", path])
    p.wait()
    return (p.returncode==0)

def castorListPattern(path, pattern):
    p = subprocess.Popen(["rfdir", path], stdout=subprocess.PIPE)
    (out, err) = p.communicate()
    if not p.returncode == 0:
        print "Error fetching dir %s" % path
        return None
    files = []
    for line in out.split("\n"):
        fields = line.split()
        if (len(fields) and (fields[8].startswith(pattern) or pattern == "")
            and (not fields[0][0] == "d")):
            files.append(fields[8])
    return files


def castorFetchPattern(src, dest, pattern):
    files = castorListPattern(src, pattern)
    if files == None:
        return
    if not dest.endswith("/"):
        dest = dest + "/"
    if not src.endswith("/"):
        src = src + "/"
    try:
        for f in files:
            if not os.path.exists(dest + f):
                print ">> Copying file %s" % f
                if not rfcp(src + f, dest + "/" + f):
                    print ">> Error copying file"
                    return False
    except KeyboardInterrupt:
        print "Interrupted by user"
        return True
    return True


class CrabJob:
    def __init__(self, submitted, path):
        self.path = path
        self.subjobs = []
        self.success_count = 0
        self.fail_count = 0
        self.running_count = 0
        self.unknown_count = 0
        self.submitted = submitted

    def setup(self, job, glob):
        f = open(job.get("crabtemplate"), "r")
        crab = f.read()
        for (k, v) in job.params.iteritems():
            crab = crab.replace("__" + k + "__", str(getRaw(v[1], v[0])))
        for(k, v) in glob.iteritems():
            crab = crab.replace("__" + k + "__", str(getRaw(v[1], v[0])))
        f = open(self.path + "/crab.cfg", "w+")
        f.write(crab)
        shutil.copyfile(job.get("script"),
                        self.path + "/" + os.path.split(job.get("script"))[1])

    def submit(self):
        p = subprocess.Popen(["crab", "-cfg", "crab.cfg",
                              "-create", "-submit", "all"], cwd=self.path)
        p.wait()
        return (p.returncode == 0)

    def parseStatus(self, ostr):
        jobs = []
        lines = ostr.split("\n")
        joblist = False
        for line in lines:
            if line.startswith("--------------"):
                joblist = True
            if line.strip().rstrip() == "":
                joblist = False
            if joblist:
                if line.startswith("----------"):
                    continue
                j = [x.strip().rstrip() for x in line.split()]
                for i in range(len(j), 5):
                    j.append("")
                jobs.append(j)
        return jobs

    def getStatus(self):
        if not self.submitted:
            return "Not Submitted"
        return "%d jobs (%d succeeded, %d failed, %d running, %d unknown)" % (
            len(self.subjobs), self.success_count, self.fail_count,
            self.running_count, self.unknown_count)

    def status(self):
        p = subprocess.Popen(["crab", "-status"],
                           cwd=self.path,
                           stdout=subprocess.PIPE)
        (out, err) = p.communicate(None)
        jobs = self.parseStatus(out)
        self.subjobs = []
        self.fail_count = 0
        self.success_count = 0
        self.running_count = 0
        self.unknown_count = 0
        for j in jobs:
            try:
                jid = int(j[0])
            except:
                print "Error parsing CRAB status"
            if j[1] in ["Done", "Cleared"]:
                jstatus = "Success"
                self.success_count += 1
            elif j[1] in ["Killed", "Aborted", "Done (Failed)"]:
                jstatus = "Failed"
                self.fail_count += 1
            elif j[1] in ["Running"]:
                jstatus = "Running"
                self.running_count += 1
            else:
                jstatus = "Unknown"
                self.unknown_count += 1
            self.subjobs.append((jid, jstatus))
        return jobs


class Job:
    def __init__(self, params):
        self.params = params
        self.crab_job = None

    def get(self, name):
        if not name in self.params:
            raise KeyError("Parameter not found: %s" % name)
        return self.params[name][1]

    def _set(self, name, value):
        self.params[name] = (self.params[name][0], value, self.params[name][2])

    def set(self, name, value):
        if not name in self.params:
            raise KeyError("Paramater not found: %s" % name)
        self._set(name, setRaw(value, self.params[name][0]))

    def __repr__(self):
        strs = []
        for (k, v) in self.params.iteritems():
            strs.append("%s : %s" % (k, v[1]))
            strs.append("\n")
        del strs[len(strs) - 1]
        return "".join(strs)

    def crabCreate(self, glob, path):
        if not os.path.exists(path):
            os.mkdir(path)
        c = CrabJob(False, path)
        c.setup(self, glob)
        self.crab_job = c
        self.set("crabdir", path)

    def crabSubmit(self):
        return self.crab_job.submit()

    def crabStatus(self):
        return self.crab_job.status()


class Config:
    def __init__(self, fname):
        self.conf = ConfigParser.RawConfigParser()
        self.conf.read(fname)
        self.default_job = Job(job_defaults)
        self.globals = global_defaults
        self.fname = fname

    @staticmethod
    def initDefault(fname):
        conf = ConfigParser.RawConfigParser()
        Config.writeSection(conf, job_defaults, "DEFAULT")
        Config.writeSection(conf, global_defaults, "DEFAULT")
        configfile = open(fname, 'wb')
        conf.write(configfile)

    @staticmethod
    def readSection(conf, params, secname):
        for (k, v) in params.iteritems():
            if v[0] == StringType:
                val = conf.get(secname, k)
            elif v[0] == IntType:
                val = conf.getint(secname, k)
            elif v[0] == BooleanType:
                val = False
                tmp = conf.getint(secname, k)
                if tmp == 1:
                    val = True
                elif tmp == 0:
                    val = False
                else:
                    raise ValueError
            params[k] = (params[k][0], val, params[k][2])

    @staticmethod
    def writeSection(conf, params, secname):
        for (k, v) in params.iteritems():
            conf.set(secname, k, getRaw(v[1], v[0]))

    def write(self):
        configfile = open(self.fname, 'wb')
        self.conf.write(configfile)

    def readGlobals(self):
        self.readSection(self.conf, self.default_job.params, "DEFAULT")
        self.readSection(self.conf, self.globals, "DEFAULT")

    def writeGlobals(self):
        self.writeSection(self.conf, self.default_job.params, "DEFAULT")
        self.writeSection(self.conf, self.globals, "DEFAULT")

    def readJobs(self):
        jobs = {}
        for s in self.conf.sections():
            job_params = self.default_job.params.copy()
            self.readSection(self.conf, job_params, s)
            job_name = job_params["name"][1]
            if job_name in jobs:
                raise KeyError("Duplicate job names detected")
            jobs[job_name] = Job(job_params)
            if not job_params["crabdir"][1] == "":
                jobs[job_name].crab_job = CrabJob(
                    job_params["status"][1] == "CRAB Submitted",
                    job_params["crabdir"][1])
        return jobs

    def writeJobs(self, jobs):
        for s in self.conf.sections():
            if not s in jobs:
                self.conf.remove_section(s)
        for (k, v) in jobs.iteritems():
            if not self.conf.has_section(k):
                self.conf.add_section(k)
            self.writeSection(self.conf, v.params, k)
        self.write()

    def printGlobals(self):
        for (k, v) in self.default_job.params.iteritems():
            print "%s = %s" % (k, v[1])
        for (k, v) in self.globals.iteritems():
            print "%s = %s" % (k, v[1])

if __name__ == "__main__":
    pass
