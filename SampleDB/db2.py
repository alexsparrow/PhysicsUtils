import sqlite3
import os, os.path, getpass
icf_sample = [
    ("name" , "TEXT NOT NULL"),
    ("cross_section" , "REAL"),
    ("pt_bin" , "REAL"),
    ("events" , "INTEGER"),
    ("latest_version" , "TEXT"),
    ("dbs" , "TEXT")
]

icf_version = [
    ("name" , "TEXT NOT NULL"),
    ("job_id" , "INTEGER NOT NULL"),
    ("subjob", "INTEGER NOT NULL"),
    ("icf_sample_id" , "INTEGER NOT NULL"),
    ("int_lumi" , "REAL"),
    ("comment" , "TEXT"),
    ("created_by" , "TEXT NOT NULL"),
    ("created_date" , "TEXT NOT NULL"),
]

icf_file = [
    ("job_id" , "INTEGER NOT NULL"),
    ("subjob", "INTEGER NOT NULL"),
    ("location" , "TEXT NOT NULL"),
    ("path" , "TEXT NOT NULL"),
    ("events" , "INTEGER")
]

def create_sql(tbl_name, fields):
    sql = "create table %s(%s);"
    field_list = ",\n".join(["%s %s" % (a,b) for a,b in fields])
    return sql % (tbl_name, field_list)

def insert_sql(tbl_name, fields):
    return "insert into %s (%s) VALUES(%s)" % (
        tbl_name,
        ",".join(["%s" % a for a,b in fields]),
        ",".join(["?" for a,b in fields]))

class NeedsLockError(Exception): pass
class DBLockedError(Exception):
    def __init__(self, user, time):
        self._user = user
        self._time = time
class CantLockError(Exception): pass

def needs_lock(func):
    def new_func(self, *args, **kwds):
        if self._lock is not None and self._lock.valid():
            return func(self, *args, **kwds)
        else:
            raise NeedsLockError("Attempt to run write operation (%s) on a non-locked DB."
                                % func.func_name)
    new_func.__doc__ = func.__doc__
    return new_func

class Lock(object):
    def __init__(self, path, force=False):
        self._valid = False
        if path is None:
            return
        if os.path.exists(path):
            user = open(path).readline()[:-1]
            if user != getpass.getuser():
                if force:
                    self._destroy_lock(path)
                else:
                    raise DBLockedError(user, os.path.getmtime(lockpath))
        self._path = path
        self._valid = self._create_lock(path, getpass.getuser())

    def _create_lock(self, path, user):
        try:
            lockfile = open(path, "w")
            print>>lockfile, getpass.getuser()
            lockfile.close()
            return True
        except Exception, e:
            print e
            raise CantLockError

    def destroy_lock(self, path):
        os.unlink(path)

    def __del__(self):
        if self._valid:
            self.destroy_lock(self._path)
            self._valid = False

    def valid(self):
        return self._valid

class DB(object):
    def __init__(self, path, lock=False, lock_exists_cb=None):
        self._path = path
        self._db = sqlite3.connect(path)
        self._db.row_factory = sqlite3.Row
        #sqlite3.enable_callback_tracebacks(True)
        if not lock:
            self._lock = None
        else:
            try:
                self._lock = Lock(os.path.dirname(path)+"/sqlite.lock")
            except DBLockedError,e:
                print "Database locked by user %s %d seconds ago" % (e._user, e._time)

        self._db.set_authorizer(self._auth_db)

    def _auth_db(self,*opts):
        if self._lock is not None and self._lock.valid():
            return sqlite3.SQLITE_OK
        else:
            if opts[0] in (sqlite3.SQLITE_READ, sqlite3.SQLITE_SELECT, 31):
                return sqlite3.SQLITE_OK
            else:
                return sqlite3.SQLITE_DENY

    def execute(self, sql, *opts):
        return self._db.execute(sql, *opts)

    def select(self, table, *args, **kwds):
        if "fields" in kwds:
            fields = kwds["fields"]
        else:
            fields = None
        if "where" in kwds:
            where = kwds["where"]
        else:
            where = None
        if fields is None:
            sql = "select rowid, * from %s" % table
        else:
            sql = "select %s from %s" % (
                ", ".join([str(k) for k in tuple(fields)]), table)
        if where is not None:
            sql += " where %s;" % where
        print sql
        return self._db.execute(sql,*args)

    def add_sample(self, name, dbs, cross_section, ptbin, events,
                   latest="" ):
        sql = insert_sql("icf_sample", icf_sample)
        return self._db.execute(sql, (name,
                                      cross_section,
                                      ptbin,
                                      events,
                                      latest,
                                      dbs)).lastrowid

    def add_version(self, sample, name, job, subjob, int_lumi=-1,
                    comment = "", created_by = getpass.getuser(), created_date = time.asctime()):
        sql = insert_sql("icf_version", icf_version)
        return self._db.execute(sql, (name,
                                      job,
                                      subjob,
                                      sample,
                                      int_lumi,
                                      comment,
                                      created_by,
                                      created_date)).lastrowid

    def add_file(self, job_id, subjob, location, path, events):
        sql = insert_sql("icf_file", icf_file)
        return self._db.execute(sql, (job_id, subjob, location, path, events)).lastrowid

    @needs_lock
    def update(self, rid, field, value):
        if len(field.split("."))<=1:
            raise ValueError("Invalid field name supplied")
        table = field.split(".")[0]
        field = field.split(".")[1]
        query = "update %s set %s = ? where rowid=?" % (table, field)
        self._db.execute(query, (value, rid))

    @needs_lock
    def commit(self):
        self._db.commit()

    @needs_lock
    def delete_row(self, table, rowid):
        self.execute("delete from %s where rowid=?" %table, (rowid,))


def db_init(path):
    db = sqlite3.connect(path)
    print "Creating table 'icf_sample'"
    db.execute(create_sql("icf_sample", icf_sample))
    print "Creating table 'icf_version'"
    db.execute(create_sql("icf_version", icf_version))
    print "Creating table 'icf_file'"
    db.execute(create_sql("icf_file", icf_file))
    db.commit()
    print "Done."
