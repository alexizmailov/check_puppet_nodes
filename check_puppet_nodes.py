#!/usr/bin/env python

#############################################################################

# This script was initially developed by Infoxchange for internal use       #
# and has kindly been made available to the Open Source community for       #
# redistribution and further development under the terms of the             #
# GNU General Public License v2: http://www.gnu.org/licenses/gpl.html       #

# This script checks status of P4 nodes. Uses Puppet DB as a source         #
# Usage: check_puppet_nodes.py -H <your puppetmaster hostname> [--failed]   #
# This script is supplied 'as-is', in the hope that it will be useful, but  #
# neither Infoxchange nor the authors make any warranties or guarantees     #
# as to its correct operation, including its intended function.             #
#                                                                           #
# Or in other words:                                                        #
#       Test it yourself, and make sure it works for YOU.                   #
# Author: Alex Izmaylov, Infoxchange company, Oct 2017
#############################################################################

import urllib2, base64, json, argparse

def get_data(REQUEST):
    request = urllib2.Request(REQUEST)
    try:
        response = urllib2.urlopen(request, timeout=5)
    except:
        return -1
    data = response.read()
    return json.loads(data)



def check_failed(result):
    failed_nodes = []
    for node in result:
        if node['latest_report_status']=='failed':
            failed_nodes.append(node['certname'].split(".")[0])

    failed_number = len(failed_nodes)
    if failed_number >= CRIT_THRESHOLD:
        EXIT_CODE = 2
    elif failed_number >= WARN_THRESHOLD:
        EXIT_CODE = 1
    else:
        EXIT_CODE = 0

    NODES = 'nodes'
    if failed_number ==1: # some gramma
        NODES = 'node'

    EXIT_MSG = "{} {} failed ".format(failed_number, NODES)
    if failed_number > SHOW_NODES:
        failed_nodes = failed_nodes[0:SHOW_NODES]

    for node in failed_nodes:
        EXIT_MSG += "{} ".format(node)

    EXIT_MSG += "| Failed={}".format(failed_number)
    return EXIT_CODE, EXIT_MSG



def check_changed(result):
    EXIT_CODE = 0
    EXIT_MSG = ''
    nodes_status = {'changed':[], 'unchanged':[], 'noop':[], 'unresponsive':[], 'unreported':[], 'none':[]}
    perf_data = '| '
    for node in result:
        if node['latest_report_status']!='failed':
            node_name = node['certname'].split(".")[0]
            node_status = node['latest_report_status']
            nodes_status[node_status].append(node_name)

    for status in reversed(sorted(nodes_status)): # un- statuses go first - unresponsive, unreported and so on
        nodes = nodes_status[status]
        node_list = ''
        if status in 'unresponsive unreported changed': # if there are > 0 nodes in this status - show them, <= SHOW_NODES
            if len(nodes):
                EXIT_CODE = 1
            if len(nodes) >= SHOW_NODES:
                node_list = ", ".join(nodes[0:SHOW_NODES])
            else:
                node_list = ", ".join(nodes[0:])

        if len(nodes):
            EXIT_MSG += '{} {} {}, '.format(len(nodes), status, node_list.strip())

        perf_data += "{}{}={} ".format(status[0:1].capitalize(), status[1:].strip(), len(nodes))

    EXIT_MSG = "{}{}".format(EXIT_MSG.strip(', '), perf_data.strip())
    return EXIT_CODE, EXIT_MSG


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Puppetmaster branch checker")
    parser.add_argument("-H", help="The PuppetDB hostname (fqdn)")
    parser.add_argument("-p", default=8080, help="The PuppetDB port. Defaults to 8080")
    parser.add_argument("-w", default=1, type=int, help="Warning if <num> hosts are failing. Defaults to 1.")
    parser.add_argument("-c", default=4, type=int, help="Critical if <num> hosts are failing.  Defaults to 4.")
    parser.add_argument("-n", default=10, type=int, help="How many nodes per status to display.  Defaults to 10.")
    parser.add_argument('--failed', action='store_true', help='Check only failed nodes.')
    args = parser.parse_args()

    if not args.H:
        print "Hostname is not specified, use -H, Luke"
        exit(1)

    HOSTNAME = args.H
    PORT = args.p
    WARN_THRESHOLD = args.w
    CRIT_THRESHOLD = args.c
    FAILED_ONLY = args.failed
    SHOW_NODES = args.n

    request = "http://{0}:{1}/pdb/query/v4/nodes".format(HOSTNAME, PORT)
    result = get_data(request)
    if result == -1:
        print "WARN: {} is unaccessible".format(HOSTNAME)
        exit(1)
    if FAILED_ONLY:
        EXIT_CODE, EXIT_MSG = check_failed(result)
    else:
        EXIT_CODE, EXIT_MSG = check_changed(result)

    print EXIT_MSG
    exit(EXIT_CODE)

