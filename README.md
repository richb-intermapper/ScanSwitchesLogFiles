##ScanL2Logs.py

This program scans InterMapper Layer2 log files to give a view of what occurred. The 'switches.log' file contains information for each separate scan that the customer performs. This program creates an output file that shows:

* A history of relevant log file lines. These show the start and end of the scan, as well as notable event and error messages.

* An analysis of the Layer2 scan. The log file contains the results of every scan of the tables (below) from each device. The program displays the success or failure for each of the table scans, as well as a summary of the number of lines.
  * dot1d_Info
  * ifTable
  * ipAddrTable
  * dot1dBasePortTable_csi
  * dot1dstp_Info_csi
  * dot1dStpPortTable_csi
  * cdpCacheTable
  * lldpRemManAddrTable
  * lldpRemTable

The output file has the format shown below. Each scan lists interesting log lines, then the details of all the scanned tables.

```
 2013-06-01 19:02:15, Reading switches.log from: /home/dartware/Documents/SwitchesLogFiles/Customer ABC/127.0.0.1-8181-switches.log

Starting scan 1
 2013-05-28 11:29:09, Aborting previous action:, 3565, 43 of 44, [MainThread] CMD RECV: ABORT_POLL_REQUEST  source=127.0.0.1:3238 id=7 flags=4 length=0   (0)
 2013-05-28 11:29:23, Manually start poll:, 3576, 44 of 44, [MainThread] CMD RECV: POLL_NOW_REQUEST  source=127.0.0.1:3238 id=8 flags=4 length=0   (0)
 2013-05-28 11:29:23, Requesting poller list:, 3580, 44 of 44, [MainThread] KALI: <KC_export type='direct' name='devices.csv' id='3040'>#export format=csv table=devices fields=IMIDNameAddressMapIdStatusSnmpVersionIntSysServicesSysObjectIDSysDescrStatusLevelReason match=layer2 T</KC_export>
 2013-05-28 11:29:24, Scanning tables:, 3586, 44 of 44, [MainThread] KALI: Issuing <KC_opentable commands...
 2013-05-28 11:43:58, Scanning tables:, repeated 573 times, until 2013-05-28 11:30:48
 2013-05-28 11:43:58, Aborting previous action:, 66323, 42 of 44, [MainThread] CMD RECV: ABORT_POLL_REQUEST  source=127.0.0.1:3238 id=13 flags=4 length=0   (0)
, Error during scan:, , , Device 0.0.0.0 (zAzzzKzzzWd); table -:; KCID 3415; Never received matching 'KR';  see Table Info below.
, Error during scan:, , , Device 0.0.0.0 (zAzzzKzzzad); table -:; KCID 3416; Never received matching 'KR';  see Table Info below.

SNMP Tables for scan 1:
Start Time, End Time, Start Line, End Line, IMID, HexIP, KCid, TableID, IP, Label, SysSvc, TableName, Rows, Diag
 2013-05-23 14:20:10, 2013-05-23 14:20:10, 1614, 1645, zzzzzQzzzud, 0a000016, 7+, t27216a8+, 10.0.0.22, NPIF5E00D, Host (64), dot1d_Info, 0, 
 2013-05-23 14:20:10, 2013-05-23 14:20:10, 1615, 1649, zzzzzQzzzwd, 0a000018, 8+, t27215c8+, 10.0.0.24, dt151, Host (64), dot1d_Info, 0, 
 2013-05-23 14:20:10, 2013-05-23 14:20:10, 1616, 1631, zzzzzQzzz0d, 0a000019, 9+, t2721788+, 10.0.0.25, iR C4080, Host (72), dot1d_Info, 0, 
 2013-05-23 14:20:10, 2013-05-23 14:20:10, 1617, 1630, zzzzzQzzz2d, 0a00001b, 10+, t2721868+, 10.0.0.27, 10.0.0.27, Host (72), dot1d_Info, 0, 
 2013-05-23 14:20:10, 2013-05-23 14:20:10, 1618, 1632, zzzzzQzzzPd, 0a00001c, 11+, t2721a28+, 10.0.0.28, CANONA34BEE, 0, dot1d_Info, 0, 
 2013-05-23 14:20:10, 2013-05-23 14:20:10, 1619, 1644, zzzzzQzzzQd, 0a00001d, 12+, t2721948+, 10.0.0.29, CANONA36E6F, 0, dot1d_Info, 0, 
 2013-05-23 14:20:10, 2013-05-23 14:20:10, 1620, 1635, zzzzzQzzz4d, 0a00001e, 13+, t2721b08+, 10.0.0.30, ZBR3822532, L3 SwHub, dot1d_Info, 0, 
 2013-05-23 14:20:10, 2013-05-23 14:20:10, 1654, 1674, zzzzzQzzz4d, 0a00001e, 14+, t27215c8+, 10.0.0.30, ZBR3822532, L3 SwHub, ifTable, 1, 
 2013-05-23 14:20:10, 2013-05-23 14:20:10, 1663, 1689, zzzzzQzzzud, 0a000016, 15+, t27216a8+, 10.0.0.22, NPIF5E00D, Host (64), ifTable, 2, 
...
End of scan 1

Starting scan 2
... etc...
```

