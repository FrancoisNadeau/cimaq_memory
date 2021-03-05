#!/usr/bin/env python

def zipmeta(filename):
    with zipfile.ZipFile(filename, 'r') as archv:
        archv.printdir()
    archv.close()
    
def main():
    zipmeta(filename)

if __name__ == '__main__':
    main()
