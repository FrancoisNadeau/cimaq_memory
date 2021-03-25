#!/bin/usr/python

def sizeof_fmt(num, suffix='B'):
    '''
    Return the size of the input in a humanly readable manner
    Source: https://stackoverflow.com/questions/1094841/get-human-readable-version-of-file-size
    '''
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

def main():
    if __name__ == __main__:
        sizeof_fmt(num, suffix='B')
