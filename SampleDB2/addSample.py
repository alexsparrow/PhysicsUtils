#!/usr/bin/env python
from store import openStore, JSONCancelError
from config import conf
from utils import prompt_retry, prompt_type, confirm_create, InvalidChoiceError

@prompt_retry
def prompt_sample_name(store):
    name = raw_input("Sample Name:")
    if not name.startswith("/"):
        print "Sample name should begin with /"
        raise InvalidChoiceError
    if store.Exists(name+"/_sample_.json"):
        print "Sample already exists"
        raise InvalidChoiceError
    return name

if __name__ == "__main__":
    store = openStore(conf["path"])
    name = prompt_sample_name(store)
    with store.Create(name + "/_sample_.json") as j:
        j.name = name
        j.dbs = prompt_type("DBS Path:", str, "")
        j.cross_section = prompt_type("Cross Section:", float, -1)
        j.events = prompt_type("Events:", int, -1)
        if not confirm_create(j):
            raise JSONCancelError


