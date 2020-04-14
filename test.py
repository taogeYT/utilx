from run import TestDeploy
from utilx.deploy import Supervisor


supervisor = Supervisor(TestDeploy)
supervisor.export()
