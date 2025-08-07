import subprocess

from rpmlint.helpers import ENGLISH_ENVIRONMENT


class ArParser:
    """
    Class contains all information obtained by ar command.
    """

    def __init__(self, pkgfile_path):
        self.pkgfile_path = pkgfile_path
        self.objects = []
        self.parsing_failed_reason = None
        self.parse()

    def parse(self):
        r = subprocess.run(['ar', 't', self.pkgfile_path], encoding='utf8',
                           capture_output=True, env=ENGLISH_ENVIRONMENT)
        if r.returncode != 0:
            self.parsing_failed_reason = r.stderr
            return

        self.objects = r.stdout.splitlines()
