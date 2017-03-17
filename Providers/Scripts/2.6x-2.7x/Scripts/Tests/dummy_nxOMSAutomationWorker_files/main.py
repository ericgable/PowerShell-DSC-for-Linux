#!/usr/bin/env python2
# ====================================
# Copyright (c) Microsoft Corporation. All rights reserved.
# ====================================
import sys
import os
import configuration
import ConfigParser
import time

def exit_on_error(message, exit_code=1):
    print str(message)
    try:
        os.chdir(os.path.expanduser("~"))
        open("automation_worker_crash.log", "w").write(message)
    except:
        pass
    sys.exit(exit_code)

def main():
    if len(sys.argv) < 2:
        exit_on_error("Invalid configuration file path (absolute path is required).")
    configuration_path = sys.argv[1]

    if not os.path.isfile(configuration_path):
        exit_on_error("Invalid configuration file path (absolute path is required).")

    # configuration has to be read first thing
    try:
        # remove the test_mode env_var value (mainly for Windows)
        # this value is set in test
        del os.environ["test_mode"]
    except KeyError:
        pass
    worker_dir = os.path.dirname(os.path.realpath(__file__))
    config_path = os.path.join(worker_dir, configuration_path)
    configuration.read_and_set_configuration(config_path)
    configuration.set_config({configuration.COMPONENT: "worker"})
    # do not trace anything before this point

    # start a non terminating job
    while (True):
        time.sleep(60)


if __name__ == "__main__":
    main()
