from parser import Parser

def main():
    f = open('../data/inputs/landerFuncs.oln.py')
    lines = f.readlines()

    parser = Parser()
    for l in lines:
        parser.parse(l)

    parser.signal_EOF()

if __name__ == '__main__':
    main()