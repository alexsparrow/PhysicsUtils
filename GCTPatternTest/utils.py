oct2bin = {'0': '000', '1': '001', '2': '010', '3': '011', '4': '100',
 '5': '101', '6': '110', '7': '111'}

def bin(n):
    if n < 0:
        return "-" + bin(-n)
    # Build list of groups of three binary digits
    s = [oct2bin[octdigit] for octdigit in ("%o" % n)]
    # Merge list to single string and remove leading zeros
    s = "".join(s).lstrip("0")
    return s or "0"

def ntobools(n):
    s=bin(n)
    q=[]
    for c in s:
        if c=='1':
            q.append(True)
        elif c=='0':
            q.append(False)
    return q

def count_true(bools):
    count=0
    for b in bools:
        if b:
            count+=1

    return count

def array_sub(bools,vals,off):
    count=0
    ret=[]

    for b in bools:
        if b:
            ret.append(vals[count])
            count+=1
        else:
            ret.append(off)
    return ret

def unique_elements(arr):
    tbl=[]
    for i in arr:
        if not (i in tbl):
            tbl.append(i)
    return tbl

def perm(l):
    sz = len(l)
    if sz <= 1:
        return [l]
    return [p[:i]+[l[0]]+p[i:] for i in xrange(sz) for p in perm(l[1:])]

def permute(vals,n,permd=False,size=8,min=0,max=256,off_val=0):
    q=[]
    for i in range(min,max):
        b=ntobools(i)
        while len(b)<size:
            b.append(False)
        ord=count_true(b)
        if ord==n:
            if permd:
                l=perm(vals)
            else:
                l=[vals]
            l=unique_elements(l)

            for v in l:
                q.append(array_sub(b,vals,off_val))
    return q
