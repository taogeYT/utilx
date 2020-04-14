"""
supervisor
"""
import fire
import sys
import os
import getpass

from plan import Plan, PlanError

__all__ = ["Supervisor", "set_env", "Environment"]

"""
配置说明
注意：如果是执行python程序，命令python启动命令要加-u参数，example: python -u app.py

设startsecs=1, startretries=3（都是默认值），如果有一程序有这些行为：
a) 启动即退出，exit code为0, 那么supervisor会在重试3试后停止重试，进程状态为FATAL。
b) 启动即退出，exit code为1, 那么supervisor会在重试3试后停止重试，进程状态为FATAL。
c) 启动3秒后退出，exit code为1, 那么supervisor会无限重启程序，无视startretries。
d) 启动3秒后退出，exit code为0, 那么supervisor不会重启，进程状态为EXIT。
"""
config_template = """
[program:{project}_{name}]

command     = {command}
directory   = {home}
user        = {user}
autorestart = {autorestart}
startsecs   = {startsecs}
{env_config}
redirect_stderr         = {redirect_stderr}
stdout_logfile_maxbytes = {stdout_logfile_maxbytes}
stdout_logfile_backups  = {stdout_logfile_backups}
stdout_logfile          = {logfile}
killasgroup=true
stopasgroup=true
"""


class Supervisor(object):
    """
    example:
        commands = [("celery_task", "celery worker -l INFO -A webapp.api.celery")]
        class T(Environment):
            def task1(self):
                pass
        Supervisor(T, commands).export()
    """
    config = {"autorestart": True, "startsecs": 5, "redirect_stderr": "true",
              "stdout_logfile_maxbytes": "200MB", "stdout_logfile_backups": 5}

    def __init__(self, script=None, commands=None, config=None, env_name="PYENV"):
        if config is None:
            config = {}
        if commands is None:
            commands = []
        self.config.update(config)
        self.script = script
        self._commands = commands
        file_path = self.__module__
        self.python = os.path.join(sys.prefix, "bin", "python")
        self.home = os.path.dirname(os.path.abspath(file_path))
        self.project = os.path.basename(self.home)
        self._env_name = env_name
        self.env = os.getenv(env_name)
        python = os.path.join(sys.prefix, "bin")
        path = f'{python}:%(ENV_PATH)s'
        if self.env:
            self.env_config = f'environment=PATH={path},{env_name}={self.env}'
        else:
            self.env_config = f"environment=PATH={path}"
        self.cron = Plan(self.project)
        self.config.update(
            {"home": self.home, "user": getpass.getuser(), "project": self.project, "env_config": self.env_config})

    def _get_script_names(self):
        except_names = [name for name in self.script.env.keys() if self.env not in self.script.env[name]]
        names = [name for name in dir(self.script) if name != "env" and name not in except_names and not name.startswith("_")]
        return names

    def _gen_scripts_conf(self):
        configs = []
        for name in self._get_script_names():
            logfile = os.path.join(self.home, "logs", f"{name}.log")
            script = os.path.abspath(sys.modules[self.script.__module__].__file__)
            # script = "{self.home}/run.py"
            command = f"{self.python} -u {script} {name}"
            configs.append(config_template.format(command=command, name=name, logfile=logfile, **self.config))
        return configs

    def _gen_cmd_conf(self):
        configs = []
        for name, command, *envs in self._commands:
            if not envs or self.env in envs:
                logfile = os.path.join(self.home, "logs", f"{name}.log")
                configs.append(config_template.format(command=command, name=name, logfile=logfile, **self.config))
        return configs

    def gen_config(self):
        script_config = self._gen_scripts_conf() if self.script else []
        cmd_config = self._gen_cmd_conf()
        content = "".join([*script_config, *cmd_config])
        print(content)
        return content

    def update_conf_file(self, content, file_path):
        file = self.get_file(file_path)
        with open(file, "w") as f:
            f.write(content)

    def update_supervisor(self, file):
        if file is None:
            _file = self.get_file(file)
            log_dir = os.path.join(self.home, "logs")
            os.makedirs(log_dir) if not os.path.exists(log_dir) else None
            code1 = os.system(f"sudo mv {_file} /etc/supervisord.d/")
            code2 = os.system("sudo supervisorctl update")
            return code1 == 0 and code2 == 0

    def add_crontab(self, *args, **kwargs):
        """
        example:
            setup = Setup()
            setup.add_crontab('ls /tmp', every='1.day', at='12:00')

        every can be:

        [1-60].minute [1-24].hour [1-31].day
        [1-12].month [1].year
        jan feb mar apr may jun jul aug sep oct nov dec
        sun mon tue wed thu fri sat weekday weekend
        or any fullname of month names and day of week names
        (case insensitive)

        at can be:

        when every is minute, can not be set
        when every is hour, can be minute.[0-59]
        when every is day of month, can be minute.[0-59], hour.[0-23]
        when every is month, can be day.[1-31], day of week,
                             minute.[0-59], hour.[0-23]
        when every is day of week, can be minute.[0-59], hour.[0-23]

        at can also be multiple at values seperated by one space.
        """
        self.cron.command(*args, **kwargs)

    def export(self):
        """
        supervisor配置导出
        file 默认路径 /etc/supervisord.d/
        """
        fire.Fire(self._export)

    def get_file(self, file):
        if file is None:
            _file = f"{self.project}.ini"
        else:
            _file = file
        return _file

    def _export(self, cmd):
        """
        参数说明
        --cmd: [start|stop|restart]
        --file: 导出文件
        """
        if cmd == "start":
            self._start(None)
        elif cmd == "stop":
            self._stop(None)
        elif cmd == "restart":
            self._stop(None)
            self._start(None)
        else:
            print(f"Usage: python {sys.argv[0]} [start|stop|restart]")

    def _start(self, file):
        config_content = self.gen_config()
        self.update_conf_file(config_content, file)
        result = self.update_supervisor(file)
        if config_content:
            if self.env is None:
                print(f"WARN: 环境变量'{self._env_name}'未配置")
            else:
                if result:
                    self.cron.run("update")
                    print(f"success, 当前环境: {self._env_name}={self.env}")
                else:
                    print(f"failed, supervisor命令执行异常, 当前环境: {self._env_name}={self.env}")
        else:
            print("未找到可用配置")

    def _stop(self, file):
        config_content = ""
        self.update_conf_file(config_content, file)
        self.update_supervisor(file)
        try:
            self.cron.run("clear")
        except PlanError:
            print("没有要清空的crontab任务")
        print("已停止所有执行任务")


class _EnvironmentMeta(type):
    pass
    # def __init__(cls, name, bases, dct):
    #     cls._env = {}
    #     super().__init__(name, bases, dct)
    #     inspect.getmembers(cls, inspect.ismethod)


class Environment(object, metaclass=_EnvironmentMeta):
    env = {}


def set_env(envs):
    if not isinstance(envs, (list, tuple)):
        print("ERROR: set_env 参数必须是列表类型")
        sys.exit(1)

    def decorator(func):
        Environment.env[func.__name__] = envs

        def wrapper(*args, **kw):
            return func(*args, **kw)
        return wrapper
    return decorator
