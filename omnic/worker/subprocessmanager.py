import subprocess

from omnic import singletons


class SubprocessManager(list):
    '''
    Singleton that handles running and awaiting subprocesses
    '''
    async def run(self, cmd, **kwargs):
        subprocess.run(cmd, **kwargs)


singletons.register('subprocess', SubprocessManager)
