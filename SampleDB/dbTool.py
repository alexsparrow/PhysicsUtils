#!/usr/bin/env python
import db2
import sys, os, subprocess, tempfile
from pager import Pager
import utils2 as utils
class InvalidChoiceError: pass
class UserQuitError: pass


db = None
db_dirty = False

def ui_ansi(s):
    return "%s[%s" % (chr(27), s)

def ui_standout(s):
    return ui_ansi("7m") + s + ui_ansi("0m")

def ui_bold(s):
    return ui_ansi("1m") + s + ui_ansi("0m")

def ui_red(s):
    return ui_ansi("31m") + s + ui_ansi("0m")

def ui_edit(lines):
    (fd, tempf) = tempfile.mkstemp()
    try:
        f = os.fdopen(fd, "w")
        f.write("\n".join(lines))
        f.close()
        ed = "nano"
        if "EDITOR" in os.environ:
            ed = os.environ["EDITOR"]
        subprocess.call([ed, tempf])
        f = open(tempf, "r")
        f.read().split("\n")
    finally:
        os.unlink(tempf)
    return lines

def prompt_retry(func):
    def newfunc(*args, **kwds):
        while True:
            try:
                return func(*args, **kwds)
            except InvalidChoiceError:
                print "Invalid input."
                print "[t]ry again or"
                print "[a]bort the current action"
                if raw_input("[t/a]: ") == "a":
                    raise UserQuitError
                else:
                    continue
            break
    newfunc.__doc__ = func.__doc__
    return newfunc

@prompt_retry
def prompt_name(prompt, table):
    name = raw_input(prompt)
    for r in db.execute("select rowid from %s where name = ?" %table,
                        (name,)):
        print "This name already exists in the DB"
        raise InvalidChoiceError
    if name == "":
        print "Invalid name"
        raise InvalidChoiceError
    return name

@prompt_retry
def prompt_dbs():
    dbs = raw_input("DBS Name: ")
    return dbs

@prompt_retry
def prompt_numeric(prompt, t, default=None):
    val = raw_input(prompt)
    if val == "" and default is not None:
        return default
    try:
        val = t(val)
        return val
    except ValueError:
        raise InvalidChoiceError

@prompt_retry
def prompt_choice(options):
    for k, v in options:
        if k == "-":
            print "======================"
        else:
            print "[%s]%s" % (ui_red(k[0]), k[1:])
    choice = raw_input("Option (%s): " % "/".join([opt[0][0]  for opt in options if opt[0]!="-"]))
    opts = {}
    for k, v in options:
        opts[k[0][0]] = v
    if choice in opts:
        if getattr( opts[choice], "__call__", False):
            return opts[choice]()
        else:
            return opts[choice]
    else:
        raise InvalidChoiceError

def prompt_bool():
    return prompt_choice([("True", True),
                          ("False", False)])

def prompt_yes():
    return prompt_choice([("yes", True), ("no", False)])

def prompt_sure(name, fields):
    print
    print "You are about to add a %s to the DB."
    print "Are you sure you want to proceed?"
    print "="*50
    for k, v in fields.iteritems():
        print ui_standout(k) + " : " + str(v)
    print "="*50
    return prompt_yes()

@prompt_retry
def prompt_pager(prompt,
                 sql,
                 format_str,
                 ret_val=["rowid"],
                 *values):
    rows = db.execute(sql, [str(v) for v in values])
    row_arr = [dict(r) for r in rows]
    p = Pager(prompt, [format_str.format(**r) for r in row_arr])
    if p.sel_idx == -1 or len(p.inputs) == 0:
        raise InvalidChoiceError
    else:
        return [[r[k] for k in ret_val] for r in row_arr][p.sel_idx]


def prompt_version():
    versions = db.select("icf_version", ["distinct name"], "icf_sample_id = icf_version.rowid")


def add_sample():
    name = prompt_name("Sample Name: ", "icf_sample")
    dbs = prompt_dbs()
    cross_section = prompt_numeric("Cross Section: ", float, -1)
    ptbin = prompt_numeric("Pt Bin: ", float, -1)
    nevents = prompt_numeric("#Events: ", int, -1)
    if prompt_sure("Sample",
                   {"Name":name,
                    "DBS":dbs,
                    "Cross Section":cross_section,
                    "Pt Bin":ptbin,
                    "# Events":nevents}):
        try:
            db.add_sample(name, dbs, cross_section, ptbin, nevents)
            print "DONE"
            db_dirty = True
        except Exception,e:
            print "ERROR: %s" % e
            raw_input("Press Enter")

