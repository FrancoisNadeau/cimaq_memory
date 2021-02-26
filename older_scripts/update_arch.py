#!/usr/bin/env python    

import zipfile

'''
Source: https://askubuntu.com/questions/267344/how-can-i-update-a-tar-gz-file
'''

def update_arch(filename):
	# First create the tar file. It has to be UNCOMPRESSED for -u to work
	tar -cvf my.tar some-directory/
	# ... update some files in some-directory
	# ... add files in some-directory
	# Now update only the changed and added files
	tar -uvf my.tar some-directory/
	# Compress if desired
	gzip my.tar

def main():
   update_arch(filename)

if __name__ == '__main__':
    main()
