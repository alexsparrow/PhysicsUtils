
def run(tree, ops, f):
    print "-"*70
    for o in ops:
        print "%s =>" % o.name()
        print "\n".join(["\t%s" % d for d in o.describe().split("\n")])
    print "-"*70
    for o in ops:
        o.start(tree, f)
    for ev in tree:
        for o in ops:
            if not o.process(ev):
                break
    for o in ops:
        o.end(tree)
        rep = o.report()
        if rep is not None:
            print " {0:<20} ".format(o.name())+ "="*50
            print rep
            print "="*72
