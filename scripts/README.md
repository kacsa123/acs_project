# flow_sizes.py
Run on csv file generated by exact-pcap-parse:
```
python flow_sizes.py --file "input csv file" --out "output csv file"
```
If packets were not in order in the original expcap, sort the input csv first, e.g. by
```
sort -t, -nk6 "input" > output
```

Returns a csv file with all TCP flows, their start and end times and sizes

# bursts.sh

Creates csv file with list of bursts for packets from the given machine. Includes burst sizes and start and end times.
A burst is a set of of packets, where all packets had inter-packet gaps of less than x ns, where x is given as a parameter to the script
