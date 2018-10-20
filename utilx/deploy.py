"""
设startsecs=1, startretries=3（都是默认值），如果有一程序有这些行为：

a) 启动即退出，exit code为0, 那么supervisor会在重试3试后停止重试，进程状态为FATAL。
b) 启动即退出，exit code为1, 那么supervisor会在重试3试后停止重试，进程状态为FATAL。
c) 启动3秒后退出，exit code为1, 那么supervisor会无限重启程序，无视startretries。
d) 启动3秒后退出，exit code为0, 那么supervisor不会重启，进程状态为EXIT。
"""
__all__ = ["Setup", "setenv", "Environment"]
import sys
import os
import importlib
import getpass
import inspect
from functools import partial
# from collections import defaultdict

_conf = """
[program:{project}_{name}]

command     = {command}
directory   = {home}
user        = {user}
autorestart = {autorestart}
startsecs   = {startsecs}
{envconfig}
redirect_stderr         = true
stdout_logfile_maxbytes = 10MB
stdout_logfile_backups  = 5
stdout_logfile          = {logfile}
"""

class Setup(object):
    """
    example:
        commands = [("celery", "/usr/local/anaconda3/bin/celery worker -l INFO -A webapp.api.celery")]
        class T:
            def f(self):
                pass
        Setup(T, commands).export()
    """
    config = {"autorestart": True, "startsecs": 3}

    def __init__(self, cls_name, commands=[], config={}, env_name="PYENV"):
        self.config.update(config)
        # module_name, class_name = os.path.splitext(cls_name)
        # self.cls = getattr(importlib.import_module(module_name), class_name.strip("."))
        self.cls = cls_name
        self._commands = commands
        file_path = self.cls.__module__
        self.python = os.path.join(sys.prefix, "bin", "python")
        self.home = os.path.dirname(os.path.abspath(file_path))
        self.project = os.path.basename(self.home)
        self._env_name = env_name
        self.env = os.getenv(env_name)
        python = os.path.join(sys.prefix, "bin")
        path = f'{python}:%(ENV_PATH)s'
        # "/usr/local/anaconda3/bin:%(ENV_PATH)s"
        # "environment=PYTHONPATH=/opt/mypypath:%(ENV_PYTHONPATH)s,PATH=/opt/mypath:%(ENV_PATH)s"
        if self.env:
            self.envconfig = f'environment=PATH={path},{env_name}={self.env}'
        else:
            self.envconfig = f"environment=PATH={path}"

        self.config["home"] = self.home
        self.config["user"] = getpass.getuser()
        self.config["project"] = self.project
        self.config["envconfig"] = self.envconfig

    def _get_script_names(self):
        # methods = dict(inspect.getmembers(self.cls(), inspect.ismethod))
        # funcs = dict(inspect.getmembers(self.cls(), inspect.isfunction))
        # names = [name for name in (*methods.keys(), *funcs.keys()) if not name.startswith("_")]
        except_names = [name for name in self.cls._env.keys() if self.env not in self.cls._env[name]]
        # print(except_names)
        names = [name for name in dir(self.cls) if name not in except_names and not name.startswith("_")]
        return names

    def _gen_scripts_conf(self):
        configs = []
        for name in self._get_script_names():
            logfile = os.path.join(self.home, "logs", f"{name}.log")
            script = os.path.abspath(sys.modules[self.cls.__module__].__file__)
            # script = "{self.home}/run.py"
            command = f"{self.python} -u {script} {name}"
            configs.append(_conf.format(command=command, name=name, logfile=logfile, **self.config))
        return configs

    def _gen_cmd_conf(self):
        configs = []
        for name, command in self._commands:
            logfile = os.path.join(self.home, "logs", f"{name}.log")
            configs.append(_conf.format(command=command, name=name, logfile=logfile, **self.config))
        return configs

    def gen_config(self):
        script_config = self._gen_scripts_conf()
        cmd_config = self._gen_cmd_conf()
        content = "".join([*script_config, *cmd_config])
        print(content)
        return content

    # def export(self, file=None):
    #     """
    #     supervisor配置导出
    #     file 默认路径 /etc/supervisord.d/
    #     """
    #     if file is None:
    #         _file = f"{self.project}.ini"
    #     else:
    #         _file = file
    #     if self.env == "stop":
    #         config_content = ""
    #     else:
    #         config_content = self.gen_config()
    #     self.update_conf_file(config_content, _file)
    #     if file is None:
    #         log_dir = os.path.join(self.home, "logs")
    #         os.makedirs(log_dir) if not os.path.exists(log_dir) else None
    #         os.system(f"sudo mv {_file} /etc/supervisord.d/")
    #         os.system("sudo supervisorctl update")
    #     if config_content:
    #         if self.env is None:
    #             print(f"WARN: 环境变量'{self._env_name}'未配置")
    #         else:
    #             print(f"success, 当前环境: {self._env_name}={self.env}")
    #     else:
    #         if self.env == "stop":
    #             print("已停止所有supervisor任务")
    #         else:
    #             print("未找到可用配置")

    def update_conf_file(self, content, file_path):
        with open(file_path, "w") as f:
            f.write(content)

    def export(self):
        """
        supervisor配置导出
        file 默认路径 /etc/supervisord.d/
        """
        import fire
        fire.Fire(self._export)

    def _export(self, cmd, file=None):
        """
        参数说明
        --cmd: [start|stop]
        --file: 导出文件
        """
        if file is None:
            _file = f"{self.project}.ini"
        else:
            _file = file

        if cmd == "stop":
            config_content = ""
        else:
            config_content = self.gen_config()

        self.update_conf_file(config_content, _file)
        if file is None:
            log_dir = os.path.join(self.home, "logs")
            os.makedirs(log_dir) if not os.path.exists(log_dir) else None
            os.system(f"sudo mv {_file} /etc/supervisord.d/")
            os.system("sudo supervisorctl update")

        if config_content:
            if self.env is None:
                print(f"WARN: 环境变量'{self._env_name}'未配置")
            else:
                print(f"success, 当前环境: {self._env_name}={self.env}")
        else:
            if cmd == "stop":
                print("已停止所有supervisor任务")
            else:
                print("未找到可用配置")


def setenv(envs):
    if not isinstance(envs, (list, tuple)):
        print("ERROR: setenv 参数必须是列表类型")
        sys.exit(1)
    class Register:
        def __init__(self, func):
            self.func = func

        def __get__(self, instance, cls):
            if instance is None:
                cls._env[self.func.__name__] = envs
            else:
                return self.func
    return Register


class _EnvironmentMeta(type):
    def __init__(cls, name, bases, dct):
        cls._env = {}
        super().__init__(name, bases, dct)
        inspect.getmembers(cls, inspect.ismethod)

class Environment(object, metaclass=_EnvironmentMeta):
    pass

