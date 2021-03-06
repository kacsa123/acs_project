/*
 * Copyright (c) 2017, 2018 All rights reserved.
 * See LICENSE.txt for full details.
 *
 *  Created:     28 Jul 2017
 *  Author:      Matthew P. Grosvenor
 *  Description: A tool for parsing pcaps and expcaps and outputting in ASCII
 *               for debugging and inspection.
 *
 */


#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <ctype.h>
#include <signal.h>
#include <errno.h>

#include <chaste/types/types.h>
#include <chaste/data_structs/vector/vector_std.h>
#include <chaste/options/options.h>
#include <chaste/log/log.h>

#include "data_structs/pthread_vec.h"
#include "data_structs/eiostream_vec.h"
#include "data_structs/pcap-structures.h"

#include "data_structs/expcap.h"


USE_CH_LOGGER_DEFAULT;
USE_CH_OPTIONS;

#define CHUNK_SIZE 4096

char fmtd[CHUNK_SIZE + 68] = {0};

int n = 0;


struct {
    char*  input;
    char* csv;
    bool verbose;
    char* format;
    ch_word offset;
    ch_word max;
    ch_word num;
} options;


static volatile bool stop = false;
void signal_handler(int signum)
{
    ch_log_warn("Caught signal %li, shutting down\n", signum);
    if(stop == 1){
        ch_log_fatal("Hard exit\n");
    }
    stop = 1;
}


int read_expect(int fd, void* buff, ssize_t len, int64_t* offset, FILE* csv_fd)
{

    ssize_t total_bytes = 0;

    do{
        ch_log_debug1("Trying to read %liB\n", len);
        ssize_t bytes = read(fd, (char*)buff + total_bytes, len - total_bytes);
        if(bytes == 0){
            ch_log_error("Reached end of file\n");
            if (csv_fd) {
            	fwrite(fmtd, n, 1, csv_fd);
	        n=0;
	    }
            return 1;
        }
        total_bytes += bytes;

    }
    while(total_bytes < len);

    *offset += total_bytes;

    return 0;
}

inline void my_putchar(char c, FILE* f) {
    fmtd[n++] = c;
    // Is the buffer full?
    if (n >= CHUNK_SIZE) {
        fwrite(fmtd, n, 1, f);
        n = 0;
    }
}

inline void my_puthex(uint8_t c, FILE* f) {
    char hex[2];
    
    char temp = c % 16;
    if( temp < 10) temp = temp + 48;
    else temp = temp + 87;
    hex[1]= temp;
    c = c / 16;

    temp = c % 16;
    if( temp < 10) temp = temp + 48;
    else temp = temp + 87;
    hex[0]= temp;

    fmtd[n++] = hex[0];
    fmtd[n++] = hex[1];
    // Is the buffer full?
    if (n >= CHUNK_SIZE) {
        fwrite(fmtd, n, 1, f);
        n = 0;
    }
}

void my_add_float(int64_t nb, int* count, char* temp) {
        if (nb <= 9) {
                //ch_log_error("write to %i", 12-(*count));
                int i = 11 - (*count);
        	temp[i] = (nb + 48);
        }
        else {
                my_add_float(nb % 10, count, temp);
                (*count)++;
                my_add_float(nb / 10, count, temp);
        }
}

void my_put_float(int64_t nb, FILE* f) {
	char temp[12];
        for (int i = 0; i<12; i++) {
        	temp[i] = '0';
        }
        //ch_log_error("init temp");
        int count = 0;
        my_add_float(nb, &count, temp);
        for (int i = 0; i<12; i++) {
                //ch_log_error("write temp %i", i);
                my_putchar(temp[i], f);
        }
}

void my_put_nbr(int64_t nb, FILE* f) {
	if (nb < 0) {
    		my_putchar('-', f);
    		nb = -nb;
	}
	if (nb <= 9) my_putchar(nb + 48, f);
	else {
    		my_put_nbr(nb / 10, f);
    		my_put_nbr(nb % 10, f);
        }
}

