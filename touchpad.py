#!/usr/bin/python3
'''
This is a simple script to enable/disable/toggle the touchpad. For those of us
who got stuck w/ a sentilic touchpad or similar.

Parses xinput output, so it should work w/ just the touchpad's name.

@note
Uses xinput (of the xorg variety), which should be installed on most/all linux operating systems by default. 

@note
Done in python b/c my bash script was starting to get complicated, and I like python more.


@author Matthew Todd
@date Oct 22, 2011
'''

import argparse
import re
import subprocess
import sys


DEFAULT_TOUCHPAD_NAME = 'Sentelic'
EXIT_FAILURE = 1


def get_device_id(touchpad_name):
    '''
    calls xinput --list and searches results to get the touchpad's id.

    @return the id as a string
    '''
    try:
        output = subprocess.check_output(['xinput', '--list'])
        output = output.decode()

        for line in output.splitlines():
            if touchpad_name in line:
                match = re.search('id=([0-9]+)', line)
                str_id = match.group(1)
                return str_id

        print("Failed to find the touchpad: %r" % touchpad_name)
        sys.exit(EXIT_FAILURE)

    except Exception as e:
        print("Failed to get touchpad id: %s" % e)
        sys.exit(EXIT_FAILURE)


def get_enabled_property_id(touchpad_id):
    '''
    calls xinput --list-props <id> to determine the id of the enabled property.

    Also determines if its currently enabled or not.

    @note
    B/c of the regex expression, this function is tied to xinput's output format, to some degree or another.

    @return (id, currently_enabled) where id is a (string, number) and currently_enabled is a boolean
    '''
    try:
        output = subprocess.check_output(['xinput', '--list-props', touchpad_id])
        output = output.decode()

        for line in output.splitlines():
            if 'Device Enabled' in line:
                line = line.strip()
                match = re.search('\(([0-9]+)\):\s([0,1])', line)
                return (match.group(1), match.group(2) == '1')

    except Exception as e:
        print("Failed to get enabled information: %s" % e)
        sys.exit(EXIT_FAILURE)


def set_enabled(touchpad_id, enabled_id, enabled):
    '''
    Sets whether the touchpad is enabled or not.

    @param touchpad_id the id of the touchpad
    @param enabled_id the id of the enabled property
    @param enabled boolean whether to enable(True) or disable(False)
    '''
    if enabled:
        value = '1'
    else:
        value = '0'

    try:
        subprocess.check_call(['xinput', '--set-prop', touchpad_id, enabled_id, value])
    except Exception as e:
        print("Failed to enable/disable touchpad: %s" % e)
        sys.exit(EXIT_FAILURE)


def main():
    '''
    '''
    # program arguments
    parser = argparse.ArgumentParser(description='enable/disable/toggle touchpad')
    parser.add_argument('action', choices=['on', 'off', 'toggle'], help='what action to take')
    parser.add_argument('--name', '-n', dest='touchpad_name', default=DEFAULT_TOUCHPAD_NAME,
                        help='the name of the touchpad device (default: %s)' % DEFAULT_TOUCHPAD_NAME)
   
    args = parser.parse_args() 

    touchpad_name = args.touchpad_name
    touchpad_id = get_device_id(touchpad_name)
    enabled_id, enabled = get_enabled_property_id(touchpad_id)

    action = args.action
    if action == 'on':
        set_enabled(touchpad_id, enabled_id, True)
    elif action == 'off':
        set_enabled(touchpad_id, enabled_id, False)
    elif action == 'toggle':
        set_enabled(touchpad_id, enabled_id, not enabled)
    else:
        print("Error: invalid action: %s" % action)
        return

if __name__ == '__main__':
    main()
