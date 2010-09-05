class InvalidChoiceError: pass
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
def prompt_type(prompt, vtype, default=None):
    val = raw_input(prompt)
    if val == "" and default is not None:
        return default
    try:
        val = vtype(val)
        return val
    except ValueError:
        raise InvalidChoiceError

def confirm_create(j):
    for k,v in j._dict.iteritems():
        print "{0:<10} = {1:<50}".format(k,v)
    print "Continue?"
    return raw_input("") == "y"
