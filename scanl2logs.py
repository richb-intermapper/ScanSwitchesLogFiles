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
from time import strftime
from l2historybuffer import L2HistoryBuffer
from l2logfile import L2LogFile
from l2scantables import L2ScanTables

thelog = None
theScanInfo = None
printTables = False

def makeScanSummary(lines, diags, tables, scanct):
    retline = "Starting scan %d\n" %(scanct)            # Heading line
    retline += lines                                    # print the lines of history
    retline += diags
    if printTables:
        retline += "\nSNMP Tables for scan %d:\n" % (scanct)
        retline += tables                               # print the table information
    else:
        retline += "\nSNMP Tables not displayed:\n"
    retline += "End of scan %d\n\n" % (scanct)          # and epilog
    return retline

def main(argv=None):

    try:
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument("-i", '--infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
        parser.add_argument("-o", '--outfile', nargs='?', type=argparse.FileType('w'), default=sys.stdout)
        parser.add_argument("--notables", action="store_false", help="Don't print the tables")
        theArgs = parser.parse_args()
    except Exception, err:
        return str(err)

    global printTables
    printTables = theArgs.notables

    f = theArgs.infile                      # the argument parsing returns open file objects
    fo = theArgs.outfile

    thelog = L2LogFile(f)                   # initialize the file object
    theHistory = L2HistoryBuffer(thelog)    # initialize the history of log lines
    theScanInfo = L2ScanTables(thelog)      # initialize the contents of each of the Layer2 table scans

    now = strftime("%Y-%m-%d %H:%M:%S")
    fo.write(" %s, Reading switches.log from: %s\n\n" % (now, os.path.abspath(f.name)))

    scanct = 1
    while True:
        line = thelog.getline()
        if line == "" or theScanInfo.isNewScan(line):       # EOF or starting a new scan, write out what has accumulated
            (diags, tables) = theScanInfo.printL2Tables()
            report = makeScanSummary(theHistory.gLineBuffer, diags, tables, scanct)
            fo.write(report)

            if line == "":                                  # finally hit EOF, so break out
                break
            else:                                           # Otherwise...
                theScanInfo = L2ScanTables(thelog)          # Create a new ScanTables object
                theHistory = L2HistoryBuffer(thelog)        # and HistoryBuffer object
                scanct += 1                                 # and bump the scan counter

        # and then process this next line
        theHistory.logit(line)
        theScanInfo.processLine(line)

    fo.write("End of Layer2 log file scan \n")

if __name__ == "__main__":
    sys.exit(main())
