import sys,os,subprocess



def create(comDevice,server):
    print(f"socat.create() pipe {comDevice} <-> {server}")
    socat_cmd = f"socat pty,link={comDevice},group-late=dialout,mode=660  tcp:{server} &"

    try:
        retcode = subprocess.call(socat_cmd, shell=True)
        if retcode < 0:
            print("Child was terminated by signal", -retcode, file=sys.stderr)
        else:
            print("Child returned", retcode, file=sys.stderr)
    except OSError as e:
        print("Execution failed:", e, file=sys.stderr)


def main():
    comDevice = os.path.expanduser("~/.local/dev/ttyMount")
    server = "moxa1:4004"

    create(comDevice,server)

if __name__ == "__main__":
    main()	


