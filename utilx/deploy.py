# -*- coding: utf-8 -*-
"""
@time: 2020/4/26 2:11 下午
@desc: 基于supervisor的项目一键自启动挂后台工具

配置说明
注意：如果是执行python程序，命令python启动命令要加-u参数，example: python -u app.py

设startsecs=1, startretries=3（都是默认值），如果有一程序有这些行为：
a) 启动即退出，exit code为0, 那么supervisor会在重试3试后停止重试，进程状态为FATAL。
b) 启动即退出，exit code为1, 那么supervisor会在重试3试后停止重试，进程状态为FATAL。
c) 启动3秒后退出，exit code为1, 那么supervisor会无限重启程序，无视startretries。
d) 启动3秒后退出，exit code为0, 那么supervisor不会重启，进程状态为EXIT。
"""
import sys
import os
import getpass
from abc import ABC, abstractmethod

import fire
from plan import Plan, PlanError


class Config(object):
    user = getpass.getuser()
    autorestart = True
    startsecs = 5
    redirect_stderr = "true"
    stdout_logfile_maxbytes = "200MB"
    stdout_logfile_backups = 5
    killasgroup = "true"
    stopasgroup = "true"
    template = """[program:{project}_{name}]\n\n{config_content}\n"""

    def __init__(self, home, config):
        if config is None:
            config = {}
        self.tasks = []
        self.home = home
        self.project = os.path.basename(self.home)
        self.config = {
            "user": self.user,
            "directory": self.home,
            "startsecs": self.startsecs,
            "autorestart": self.autorestart,
            "killasgroup": self.killasgroup,
            "stopasgroup": self.killasgroup,
            "redirect_stderr": self.redirect_stderr,
            "stdout_logfile_backups": self.stdout_logfile_backups,
            "stdout_logfile_maxbytes": self.stdout_logfile_maxbytes,
            "environment": f'PATH={os.path.join(sys.prefix, "bin")}:%(ENV_PATH)s'
        }
        self.config.update(config)

    @staticmethod
    def convert_config_text(config):
        if config is None:
            return ""
        else:
            return "\n".join([f"{k: <25}= {v}" for k, v in config.items()])

    def add(self, name, command):
        logfile = self.get_log_path(name)
        config = {"command": command, "stdout_logfile": logfile, **self.config}
        config_content = self.convert_config_text(config)
        task_config = self.template.format(project=self.project, name=name, config_content=config_content)
        self.tasks.append(task_config)

    def get_log_path(self, name):
        return os.path.join(self.home, "logs", f"{name}.log")

    def export(self, content=None):
        if content is None:
            content = "\n".join(self.tasks)
        print(content)
        file = f"{self.project}.utilx.ini"
        with open(file, "w") as f:
            f.write(content)
        log_path = os.path.join(self.home, "logs")
        if not os.path.exists(log_path):
            os.makedirs(log_path)
        return file


class BaseDeployment(ABC):

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    def restart(self):
        self.stop()
        self.start()

    def help(self):
        print(f"Usage: python {sys.argv[0]} [start|stop|restart]")

    def execute(self, option):
        """
        [start|stop|restart]
        """
        actions = {
            "start": self.start,
            "stop": self.stop,
            "restart": self.restart,
        }
        actions.get(option, self.help)()

    def deploy(self):
        fire.Fire(self.execute)


class Deployment(BaseDeployment):
    python = os.path.join(sys.prefix, "bin", "python")

    def __init__(self, commands=None, script=None, crons=None,
                 config=None, need_sudo=False, supervisor_conf_path="/etc/supervisord.d/"):
        self.need_sudo = need_sudo
        self.supervisor_conf_path = supervisor_conf_path
        self.crons = self.get_crons(crons)
        self.scripts = self.get_scripts(script)
        self.commands = self.get_commands(commands)
        self.home = os.path.dirname(os.path.abspath(self.__module__))
        self.config = Config(self.home, config)
        self.cron = Plan(self.config.project)
        self.init_tasks()

    def init_tasks(self):
        for name, cmd in self.commands:
            self.config.add(name, cmd)
        for name, cmd in self.scripts:
            self.config.add(name, cmd)
        for cron in self.crons:
            self.cron.command(cron)

    def get_scripts(self, script_obj):
        if script_obj is None:
            return []
        else:
            # 存放脚本文件名称
            script_file_name = os.path.abspath(sys.modules[script_obj.__module__].__file__)
            scripts = [name for name in dir(script_obj) if not name.startswith("_")]
            return [(script, f"{self.python} -u {script_file_name} {script}") for script in scripts]

    def get_commands(self, commands):
        name_commands = []
        if commands:
            name_commands = commands
        return name_commands

    def get_crons(self, crons_config):
        crons = []
        if crons:
            crons = crons_config
        return crons

    def update_supervisor(self, file):
        if self.need_sudo:
            code1 = os.system(f"sudo mv {file} {self.supervisor_conf_path}")
            code2 = os.system("sudo supervisorctl update")
        else:
            code1 = os.system(f"mv {file} {self.supervisor_conf_path}")
            code2 = os.system("supervisorctl update")
        return code1 or code2

    def update_cron(self, action):
        try:
            self.cron.update_crontab(action)
        except PlanError:
            pass

    def start(self):
        config_file = self.config.export()
        self.update_cron("update")
        return self.update_supervisor(config_file)

    def stop(self):
        config_file = self.config.export(content="")
        self.update_cron("clear")
        return self.update_supervisor(config_file)
