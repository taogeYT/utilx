# -*- coding: utf-8 -*-
"""
@time: 2020/4/14 2:42 下午
@desc:
"""
import fire
from utilx.deploy import Environment, set_env


class TestDeploy(Environment):

    @staticmethod
    @set_env(["dev"])
    def task1():
        while 1:
            import time
            time.sleep(10)
            print("task1 running...")

    @staticmethod
    def task2():
        while 1:
            import time
            time.sleep(10)
            print("task2 running...")


if __name__ == '__main__':
    fire.Fire(TestDeploy)
