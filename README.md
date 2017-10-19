# check_puppet_nodes
Nagios check for Puppet 4 nodes. Returns a list of failed or changed/unreported/unresponsive nodes

usage: check_puppet_nodes.py -H puppetmaster [-p 8080] [-c 4] [-w 1] [-n 7] [--failed]

* -p - port of your puppetmaster api endpoint. Default is 8080  
* -w - warning threshold, default is 1.
* -c - critical threshold, default is 4.
* -n - number of node names to show is there are too many of them. Default is 7.
* --failed - show only failed nodes. Default is false.
