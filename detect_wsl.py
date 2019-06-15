#!/usr/bin/env python

import os

def is_running_win():
	if os.name in ['nt']:
		return True
	return False

def is_running_wsl():
	if is_running_win():
		return False
	if os.name in ['posix']:
		if 'microsoft' in os.uname().release.lower():
			return True
		if 'microsoft' in os.uname().version.lower():
			return True
	return False
