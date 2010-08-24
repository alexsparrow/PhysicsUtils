
class NodeNotFoundError(Exception): pass
class NodeUnsupportedProtocolError: pass

def se_std_url(protocol, node_info, path):
    host = "%s://%s" % (protocol, node_info["%s_host" % protocol])
    port = ""
    if node_info["%s_port" % protocol] is not None:
        port = ":%d" % node_info["%s_port" % protocol]
    return "".join([host,port, path])

def se_rfio_url(protocol, node_info, path):
    return path

se_path_url_map = {
    "IC_DCACHE": {
        "prefix" : "/pnfs/hep.ph.ic.ac.uk",
        "srm_host" : "gfe02.grid.hep.ph.ic.ac.uk",
        "dcap_host" : "gfe02.grid.hep.ph.ic.ac.uk",
        "srm_port" : 8443,
        "dcap_port" : 22128,
        "srm_path" : "/srm/managerv2?SFN=",
        "supports" : ["srm", "dcap"]
        },
    "CASTOR" : {
        "prefix" : "/castor/cern.ch",
        "srm_host" : "srm://srm-cms.cern.ch",
        "srm_port" : None,
        "dcap_host" : None,
        "dcap_port" : None,
        "srm_path" : "/srm/managerv2?SFN=",
        "supports" : ["srm", "rfio"]
        }
}

se_url_fn_map = {
    "dcap" : se_std_url,
    "srm" : se_std_url,
    "rfio" : se_rfio_url
}

def se_path_to_url(path, protocol = "srm"):
    # First find the node using the path prefix
    node = se_path_to_node(path)
    node_info = se_path_url_map[node]
    # Check it supports requested protocol
    if not protocol in node_info["supports"]:
        raise NodeUnsupportedProtocolError("The specified protocol '%s' is not supported by node %s." % (protocol, node))
    # Get the "url"
    return se_url_fn_map[protocol](protocol, node_info, path)

def se_path_to_node(path):
    node = None
    for k, v in se_path_url_map.iteritems():
        if path.startswith(v["prefix"]):
            node = k
            break
    if node is None:
        raise NodeNotFoundError("No node found matching path '%s'." % node)
    return node

def se_lcg_ls(path):
    import commands,sys
    ret, out = commands.getstatusoutput("lcg-ls %s" % path)
    if ret != 0:
        print "\tError occured:"
        print out
        return []
    for line in out.split("\n"):
        files.append(line)
    return files
