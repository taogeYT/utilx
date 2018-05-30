from utilx.daemon import Daemon, run_daemon
import time

class TDaemon(Daemon):
    def run(self):
        while True:
            time.sleep(1)
            print("hello daemon")

def main():
    run_daemon(TDaemon("pid.pid"))

if __name__ == '__main__':
    main()
