## Parsing packets

The .expcap files are converted to csv format using exact-pcap-parse.c. This program is a slightly modified version of the one included in 
[exablaze's exact-capture](https://github.com/exablaze-oss/exact-capture/blob/master/tools/exact-pcap-parse.c). It reads the expcap file sequentially, and
outputs a csv file, where each line corresponds to a packet. The format of the file is as follows:

```
no. packet, caplen (length written to file), len (length of packet on the wire), dev_id, port_id, timestamp (seconds.pico seconds), data (default: first 68 bytes) 
```

Can be run by calling `exact-pcap-parse -i in.expcap -c out.csv -f expcap`.