void dprint_packet(/*int fd*/FILE* f, bool expcap, pcap_pkthdr_t* pkt_hdr, char* packet,
                  bool nl, bool content, int total_out, int64_t timedelta_ns)
{
    //char fmtd[4096] = {0};
   //ch_log_error("what");
    //int n = 0;
   expcap_pktftr_t* pkt_ftr = (expcap_pktftr_t*)((char*)(packet)
                + pkt_hdr->caplen - sizeof(expcap_pktftr_t));
   my_put_nbr(total_out, f);
   my_putchar(',', f);
   my_put_nbr(pkt_hdr->caplen, f);
   my_putchar(',', f);
   my_put_nbr(pkt_hdr->len, f);
   my_putchar(',', f);
   my_put_nbr(pkt_ftr->dev_id, f);
   my_putchar(',', f);
   my_put_nbr(pkt_ftr->port_id, f);
   my_putchar(',', f);
   my_put_nbr((int64_t)pkt_ftr->ts_secs, f);
   my_putchar('.', f);
   my_put_float((int64_t)pkt_ftr->ts_psecs, f);
   my_putchar(',', f);


   /*n += sprintf(&fmtd[n], "%04i,%i,%i,",
            total_out, pkt_hdr->caplen, pkt_hdr->len);
   if (n >= CHUNK_SIZE) {
        fwrite(fmtd, n, 1, f);
        n = 0;
   }*/
    
   /*if(expcap && packet) {
        expcap_pktftr_t* pkt_ftr = (expcap_pktftr_t*)((char*)(packet)
                + pkt_hdr->caplen - sizeof(expcap_pktftr_t));

        n += sprintf(&fmtd[n], "%i,%i,%li.%012li,",
                pkt_ftr->dev_id,
                pkt_ftr->port_id,
                (int64_t)pkt_ftr->ts_secs, (int64_t)pkt_ftr->ts_psecs);
    }*/
    
    /*if (n >= CHUNK_SIZE) {
        fwrite(fmtd, n, 1, f);
        n = 0;
    }*/

    if(content && options.num != 0){

        if(options.num < 0){
            options.num = INT64_MAX;
        }

        for(int64_t i = 0; i < MIN((int64_t)pkt_hdr->caplen,options.num); i++){
            my_puthex(*((uint8_t*)packet +i), f);
            //n += sprintf(&fmtd[n], "%02x", *((uint8_t*)packet +i));
        }
        if (n >= CHUNK_SIZE) {
            fwrite(fmtd, n, 1, f);
            n = 0;
        }
    }

    /* dprintf(fd, "%04i,%lins,%i.%09i,%i,%i,",
            total_out, timedelta_ns,
            pkt_hdr->ts.ns.ts_sec, pkt_hdr->ts.ns.ts_nsec,
            pkt_hdr->caplen, pkt_hdr->len); */
    /*fprintf(f, "%04i,%i,%i,",
            total_out, pkt_hdr->caplen, pkt_hdr->len);*/


    /*if(expcap && packet){
        expcap_pktftr_t* pkt_ftr = (expcap_pktftr_t*)((char*)(packet)
                + pkt_hdr->caplen - sizeof(expcap_pktftr_t));

        fprintf(f, "%04i,%i,%i,%i,%i,%li.%012li,",
                total_out, pkt_hdr->caplen, pkt_hdr->len,
                pkt_ftr->dev_id,
                pkt_ftr->port_id,
                (int64_t)pkt_ftr->ts_secs, (int64_t)pkt_ftr->ts_psecs);
    }*/
    
    /* fprintf(f, "%s",fmtd); */
    
    if(nl){
        fmtd[n++] = '\n';
        //n += fprintf(f, "\n");
    }
    if (n >= CHUNK_SIZE) {
        fwrite(fmtd, n, 1, f);
        n = 0;
    }
    //fwrite(fmtd, n, 1, f);
}



