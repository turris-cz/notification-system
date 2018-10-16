import logging.handlers
import os
import shlex
import signal
import subprocess
import sys


class Supervisor:
    def __init__(self):
        self.process = None
        self.cmd = None
        self.timeout = None

        # create separate logger for new process
        self.logger = None

        self.init_logger()

    def init_logger(self):
        self.logger = logging.getLogger('notifylib')
        self.logger.setLevel(logging.DEBUG)

        syslog_handler = logging.handlers.SysLogHandler(address='/dev/log')
        syslog_handler.setLevel(logging.INFO)

        formatter = logging.Formatter('%(name)s %(message)s')
        syslog_handler.setFormatter(formatter)

        self.logger.addHandler(syslog_handler)

    def fork(self):
        """Double fork process"""
        try:
            pid = os.fork()
            if pid > 0:
                return
        except OSError as e:
            self.logger.error("fork #1 failed: %d (%s)", e.errno, e.strerror)
            sys.exit(1)

        os.setsid()

        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as e:
            self.logger.error("fork #2 failed: %d (%s)", e.errno, e.strerror)
            sys.exit(1)

        self.run_proc()
        exit_code = self.join()

        self.logger.info("Process exited with exit code %s", exit_code)
        if exit_code != 0:
            self.logger.info("stdout: %s", self.process.stdout.readline())
            self.logger.warning("stderr: %s", self.process.stderr.readline())

        sys.exit(0)

    def run_proc(self):
        try:
            self.process = subprocess.Popen(
                shlex.split(self.cmd),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
        except FileNotFoundError:
            self.logger.error("Couldn't execute '%s'. Executable '%s' not found", self.cmd, shlex.split(self.cmd)[0])
            sys.exit(1)

    def run(self, cmd, timeout):
        self.cmd = cmd
        self.timeout = timeout
        self.fork()

    def join(self):
        signal.signal(signal.SIGALRM, self.timeout_handler)
        signal.alarm(self.timeout)

        exit_code = self.process.wait()

        signal.alarm(0)

        return exit_code

    def timeout_handler(self, signum, frame):
        self.logger.info("Terminating process due to timeout")
        self.process.terminate()
