Run `sudo ethtool -N ens2f1 flow-type udp4 dst-ip <server-ip> dst-port <port for moongen> action -1`
on the target machine (with the correct interface, ip and port (as specified in the moongen script on the client)) to drop all moongen packets in the NIC.
