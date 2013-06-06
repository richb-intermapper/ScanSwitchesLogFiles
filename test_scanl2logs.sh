# Shell script to run scanl2logs.py on each of the sample log files

python scanl2logs.py -i "CustomerInfo/RT118983/com.dartware.switches/switches.log.2013_05_23" -o CustomerInfo/Results/dd.csv

python scanl2logs.py -i "CustomerInfo/RT117599/166.77.200.105-8181-switches.log" -o CustomerInfo/Results/pq.csv

python scanl2logs.py -i "CustomerInfo/RT118153/192.168.100.26-8181-switches.log" -o CustomerInfo/Results/em.csv

python scanl2logs.py -i "CustomerInfo/RT119248/com.dartware.switches/switches.log" -o CustomerInfo/Results/al.csv

python scanl2logs.py -i "CustomerInfo/RT119535/127.0.0.1-8181-switches.log" -o CustomerInfo/Results/rb.csv

python scanl2logs.py -i "CustomerInfo/RT119439/127.0.0.1-8181-switches.log" -o CustomerInfo/Results/mvs.csv

python scanl2logs.py -i "CustomerInfo/RT119805/com.dartware.switches/switches.log" -o CustomerInfo/Results/Splunk.csv

python scanl2logs.py -i "CustomerInfo/RT119839/switches.log" -o CustomerInfo/Results/dg.csv
