'''
tabfilepy; A simple Python library (with associated cmd/bash script) which allows file directory tab auto-completions. 
This library is free software; you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation; either version 2.1 of the License, or (at your option) any later version.
This library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along with this library; if not, see <https://www.gnu.org/licenses/>.
'''

import subprocess
import os
import tempfile

class tabfilepy:
    def __init__(self, windows_script="fp_autocomplete.cmd", posix_script="fp_autocomplete.sh"):
        self.PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.windows_script = os.path.join(self.PACKAGE_DIR, windows_script)
        self.posix_script = os.path.join(self.PACKAGE_DIR, posix_script)
        self.temp_file = os.path.join(tempfile.gettempdir(), 'filename_output.txt')

    def get_filename(self):
        """Retrieve the filename using the appropriate autocomplete script."""
        try:
            if os.name == "nt":
                subprocess.run(['cmd', '/c', self.windows_script], check=True)
            else:
                subprocess.run(['bash', self.posix_script], check=True)
            return self._read_output()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error executing script: {e}")

    def _read_output(self):
        """Reads the filename from the temporary output file."""
        if os.path.exists(self.temp_file):
            with open(self.temp_file, 'r') as file:
                return file.read().strip()
        raise FileNotFoundError("Output file not found.")

def main():
    result = tabfilepy().get_filename()
    print(result)
