#!/usr/bin/env python3
# coding: utf-8


import sys
import urllib.request
import socket
import socket
import struct
import os
import datetime
import getopt


class CNRoute:
    data_src = "https://ispip.clang.cn/all_cn.txt"
    cache_file = os.path.join(os.path.dirname(__file__) , "all_cn.txt")

    def __init__(self):
        pass

    def help(self):
        print("""
        -----------------------------------------
        CNRoute  by hefish

        -h   this message
        -u   update CN network list
        -a   add cn route
        -d   remove cn route
        """)
        sys.exit(0)


    def download_cache_file(self):
        f = urllib.request.urlopen(CNRoute.data_src)
        content = f.read().decode("utf-8")
        f.close()

        f = open(CNRoute.cache_file, "w")
        f.write(content)
        f.close()
            
        print("cnroute network list updated. ")
        return content

    def get_cn_ip(self):
        if not os.path.exists(CNRoute.cache_file):
            content = self.download_cache_file()
        else:
            st = os.stat(CNRoute.cache_file)
            if st.st_mtime + 7*86400 < datetime.datetime.now().timestamp():
                content = self.download_cache_file()
            else: 
                f = open(CNRoute.cache_file, "r")
                content = f.read()
                f.close()
        net_list = content.split("\n")
        return net_list
       
    
    def get_default_gateway(self):
        """Read the default gateway directly from /proc."""
        with open("/proc/net/route") as fh:
            for line in fh:
                fields = line.strip().split()
                if fields[1] != '00000000' or not int(fields[3], 16) & 2:
                    # If not default route or not RTF_GATEWAY, skip it
                    continue
                if fields[2] == '00000000':
                    continue
                if fields[7] != '00000000' :
                    continue

                return socket.inet_ntoa(struct.pack("<L", int(fields[2], 16)))
            return None

    def add_route(self, ip_list):
        default_gateway = self.get_default_gateway()
        if default_gateway == None:
            print("Cannot find default gateway, check the route table . ")
            return 

        for network in ip_list:
            if network.strip() != "":
                cmd = "ip ro add " + network + " via " + default_gateway
                print(cmd, end="\n")
                os.system(cmd)
    
    def del_route(self, ip_list):
        for network in ip_list:
            if network.strip() != "":
                cmd = "ip ro delete " + network 
                print(cmd, end="\n")
                os.system(cmd)

    def run(self):
        try :
            argv=sys.argv[1:]
            opts , args = getopt.getopt(argv, "adhu")
        except:
            self.help()
        
        for opt, arg in opts:
            if opt in ['-h']:
                self.help()
            if opt in ['-a']:
                net_list = self.get_cn_ip()
                self.add_route(net_list)
            elif opt in ['-d']:
                net_list = self.get_cn_ip()
                self.del_route()
            elif opt in ['-u']:
                self.download_cache_file()
            else:
                self.help()                


if __name__ == "__main__" :
    o = CNRoute()
    o.run()
