'''
Scan a switches.log file to prepare a history of the InterMapper Layer2 scan/harvest operation

The program is a filter - it reads stdin and writes to stdout.
These can be overridden by -i and -o arguments.

There are four important pieces of information garnered from the file.
They require that log.kali and log.sql both be true before beginning the scan
As scanlogs.py reads the input file it detects:

SQL "INSERT INTO device" lines that contain data about the IMID, the IP address, name/label, and sysSvcs for all "pollers"
<KC_opentable lines that contain an IMID for a device and the KCid to link it to the following "<KR"
<KR with a matching KCid that also contains a "table id" and a tableTitle (ifIndex, ifAddrTable, etc.)
<KU_tabledata lines with the same "table ID" to data, or to a "ParseError" or "NoAnswer" to indicate that it's the last line.

In addition, scanl2logs creates a history of interesting commands that are printed to show what happened.
'''

import os
import sys
import argparse
from l2historybuffer import L2HistoryBuffer
from l2logfile import L2LogFile
from l2scantables import L2ScanTables


def main(argv=None):

    try:
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument("-i", '--infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
        parser.add_argument("-o", '--outfile', nargs='?', type=argparse.FileType('w'), default=sys.stdout)
        theArgs = parser.parse_args()
    except Exception, err:
        return str(err)

    f = theArgs.infile                      # the argument parsing returns open file objects
    fo = theArgs.outfile

    # Now to the meat of the program

    thelog = L2LogFile(f)                  # initialize the file object
    theHistory = L2HistoryBuffer(thelog)
    theScanInfo = L2ScanTables(thelog)

    while True:
        line = thelog.getline()
        if line == "":
            break
        theHistory.logit(line)
        theScanInfo.processLine(line)

    fo.write("Reading switches.log, %s\n" % os.path.abspath(f.name))
    fo.write(theHistory.gLineBuffer+"\n")
    fo.write("Resulting Table Info\n")
    fo.write(theScanInfo.printL2Tables())                         # print the relevant information

if __name__ == "__main__":
    sys.exit(main())
