import argparse
import re
import os
import shutil

def main():
    parser = argparse.ArgumentParser(description="This is a batch renamer",
                                     usage="To replace all files with hello "
                                           "with goodbye instead: python cliRenamer.py hello goodbye")
    parser.add_argument('inString', help="The word to replace")
    parser.add_argument('outString', help="The word to replace it with")
    parser.add_argument('-d', '--duplicate', help="Whether to duplicate or replace in spot", action="store_true")
    parser.add_argument('-r', '--regex', help="whether the patterns are regex or not", action="store_true")
    parser.add_argument('-o','--out', help="The output location. Defaults to here")

    args = parser.parse_args()
    rename(args.inString, args.outString, duplicate=args.duplicate, outDirectory=args.out, regex=False)

def rename(inString, outString, duplicate=True, inDirectory=None, outDirectory=None, regex=False):
    if not inDirectory:
        inDirectory = os.getcwd()

    if not outDirectory:
        outDirectory = inDirectory

    outDirectory = os.path.abspath(outDirectory)

    if not os.path.exists(outDirectory):
        raise IOError("%s does not exist" % outDirectory)
    if not os.path.exists(inDirectory):
        raise IOError("%s does not exist" % inDirectory)

    for f in os.listdir(inDirectory):
        if f.startswith('.'):
            continue

        if regex:
            name = re.sub(inString, outString, f)
        else:
            name = f.replace(inString, outString)

        if name == f:
            continue
        src = os.path.join(inDirectory, f)
        dest = os.path.join(outDirectory, name)
        if duplicate:
            shutil.copy2(src, dest)
        else:
            os.rename(src, dest)

    print(outDirectory)

if __name__ == '__main__':
    main()