def add_version():
    sample = prompt_pager("Please select a sample",
                          "select rowid, name, dbs from icf_sample",
                          "{rowid:<6} {name:<20} {dbs:<30}", ["rowid", "name"])
    name = prompt_name("Version Name: ", "icf_version")
    jobs = []
    print "Would you like to extend an existing version?"
    if prompt_yes():
        version = prompt_pager("Please choose a version",
                               "select rowid, name, created_date, created_by from icf_version where icf_version.icf_sample_id=?",
                               "{rowid:<6} {name:<20} {created_date:<10} {created_by:<10}",
                               ["name"], sample[0])

        for j in db.execute("select rowid, job_id, name, int_lumi, subjob from icf_version where name=?",
                            version):
            jobs.append((j["rowid"], j["int_lumi"], j["subjob"]))
    finished = False
    filter_dbs = raw_input("Filter by DBS: ")
    while not finished:
        sql = "select job.rowid, user, state, dset.dataset, tag.susycaf, dset.rowid, tag.rowid, job.rpath from job, dset, tag where dset.rowid = job.dsetid and tag.rowid = job.tagid"
        if filter_dbs:
            sql += " and dset.dataset LIKE ?"
            job = prompt_pager("Please choose a job", sql,
                               "{rowid:<6} {user:<10} {state:<10} {dataset:<20} {susycaf:<10} {rpath:<30}", ["rowid", "dataset"], filter_dbs+"%")
        else:
            job = prompt_pager("Please choose a job", sql,
                               "{rowid:<6} {user:<10} {state:<10} {dataset:<20} {susycaf:<10} {rpath:<30}", ["rowid", "dataset"])
        subjob = 0
        if len(job[1].split(",")) > 1:
            print "This job contains several subjobs"
            print "Please choose which subjob"
            subjob = Pager("Choose subjob", job1.split(",")).sel_idx
            if subjob == -1:
                return
        print "Added job # %d (subjob # %d)" % (job[0], subjob)
        int_lumi = prompt_numeric("Integrated Luminosity: ", float, -1)
        jobs.append((job[0],int_lumi, subjob))
        print "Finished adding jobs?"
        finished = prompt_yes()
    print "Should this be the recommended version?"
    recommended = prompt_yes()
    if prompt_sure("Version",
                   {"Sample": sample[1],
                   "Version Name" : name,
                   "Jobs" : jobs,
                   "Recommended" : recommended}):
        try:
            for j in jobs:
                db.add_version(sample[0], name, j[0], j[2])
            if recommended:
                db.update(sample[0], "icf_sample.latest_version", name)
            print "DONE"
            db_dirty = True
        except Exception,e:
            print "ERROR: %s" % e
            raw_input("Press Enter")

def add_files():
    filter_dbs = raw_input("Filter by DBS: ")
    sql = "select job.rowid, user, state, dset.dataset, tag.susycaf, dset.rowid, tag.rowid, job.rpath from job, dset, tag where dset.rowid = job.dsetid and tag.rowid = job.tagid"
    if filter_dbs:
        sql += " and dset.dataset LIKE ?"
        job = prompt_pager("Please choose a job", sql,
                           "{rowid:<6} {user:<10} {state:<10} {dataset:<20} {susycaf:<10} {rpath:<30}", ["rowid", "rpath", "dataset"], filter_dbs+"%")
    else:
        job = prompt_pager("Please choose a job", sql,
                           "{rowid:<6} {user:<10} {state:<10} {dataset:<20} {susycaf:<10} {rpath:<30}",  ["rowid", "rpath", "dataset"])
    ds_paths = []
    if len(job[2].split(",")) == 1:
        ds_paths = [(0, job[2],job[1])]
    else:
        for i, d in enumerate(job[2].split(",")):
            ds_paths.append((i, d, job[1]+"/"+d[1:].replace("/", ".")))
    print "You have chosen job: %d" % job[0]
    print "{0:<40} {1:<40}".format("Dataset", "Path")
    for i, d, p in ds_paths:
        print "{0:<40} {1:<40}".format(d,p)
    print "Scan for files?"
    files = []
    if prompt_yes():
        for i, d, p in ds_paths:
            print "="*70
            print "Scanning %s for files..." % p
            print "="*70
            url = utils.se_path_to_url(p)
            flist = utils.se_lcg_ls(url)
            flist = ui_edit(flist)
            print "This subjob has %d files" % len(flist)
            print "Are you sure you want to add them to the DB?"
            if prompt_yes():
                for f in flist:
                    db.add_file(job[0], i, utils.se_path_to_node(f), f, -1)
                print "Done"
            else:
                print "Subjob %s not added" % d
        lines = []
        for d, f in files:
            lines.extend(f)
        ui_edit(lines)
    print

def lock_db():
    global db
    if db_dirty:
        print "Do you wish to save your changes first."
        print "If not they will be lost."

        if not prompt_choice([("save data", db.commit),
                              ("discard data", True),
                              ("cancel", False)]):
            return
    db = db2.DB("./sqlite.test.db", not lock_state())

def lock_state():
    return db._lock is not None and db._lock.valid()

def db_save():
    print "Saving..."
    db.commit()

def user_quit():
    if db_dirty:
        print "Save before quitting?"
        if prompt_yes():
            db_save()
    sys.exit()

if __name__ == "__main__":
    global db
    db = db2.DB("sqlite.test.db", False)
    while True:
        try:
            print " *** Main Menu *** "
            print "{0:<10} : {1:<10}".format("DB Locked",
                                             ui_standout(str(lock_state())))
            print "{0:<10} : {1:<10}".format("DB Changed",
                                             ui_standout(str(db_dirty)))
            choices = [("-", None)]
            if lock_state():
                choices.append(("drop lock", lock_db))
            else:
                choices.append(("lock db", lock_db))
            choices.extend([
                    ("commit changes", db_save),
                    ("-", None),
                    ("sample add", add_sample),
                    ("version add", add_version),
                    ("files add", add_files),
                    ("-", None),
                    ("quit", user_quit)])
            prompt_choice(choices)
        except UserQuitError:
            continue
