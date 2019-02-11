import logging
import os
import shlex
import signal
import subprocess
import sys

logger = logging.getLogger(__name__)


class Supervisor:
    def __init__(self):
        self.process = None
        self.cmd = None
        self.cmd_args = None
        self.timeout = None

    def fork(self):
        """Double fork process"""
        try:
            pid = os.fork()
            if pid > 0:
                return
        except OSError as e:
            logger.error("fork #1 failed: %d (%s)", e.errno, e.strerror)
            os._exit(1)

        os.setsid()

        try:
            pid = os.fork()
            if pid > 0:
                os._exit(0)
        except OSError as e:
            logger.error("fork #2 failed: %d (%s)", e.errno, e.strerror)
            sys.exit(1)

        self.run_proc()
        exit_code = self.join()

        if exit_code != 0:
            logger.error("Process exited with exit code %s", exit_code)
            logger.error("stdout: %s", self.process.stdout.readline())
            logger.error("stderr: %s", self.process.stderr.readline())

        # dettach stdin/out/err and close them
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, 0)
        os.dup2(devnull, 1)
        os.dup2(devnull, 2)
        os.close(devnull)

        os._exit(0)

    def run_proc(self):
        try:
            if self.cmd_args:
                cmd = f'{self.cmd} {self.cmd_args}'
            else:
                cmd = self.cmd

            self.process = subprocess.Popen(
                shlex.split(cmd),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
        except ValueError as e:
            logger.error("Failed to parse command: %s", e)
            sys.exit(1)
        except FileNotFoundError:
            logger.error("Couldn't execute '%s'. Executable '%s' not found", self.cmd, shlex.split(self.cmd)[0])
            sys.exit(1)

    def run(self, cmd, cmd_args, timeout):
        self.cmd = cmd
        self.cmd_args = cmd_args
        self.timeout = timeout
        self.fork()

    def join(self):
        signal.signal(signal.SIGALRM, self.timeout_handler)
        signal.alarm(self.timeout)

        exit_code = self.process.wait()

        signal.alarm(0)

        return exit_code

    def timeout_handler(self, signum, frame):
        logger.warning("Terminating process due to timeout")
        self.process.terminate()
