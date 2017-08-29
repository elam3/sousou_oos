import sys
isVerbose = False
def main():
    ''' TODO '''
    global isVerbose
    if len(sys.argv) == 2 and (sys.argv[1] == 'v' or sys.argv[1] == '-v'):
        isVerbose = True
    if isVerbose:
        print('true')
    else:
        print('false')
    _print("hello world")

def _print(s):
    if isVerbose:
        print(s)

if __name__=='__main__': main()
