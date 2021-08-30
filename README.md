# Downtimer

A script that utilizes the locally installed ping command to measure duration of ping loss. 

## Example

```
$ ./downtimer.py -b -l /tmp/pinglog.txt pingo.example.com
 === Pinging pingo.example.com (192.168.1.99) every 1 second until you hit CTRL+C ===
 === Logging to /tmp/pinglog.txt ===
!!!!!!!!!!!!!!!!!!!!!!!!!!.... 00:00:07 !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!^C Exiting...
 === Total runtime was 00:04:00. Total downtime was 00:00:08. ===



$ cat /tmp/pinglog.txt
 === Starting pings to pingo.example.com every 1 second at 2021-07-10T15:20:42 ===
 - Ping loss to pingo.example.com started at 2021-07-10T15:24:03.
 + Ping loss to pingo.example.com ended at 2021-07-10T15:24:10 - 7 seconds elapsed.
 === Stopping at 2021-07-10T15:24:43 ===
 === Total runtime was 00:04:00. Total downtime was 00:00:08. ===
$
```
