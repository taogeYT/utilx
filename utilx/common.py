# encoding: utf-8
"""
@time: 2019/7/5/005 17:11
@desc:
"""


class Dict(dict):

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value



def main():
    Dict({"a": 1}).b()


if __name__ == '__main__':
    main()