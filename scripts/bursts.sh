#!/bin/sh

if [ $# -ne 3 ]; then
	echo "Parameters: csv file name (without .csv), minimum inter-frame gap for burst (in ns), IP of the machine to look at (in hex)"
	exit 1
fi

# SOURCE is IP adress in hex
SOURCE=$3
IFG=$2
FILE=$1

TEMP="${FILE}_${SOURCE}_${IFG}.tmp"

if [ ! -f $TEMP ]; then
	sort -t, -nk6 "${FILE}.csv" | awk -M -v PREC=200 -v ifg=$IFG -v from_ip=$SOURCE 'BEGIN {
		NANOS = ifg * 0.000000001;
		# 10Gb/s bandwidth
		SECOND_PER_BYTE_W = 8/10000000000;
		# Preamble is 8 bytes
		PREAMBLE_W_LENGTH = 8 * SECOND_PER_BYTE_W;
		FS = ",";
		second = 0;
		burst = 0;
		burst_count = 0;
		prev_start = 0;
		prev_end = 0;
		prev_len = 0;
		burst_start = 0;
		burst_packet_sum = 0;
		burst_size = 0;

		second_to = 0;
		burst_to = 0;
		burst_count_to = 0;
		prev_start_to = 0;
		# prev_end = 0;
		prev_len_to = 0;
		burst_start_to = 0;
		burst_packet_sum_to = 0;
		burst_size_to = 0;
	}
	# Skip bad first line
	FNR == 1 { next; }
	# Match source and destination ip
	substr($7, 25, 4) == "0800" && substr($7, 53, 8) == from_ip {
		len = $3;
		s = $6 - PREAMBLE_W_LENGTH;
		# IFG after ethernet packets is 12 bytes
		e = s + ((len + 12) * SECOND_PER_BYTE_W);
		if (s - prev_end <= NANOS) {
			if (second == 1) {
				burst_count += 1;
				burst_start = prev_start;
				burst_size = 1;
				burst_packet_sum = prev_len + 20;
				# Wire length of packet is length + preamble (8 bytes) + IFG (12 bytes)
				# printf("%i %.15f %.15f %i\n", burst_count, prev_start, prev_end, prev_len+20);
			}
			burst = 1;
			second = 0;
			burst_size += 1;
			burst_packet_sum += len + 20;
			# printf("%i %.15f %.15f %i\n", burst_count, s, e, len+20);
		} else {
			# First non-burst after a burst
			if (burst == 1) {
				burst = 0;
				printf("%i,%i,%.15f,%.15f,%i\n", burst_count, burst_size, burst_start, prev_end, burst_packet_sum);
				burst_size = 0;
			}
			second = 1;
		}
		prev_start = s;
		prev_end = e;
		prev_len = len;
	}
	# Packets to the specified machine
	#substr($7, 25, 4) == "0800" && substr($7, 61, 8) == from_ip {
	#	len = $3;
	#	s = $6 - PREAMBLE_W_LENGTH;
	#	# IFG after ethernet packets is 12 bytes
	#	e = s + ((len + 12) * SECOND_PER_BYTE_W);
	#	if (s - prev_end_to <= NANOS) {
	#		if (second_to == 1) {
	#			burst_count_to += 1;
	#			burst_start_to = prev_start_to;
	#			burst_size_to = 1;
	#			burst_packet_sum_to = prev_len_to + 20;
	#			# Wire length of packet is length + preamble (8 bytes) + IFG (12 bytes)
	#			# printf("%i %.15f %.15f %i\n", burst_count, prev_start, prev_end, prev_len+20);
	#		}
	#		burst_to = 1;
	#		second_to = 0;
	#		burst_size_to += 1;
	#		burst_packet_sum_to += len + 20;
	#		# printf("%i %.15f %.15f %i\n", burst_count, s, e, len+20);
	#	} else {
	#		# First non-burst after a burst
	#		if (burst_to == 1) {
	#			burst_to = 0;
	#			printf("2 %i %i %.15f %i\n", burst_count_to, burst_size_to, prev_end_to - burst_start_to, burst_packet_sum_to);
	#			burst_size_to = 0;
	#		}
	#		second_to = 1;
	#	}
	#	prev_start_to = s;
	#	prev_end_to = e;
	#	prev_len_to = len;
	#}
	END {
		if (burst == 1) printf("%i,%i,%.15f,%.15f,%i\n", burst_count, burst_size, burst_start, prev_end, burst_packet_sum);
		#if (burst_to == 1) printf("2 %i %i %.15f %i\n", burst_count_to, burst_size_to, prev_end_to - burst_start_to, burst_packet_sum_to);
	}' > $TEMP
fi