int read_packet(int fd, int64_t* offset, int64_t snaplen, pcap_pkthdr_t* pkt_hdr, char* pbuf, FILE* csv_fd )
{

    if(read_expect(fd, pkt_hdr, sizeof(pcap_pkthdr_t), offset, csv_fd)){
        return 1;
        //ch_log_fatal("Could not read enough bytes from %s at offset %li, (%li required)\n", options.input, offset, sizeof(pkt_hdr));
    }

    bool error = false;
    snaplen = 4096;
    if(pkt_hdr->caplen > snaplen){
        ch_log_error("Error, packet length out of range [0,%li] %u at offset=%li\n", snaplen, pkt_hdr->len, offset);
        error = true;
    }

    if(options.verbose && (pkt_hdr->len == 0 || pkt_hdr->len + sizeof(expcap_pktftr_t) < pkt_hdr->caplen)){
        ch_log_warn("Warning: packet len %li < capture len %li\n", pkt_hdr->len, pkt_hdr->caplen);
    }


    if(error){
        read_expect(fd, pbuf, 4096, offset, csv_fd);
        hexdump(&pkt_hdr, sizeof(pkt_hdr));
        hexdump(pbuf, 4096);
        exit(0);

    }

    if(read_expect(fd, pbuf, pkt_hdr->caplen, offset, csv_fd)){
        return 1;
    }

    return 0;

}


bool check_udp_tcp(char* fmtd)
{
  //printf("len: %d", len);
  //if (len < 68) return false;

  //printf("%.2s\n", &(fmtd[46]));

  // check if TCP packet
  if (strncmp(&(fmtd[46]), "06", strlen ("06")) == 0) return true;
  // check if UDP packet
  if (strncmp(&(fmtd[46]), "11", strlen ("06")) == 0) return true;
  return false;
}



