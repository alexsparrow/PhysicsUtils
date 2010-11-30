import os
import os.path
import sys

def ensure_dir(path):
    """Ensure a given directory exists"""
    if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))

def progress(n1, n2, width = 80, text="" , term="\r", post_text=""):
    """Return string showing a progress bar with percentage n1/n2"""
    frac = float(n1)/float(n2)
    prog_str = "%d / %d" % (n1, n2)
    bar_size = width - 3 - len("%d / %d" % (n2, n2))
    text_str = ""
    if text != "":
        bar_size -= len(text)+3
        text_str = text + " : "
    bar_str = "#"*int(frac*bar_size)
    fmt_str = "%s[{0:<%d}] {1}%s%s" % (text_str, bar_size, post_text, term)
    return fmt_str.format(bar_str, prog_str)

def print_progress(*args, **kwargs):
    sys.stdout.write(progress(*args, **kwargs))
    sys.stdout.flush()

def dispatch_cmd(call_tbl):
    from optparse import OptionParser
    parser = OptionParser()

    for k, v in call_tbl.iteritems():
        parser.add_option("--%s" % k,
                          action="store_true",
                          help = v.__doc__)
    (options, args) = parser.parse_args()
    found = False
    for k, v in call_tbl.iteritems():
        if getattr(options, k.replace("-", "_")):
            v()
            found = True
    if not found:
        print "No valid commands found"
        parser.print_help()
