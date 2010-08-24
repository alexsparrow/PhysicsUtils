#!/usr/bin/env python

class SampleDBError(Exception): pass
class SampleNotFoundError(SampleDBError): pass
class VersionNotFoundError(SampleDBError):
    def __init__(self, sample, version, available_versions):
        self.sample = sample
        self.version = version
        self.available_versions = available_versions
    def __str__(self):
        return self.sample +" : " + self.version

class UnsupportedError(Exception): pass
try:
    import sqlite3
except:
    print "No SQLite Support"

class DB(object):
    def _files_by_sample(self,
                         name,
                         version = None,
                         ignore_missing = False):
        samples = self._find_samples(name)
        if len(samples) == 0:
            raise SampleNotFoundError("No samples matching %s found" % name)
        files = []
        for rowid, name in samples:
            versions = self._find_version(rowid, version)
            if len(versions) == 0:
                available_versions = self._list_versions(rowid)
                raise VersionNotFoundError(name, version , available_versions)
            jobs = self._find_jobs(versions)
            files.append(self._find_files(jobs))
        return files

    def _version_info(self, s, version):
        versions = self._find_version(s[0], version)
        jobs =  self._find_jobs(versions)
        info = {}
        for j in jobs:
            job_info = self._job_info(j)
            info["susycaf_tag"]=job_info["susycaf_tag"]
        return info

    def sample(self,
               name=None,
               version=None,
               dbs=None,
               ignore_missing_version=False):
        info = {}
        if name:
            try:
                files = self._files_by_sample(name, version)
            except VersionNotFoundError,e:
                print
                if e.version is None:
                    print  "There is no version of sample '%s' marked as LATEST. Please correct the db or explicitly specify a version to use." % e.sample
                else:
                    print "No version of sample %s matching %s" (e.sample, e.version)
                print "Available Versions:"
                for v in e.available_versions:
                    print v
                print
                raise
            samples = self._find_samples(name)
            for s in samples:
                samp_info = self._sample_info(s)
                version_info = self._version_info(s, version)
                info["name"] = samp_info["name"]
                info["cross_section"] = samp_info["cross_section"]
                info["ntuple_tag"] = version_info["susycaf_tag"]
                info["files"] = []
                for f in files:
                    info["files"].append(f)
        elif dbs:
            raise UnsupportedError("Searching by DBS path not ready yet")
        return info

    def pset(**opts):
        from icf.core import PSet
        if not "nt_format" in opts:
            raise ValueError("Must supply nt_format argument")
        nt_format = opts["nt_format"]
        if "pset_name" in opts:
            pset_name = opts["pset_name"]
            del opts["pset_name"]
        else:
            pset_name = None
        info = self.sample(**opts)

        ps = PSet()
        if pset_name is not None:
            ps._quiet_set("Name", pset_name)
        else:
            if "name" in opts:
                ps._quiet_set("Name", opts["name"].replace("/", "_").replace("*",""))
            elif "dbs" in opts:
                ps._quiet_set("Name", opts["name"].replace("/", "_"))
            else:
                raise ValueError("Cannot construct name")
        ps._quiet_set("Format", nt_format)
        ps._quiet_set("File", info["files"])
        if info["cross_section"] == -1:
            ps._quiet_set("Weight", 1.)
        else:
            ps._quiet_set("CrossSection", info["cross_section"])
        return ps

class SQLiteDB(DB):

    def __init__(self, path):

        self._path = path
        self._db = sqlite3.connect(path)
        self._db.row_factory = sqlite3.Row
        self._db.set_authorizer(self.auth_cb)
        sqlite3.enable_callback_tracebacks(True)

    def auth_cb(self, *opts):
        auth = {sqlite3.SQLITE_SELECT:sqlite3.SQLITE_OK,
                sqlite3.SQLITE_READ:sqlite3.SQLITE_OK,
                31: sqlite3.SQLITE_OK}
        if opts[0] in auth:
            return auth[opts[0]]
        else:
            return sqlite3.SQLITE_DENY

    def _find_samples(self, name):
        if name.endswith("*"):
            name = name.replace("*", "%")
            sql = "select rowid, name from icf_sample where name like ?"
        else:
            sql = "select rowid, name from icf_sample where name = ?"
        rows = self._db.execute(sql, (name,))
        return [(r["rowid"], r["name"]) for r in rows]

    def _find_version(self, sample, version=None):
        if version is None:
            sql = """
select icf_version.rowid from icf_sample, icf_version where icf_version.icf_sample_id=? and icf_version.name=icf_sample.latest_version
"""
            rows = self._db.execute(sql, (sample,))
        else:
            sql = """
select icf_version.rowid from icf_sample, icf_version where icf_version.icf_sample_id=? and icf_version.name=?
"""
            rows = self._db.execute(sql, (sample, version))
        return [r["rowid"] for r in rows]

    def _list_versions(self, sample):
        rows = self._db.execute("""
select distinct icf_version.name from icf_version, icf_sample where icf_version.icf_sample_id=?""", (sample,))
        return [r["name"] for r in rows]


    def _find_jobs(self, version):
        sql = "select job.rowid, icf_version.job_id, icf_version.rowid from icf_version, job where job.rowid = icf_version.job_id"
        sql += " and (" +"or".join(["icf_version.rowid = ?"]) + ")"
        rows = self._db.execute(sql, tuple(version))
        return [r["rowid"] for r in rows]

    def _find_files(self, job, location=None):
        sql = "select icf_file.rowid, icf_file.job_id, job.rowid from icf_file, job where icf_file.job_id = job.rowid"
        sql += " and (" + "or".join(["job.rowid =?"])+")"
        if location:
            sql += " and icf_file.location = ?"
            job.append(location)
        rows = self._db.execute(sql, tuple(job))
        return [(r["icf_file.rowid"], r["icf_file.path"], r["icf_file.events"]) for r in rows]

    def _job_info(self, job):
        row = self._db.execute("select tag.susycaf from tag, job where job.rowid = ? and job.tagid = tag.rowid", (job,)).fetchone()
        info = {"susycaf_tag":row["susycaf"]}
        return info

    def _sample_info(self, sample):
        row = self._db.execute("select name, cross_section from icf_sample where rowid = ?", (sample[0],)).fetchone()
        return {"name":row["name"], "cross_section":row["cross_section"]}

# Database mapping
databases = {
    "icf" : {
        "sqlite_afs": "/afs/cern.ch/user/a/arlogn/www/web/ICF_Database/sqlite.db",
        "www": "arlogb.web.cern.ch/cgi-bin/dbconnect.cgi"
        }
}

method_classes = {
    "sqlite_afs" : SQLiteDB,
    "www" : None
}

def sample_db(self, db, method="sqlite_afs"):
    if not db in databases:
        raise InvalidDatabaseError("Database '%s' not found" % db)
    if method in databases[db] and method in method_classes:
        return method_classes[method](databases[db][method])

if __name__ == "__main__":
        db = SQLiteDB("sqlite.test.db")
        print db.sample("ert","ert")
