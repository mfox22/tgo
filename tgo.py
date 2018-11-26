#!/usr/bin/env python

import os
import sys
import json
import argparse
import logging


def get_args():
    # Construct Arguments
    parser = argparse.ArgumentParser(description='tgo - tmux session tool')
    parser.add_argument('--session_file', '-s', required = False, help='The session description file')
    parser.add_argument('--user', '-u', required = False, default='mfox', help='The user for the session')
    parser.add_argument('--debug', action='store_true', help='Turn on debugging')
    args = parser.parse_args()
    return args

def process_json(session, user):
    first_time = 0
    windows_present = 0

    if os.system("tmux has-session -t %s" % (session)):
        json_data = json.load(open(session))
        os.system("tmux -2 new-session -d -s %s" % (session))
        os.system("tmux set-window-option -t %s -g automatic-rename off" % (session))
        if 'windows' in json_data:
            windows_present = 1
            windows = json_data['windows']
            for name in windows:
                node = windows[name]
                if first_time == 0:
                    os.system("tmux new-window  -t %s:1 -k -n '%s' 'ssh %s@%s'" % (session, name, user, node))
                    first_time = 1
                else:
                    first_time = first_time + 1
                    os.system("tmux new-window  -t %s:%s -n '%s' 'ssh %s@%s'" % (session, first_time, name, user, node))
        first_time = 0

        if 'local-windows' in json_data:
            json_data = json.load(open(session))
            windows_present = 1
            windows = json_data['local-windows']
            for name in windows:
                node = windows[name]
                if first_time == 0:
                    os.system("tmux new-window  -t %s:1 -k -n '%s' 'cd %s;bash'" % (session, name, node))
                    first_time = 1
                else:
                    first_time = first_time + 1
                    os.system("tmux new-window  -t %s:%s -n '%s' 'cd %s;bash'" % (session, first_time, name, node))
        first_time = 0


        if 'sync-panes' in json_data:
            panes = json_data['sync-panes']
            for name in panes:
                if name == 'name':
                    continue
                node = panes[name]

                if first_time == 0:
                    if windows_present:
                        os.system("tmux new-window -t %s -n '%s' 'ssh %s@%s'" % (session, panes['name'], user, node))
                    else:
                        os.system("tmux new-window -t %s:1 -k -n '%s' 'ssh %s@%s'" % (session, panes['name'], user, node))
                    first_time = 1
                else:
                    os.system("tmux split-window  -h 'ssh %s@%s'" % (user, node))
            os.system("tmux select-pane -t 0")
            os.system("tmux next-layout")
            os.system("tmux next-layout")
            os.system("tmux setw synchronize-panes on")

        os.system("tmux select-window -t %s:1" % (session))
        os.system("tmux -2 attach -t %s" % (session))
    else:
        os.system("tmux -2 attach -t %s" % (session))

def main():
    default_session_path = '/Users/mfox/Data/tgo-sessions/'

    if len(sys.argv) == 1:
        os.system("tmux ls")
        return 

    logger = logging.getLogger(__name__)

    args = get_args()
    if args.debug == True:
        logging.basicConfig(level=logging.DEBUG)

    args.session_file = default_session_path + args.session_file
    logging.debug("session file: %s", args.session_file)
    logging.debug("user: %s", args.user)

    process_json(args.session_file, args.user)


if __name__ == "__main__":
    main()

# vim: set et si ts=4 sw=4 ft=python:
