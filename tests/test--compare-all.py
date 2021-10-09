#!/usr/bin/env python

import os, sys
import glob
import filecmp

import pyemf

is_py3 = sys.version_info[0] == 3
if is_py3:
    bchr = lambda x: bytes((x,))
else:
    bchr = chr


def dump(fh, length=8):
    """ "Return a hex dump of the file."""
    N = 0
    result = ""
    s = fh.read(length)
    while len(s) > 0:
        hexa = " ".join(["%02X" % ord(s[i : i + 1]) for i in range(len(s))])
        FILTER = b"".join([bchr(x) if 32 <= x < 127 else b"." for x in range(256)])
        s = s.translate(FILTER)
        result += "%04X   %-*s   %s\n" % (N, length * 3, hexa, s.decode("ascii"))
        N += length
        s = fh.read(length)
    return result


def dumpfile(filename):
    fh = open(filename, "rb")
    if fh:
        result = dump(fh)
        fh = open(filename + ".hex", "w")
        fh.write(result)


class Comparison:
    def __init__(self):
        self.verbose = False
        self.total = 0
        self.passed = []
        self.failed = []

    def show(self, char):
        sys.stdout.write(char)
        sys.stdout.flush()

    def compare(self, filename):
        self.total += 1
        outputfile = filename + ".out.emf"
        try:
            e = pyemf.EMF(verbose=self.verbose)
            e.load(filename)
            if os.path.exists(outputfile):
                os.remove(outputfile)
            ret = e.save(outputfile)
            if ret:
                if filecmp.cmp(filename, outputfile, shallow=False):
                    self.show(".")
                    self.passed.append(filename)
                else:
                    self.show("F")
                    self.failed.append(filename)
                    dumpfile(filename)
                    dumpfile(outputfile)
            else:
                self.failed.append(filename)
                self.show("0")
        except Exception as e:
            print(e)
            self.failed.append(filename)
            self.show("E")
            if os.path.exists(outputfile):
                dumpfile(filename)
                dumpfile(outputfile)

    def stats(self):
        print()
        print("%d passed out of %d" % (len(self.passed), self.total))
        print("passed: %s" % self.passed)
        print("failed: %s" % self.failed)


comp = Comparison()
tests = glob.glob("test-[a-z0-9]*.py")
tests.sort()
for filename in tests:
    print("Running %s" % filename)
    filename = filename[:-3] + ".emf"
    comp.compare(filename)

# check some other (non-redistributable, unfortunately) tests
tests = [
    "mapping1.emf",
    "mapping2.emf",
    "example1.emf",
    "clip-art-computer.emf",
    "features.emf",
]
for filename in tests:
    if os.path.exists(filename):
        comp.compare(filename)

comp.stats()
