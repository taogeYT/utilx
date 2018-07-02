from utilx.daemon import Daemon, run_daemon
from utilx.deploy import Environment, Setup, setenv
import time

class TDaemon(Daemon):
    def run(self):
        while True:
            time.sleep(1)
            print("hello daemon")


class Tdeploy(Environment):

    @setenv(["dev", None])
    def f():
        print("ok")

    def f2():
        print("ok")


def main():
    # run_daemon(TDaemon("pid.pid"))
    t = Tdeploy()
    print(dir(t))
    print(Tdeploy._env, t._env)
    Setup(Tdeploy).export("test.ini")

if __name__ == '__main__':
    # import fire
    # fire.Fire(Tdeploy())
    main()
