



from fabric.api import run, env

from fabric.tasks import execute

env.hosts = ['localhost']

def deploy():
    run("ls")

if __name__ == "__main__":
    execute(deploy)
