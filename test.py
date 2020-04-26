from utilx.deploy import Deployment

commands = [("demo", "ping www.example.com")]

Deployment(commands=commands).config.export()