int main(int argc, char** argv)
{
    ch_word result = -1;
    int64_t offset = 0;

    signal(SIGHUP, signal_handler);
    signal(SIGINT, signal_handler);
    signal(SIGPIPE, signal_handler);
    signal(SIGALRM, signal_handler);
    signal(SIGTERM, signal_handler);

    ch_opt_addsu(CH_OPTION_REQUIRED,'i',"input","PCAP file to read", &options.input);
    ch_opt_addsi(CH_OPTION_OPTIONAL,'c',"csv","CSV output file to write to ", &options.csv, NULL);
    ch_opt_addbi(CH_OPTION_FLAG,'v',"verbose","Printout verbose output", &options.verbose, false);
    ch_opt_addsu(CH_OPTION_REQUIRED,'f',"format","Input format [pcap | expcap]", &options.format);
    ch_opt_addii(CH_OPTION_OPTIONAL,'o',"offset","Offset into the file to start ", &options.offset, 0);
    ch_opt_addii(CH_OPTION_OPTIONAL,'m',"max","Max packets to output (<0 means all)", &options.max, -1);
    ch_opt_addii(CH_OPTION_OPTIONAL,'n',"num-chars","Number of characters to output (<=0 means all)", &options.num, 68);

    ch_opt_parse(argc,argv);
    FILE* csv_fd = NULL;

    if(!options.verbose && !options.csv){
        ch_log_fatal("Must choose an output type. Use either --verbose or --csv\n");
    }

    bool expcap = false;
    if(strncmp(options.format, "pcap", strlen("pcap")) == 0){
        expcap = false;
    }
    else if(strncmp(options.format, "expcap", strlen("expcap")) == 0){
        expcap = true;
    }
    else{
        ch_log_fatal("Unknown format type =\"%s\". Must be \"pcap\" or \"expcap\"\n", options.format);
    }

    if(options.max < 0){
        options.max = INT64_MAX;
    }

    ch_log_info("Starting PCAP parser...\n");

    int fd = open(options.input,O_RDONLY);
    if(fd < 0){
        ch_log_fatal("Could not open PCAP %s (%s)\n", options.input, strerror(errno));
    }

    pcap_file_header_t fhdr;
    if(read_expect(fd, &fhdr, sizeof(fhdr), &offset, csv_fd)){
        ch_log_fatal("Could not read enough bytes from %s at offset %li, (%li required)\n", options.input, offset, sizeof(pcap_file_header_t));
    }

    char* magic_str = fhdr.magic == NSEC_TCPDUMP_MAGIC ? "Nansec TCP Dump" :  "UNKNOWN";
    magic_str = fhdr.magic == TCPDUMP_MAGIC ? "TCP Dump" :  magic_str;
    if(options.verbose){
        printf("Magic    0x%08x (%i) (%s)\n", fhdr.magic, fhdr.magic, magic_str);
        printf("Ver Maj  0x%04x     (%i)\n", fhdr.version_major, fhdr.version_major);
        printf("Ver Min  0x%04x     (%i)\n", fhdr.version_minor, fhdr.version_minor);
        printf("Thiszone 0x%08x (%i)\n", fhdr.thiszone, fhdr.thiszone);
        printf("SigFigs  0x%08x (%i)\n", fhdr.sigfigs, fhdr.sigfigs);
        printf("Snap Len 0x%08x (%i)\n", fhdr.snaplen, fhdr.snaplen);
        printf("Link typ 0x%08x (%i)\n", fhdr.linktype, fhdr.linktype);
    }

    pcap_pkthdr_t pkt_hdr;
    char pbuf[1024 * 64] = {0};
    if(read_packet(fd, &offset, fhdr.snaplen, &pkt_hdr, pbuf, csv_fd)){
        exit(0);
    }

    if(options.csv){
        csv_fd = fopen(options.csv, "w");
	// csv_fd = open(options.csv,O_WRONLY | O_CREAT | O_TRUNC, 0666);
        if(csv_fd == NULL){
            ch_log_fatal("Could not open in missed file %s (%s)\n", options.csv, strerror(errno));
        }
        fprintf(csv_fd, "count,timedelta_ns,sec.ns,caplen,len,dev_id,port_id,sec.ps,data\n");
        /*if(expcap){
            fprintf(csv_fd,"cap port,seconds.picos,");
        }
        fprintf(csv_fd,"seconds.nanos,length,payload\n");*/

    }

    int64_t timenowns = 0;
    int64_t timeprevns = 0;
    int64_t total_out = 0;
    for(int pkt_num = 0; !stop && pkt_num < options.offset + options.max; pkt_num++,
    timeprevns = timenowns ){
        if(pkt_num && pkt_num % (1000 * 1000) == 0){
            ch_log_info("Loaded %li,000,000 packets\n", pkt_num/1000/1000);
        }


        if(read_packet(fd, &offset, fhdr.snaplen, &pkt_hdr, pbuf, csv_fd)){
            break;
        }
        timenowns = pkt_hdr.ts.ns.ts_sec * 1000ULL * 1000 * 1000 + pkt_hdr.ts.ns.ts_nsec;

        if(timeprevns == 0){
            timeprevns = timenowns;
        }

        const int64_t time_delta = timenowns - timeprevns;


        if(pkt_num < options.offset){
            continue;
        }


        if(options.verbose){
            dprint_packet(stdout, expcap, &pkt_hdr, pbuf, true, true, total_out, time_delta );
        }
        
        
        if(csv_fd > 0 /*&& check_udp_tcp(payload_start)*/){
            dprint_packet(csv_fd, expcap, &pkt_hdr, pbuf, true, true, total_out, time_delta);
        }
            

        total_out++;


    }

    if(csv_fd) { 
        fwrite(fmtd, n, 1, csv_fd);
        n = 0;
    }


    close(fd);
    if(csv_fd) fclose(csv_fd);

    ch_log_info("Output %li packets\n", total_out);
    ch_log_info("PCAP parser, finished\n");
    return result;

}
