#!/usr/bin/env python2
#
# Copyright (C) Microsoft Corporation, All rights reserved.

import os
import subprocess
import sys

# workaround when unexpected environment variables are present
# sets COLUMNS wide enough so that output of ps does not get truncated
if 'COLUMNS' in os.environ:
    os.environ['COLUMNS'] = "3000"

# pwd will not be present on windows
# not using if clause in case some os other than posix has support for pwd
try:
    import pwd
except:
    pass

PS_FJH_HEADER = ["UID", "PID", "PPID", "PGID", "SID", "C", "STIME", "TTY", "TIME", "CMD"]


def posix_only(func):
    """Decorator to prevent linux specific methods to run on other OS."""
    if os.name.lower() != "posix":
        print func.__name__ + " isn't supported on " + str(os.name) + " os."
        return bypass
    else:
        return func


def bypass():
    pass


def format_process_entries_to_list(process_list):
    """Formats a list of raw list of string to process model objects.

    Example input :
            ["UID        PID  PPID  PGID   SID  C STIME TTY          TIME CMD",
             "oaastest 22448 22445 22448 22448  0 Mar08 pts/0    00:00:03 bash",
             "oaastest  2509 22448  2509 22448  0 06:14 pts/0    00:00:00 ps -fjH"]

    Returns:
        A list of ProcessModel objects.

    Note : The header row will be discarded.
    """
    formatted_entries = []
    for entry in process_list:
        sanitized_entry = filter(None, entry.split(" "))
        if len(sanitized_entry) < 1 or sanitized_entry == PS_FJH_HEADER:
            continue
        process = ProcessModel(sanitized_entry)
        formatted_entries.append(process)
    return formatted_entries


@posix_only
def get_current_username():
    """Returns the username owning the current process.

    Returns:
        string, representing the username (i.e myusername)
    """
    user_id = os.getuid()
    return pwd.getpwuid(user_id).pw_name


@posix_only
def get_current_user_processes():
    """Gets the list of process of the current user.

    Returns:
        A list of ProcessModel objects.
    """
    current_username = get_current_username()
    proc = subprocess.Popen(["ps", "-fjH", "-u", current_username], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = proc.communicate()
    if proc.poll() != 0:
        raise Exception("Unable to get processes : " + str(error))
    formatted_entries = format_process_entries_to_list(output.split("\n"))
    return formatted_entries


@posix_only
def kill_current_user_process(pid):
    """Kills the process specified by the pid argument.

    Note:
        The specified pid has to be own by the same user owning the current process.
    """
    subprocess.call(["kill", "-9", str(pid)])


@posix_only
def fork_and_exit_parent():
    """Forks and kills the parent process."""
    try:
        pid = os.fork()
        if pid > 0:
            print "parent process " + str(os.getpid()) + " exiting"
            sys.exit(0)
    except OSError, e:
        print "fork failed. " + str(e.message)
        sys.exit(1)


@posix_only
def daemonize():
    """Daemonize the current process by double forking and closing all file descriptors

    Note:
        One of the fork fails, the process will exit
    """
    # fork first child and exist parent
    fork_and_exit_parent()

    # decouple from parent environment
    os.setsid()
    os.close(sys.stdin.fileno())
    os.close(sys.stdout.fileno())
    os.close(sys.stderr.fileno())

    # fork second child and exist parent
    fork_and_exit_parent()


class ProcessModel:
    def __init__(self, process_info):
        """FORMAT : ['UID', 'PID', 'PPID', 'PGID', 'SID', 'C', 'STIME', 'TTY', 'TIME', 'CMD']"""
        self.uid = process_info[0]
        self.pid = int(process_info[1])
        self.ppid = int(process_info[2])
        self.pgid = int(process_info[3])
        self.sid = int(process_info[4])
        self.c = process_info[5]
        self.stime = process_info[6]
        self.tty = process_info[7]
        self.time = process_info[8]
        self.cmd = " ".join(process_info[9:])

    def __str__(self):
        return " ".join([self.uid,
                         self.pid,
                         self.ppid,
                         self.pgid,
                         self.sid,
                         self.c,
                         self.stime,
                         self.tty,
                         self.time,
                         self.cmd])
