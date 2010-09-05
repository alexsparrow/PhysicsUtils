#!/usr/bin/env python
from store import openStore, JSONCancelError
from config import conf
from utils import prompt_retry, prompt_type, confirm_create
from pager import Pager
import sys, readline
import utils2 as utils

@prompt_retry
def prompt_sample(store):
    samples = store.Collect(store.FindByName("_sample_.json"),
                            ["name", "dbs"])
    l = zip(samples["name"], samples["dbs"])
    if len(l) == 0:
        print "No samples found. Exiting"
        sys.exit(1)
    p = Pager("Please choose a sample",
              ["{0:<15} {1:<30}".format(*i) for i in l])
    if p.sel_idx == -1:
        raise InvalidChoiceError
    else:
        return l[p.sel_idx][0]

@prompt_retry
def prompt_version(store, sample):
    versions = store.Collect(store.Glob(sample+"/*.json", True),
                             ["name", "created_by", "created_date"])
    l = zip(versions["name"], versions["created_by"], versions["created_date"])
    p = Pager("Please choose a version to extend",
              ["New Version"] +["{0:<15} {1:<15} {2:<15}".format(*i) for i in l])
    if p.sel_idx == -1:
        raise InvalidChoiceError
    elif p.sel_idx == 0:
        return None
    else:
        return l[p.sel_idx-1][0]

@prompt_retry
def prompt_version_name(store):
    name = raw_input("Version Name:")
    if store.Exists(sample+"/"+name+".json"):
        print "Version called '%s' already exists." % name
        raise InvalidChoiceError
    else:
        return name

@prompt_retry
def prompt_job(db_path):
    import sqlite3
    db = sqlite3.connect(db_path)
    rows = db.execute("select job.rowid, dset.dataset, state, rpath from job, dset where dset.rowid = job.dsetid").fetchall()
    p = Pager("Please choose a job", ["{0:<6} {1:<30} {2:<10}".format(*j) for j in rows])
    if p.sel_idx == -1:
        raise InvalidChoiceError
    else:
        return rows[p.sel_idx]

@prompt_retry
def prompt_subjob(db_path, subjobs):
    p = Pager("Please choose a subjob", ["{0:<40}".format(s) for s in subjobs])
    if p.sel_idx == -1:
        raise InvalidChoiceEror
    else:
        return p.sel_idx


if __name__ == "__main__":
    store = openStore(conf["path"], lock=True)
    sample = prompt_sample(store)
    extend = prompt_version(store, sample)
    blocks = []
    while True:
        j = prompt_job(conf["db_path"])
        path = j[3]
        sub = 0
        if len(j[1].split(",")) > 1:
            sub = prompt_subjob(conf["db_path"], j[1].split(","))
            path = j[3] + '/' + string.replace(j[1][1:], '/', '.')
        print "Scan path '%s for files?" % path
        files = []
        file_counts = {}
        if raw_input() == "y":
            files.extend(utils.se_lcg_ls(utils.se_path_to_url(path)))
        print "Files found: %d" % len(files)
        print "Scan for event counts?"
        if raw_input() == "y":
            import ROOT as r
            for idx, f in enumerate(files):
                print "*"*60
                print "Scanning file (%d of %d): %s" % (idx,
                                                        len(files),
                                                        utils.se_path_to_url(f, "dcap"))
                f = r.TDCacheFile(utils.se_path_to_url(f, "dcap"))
                if f is None:
                    continue
                d = f.Get("susyTree")
                if d is None:
                    print "Directory not found"
                    continue
                t = d.Get("tree")
                if t is None:
                    print "tree not found"
                    continue
                file_counts[idx] = t.GetEntriesFast()
                print "Contains %d events" % file_counts[idx]
        file_info = []
        total_events = 0
        for idx, f in enumerate(files):
            if idx in file_counts:
                n = file_counts[idx]
                total_events += n
            else:
                n = -1
            file_info.append({"path" : f,
                              "events" : n})
        print "Add?"
        if raw_input() == "y":
            blocks.append({"job":j[0],
                           "dataset": j[1].split(",")[sub],
                           "files" : file_info,
                           "node" : utils.se_path_to_node(path),
                           "events" : total_events})
        print "Add more jobs?"
        if raw_input() != "y":
            break
    name = prompt_version_name(store)

    if extend is not None:
        with store.Copy(sample+"/"+extend+".json",sample+"/"+name+".json") as j:
            j.name = name
            j.blocks.extend(blocks)
            if not confirm_create(j):
                raise JSONCancelError
    else:
        with store.Create(sample+"/"+name+".json") as j:
            j.name = name
            j.blocks = blocks
            if not confirm_create(j):
                raise JSONCancelError
