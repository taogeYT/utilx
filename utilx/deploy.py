import sys
import os
import importlib
import getpass
import inspect

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

    def __init__(self, cls_name, commands=[], config={}, env_name="PY_ENV"):
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
        methods = dict(inspect.getmembers(self.cls(), inspect.ismethod))
        funcs = dict(inspect.getmembers(self.cls(), inspect.isfunction))
        return [name for name in (*methods.keys(), *funcs.keys()) if not name.startswith("_")]

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

    def export(self, file=None):
        """
        supervisor配置导出
        file 默认路径 /etc/supervisord.d/
        """
        if file is None:
            _file = f"/etc/supervisord.d/{self.project}.ini"
        else:
            _file = file
        config_content = self.gen_config()
        self.update_conf_file(config_content, _file)
        if file is None:
            os.system("sudo supervisorctl update")
        if config_content:
            if self.env is None:
                print(f"WARN: 环境变量'{self._env_name}'未配置")
            else:
                print(f"success, 当前环境: {self._env_name}={self.env}")
        else:
            print("未找到可用配置")

    def update_conf_file(self, content, file_path):
        with open(file_path, "w") as f:
            f.write(content)


if __name__ == '__main__':
    # cmds = [
    #     ("celery", "/usr/local/anaconda3/bin/celery worker -l INFO -A webapp.api.celery"),
    # ]
    class T:
        def _f(self):
            pass
    Setup(T).export("test.ini")
