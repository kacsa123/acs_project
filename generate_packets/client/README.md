To use unique-udp.lua, first install moongen on a computer with a NIC supporting DPDK, and follow the intructions at their [manual](https://github.com/emmericp/MoonGen).
Then unique-udp.lua can be run by calling `sudo ./build/MoonGen ./unique-udp.lua 0 1`, with additional options being
`-t`: time to run scripts for in seconds (default is 10s), `-r`: rate in Mbit/s (default is 10Gbit/s), and `-s`: size of packets (default is 60).
