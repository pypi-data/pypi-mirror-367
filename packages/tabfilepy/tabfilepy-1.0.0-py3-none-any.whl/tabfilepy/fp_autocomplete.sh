# tabfilepy; A simple Python library (with associated cmd/bash script) which allows file directory tab auto-completions. 
# This library is free software; you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation; either version 2.1 of the License, or (at your option) any later version.
# This library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.
# You should have received a copy of the GNU Lesser General Public License along with this library; if not, see <https://www.gnu.org/licenses/>.

#!/bin/bash

# Ensure characters are displayed correctly
stty sane

# Prompt the user for a filename with autocompletion
while true; do
    read -e -p "File path: " filename
    ext_filename=$(eval echo "$filename")
    if [ $? -eq 0 ]; then
        break
    fi
done

# Write the result to a temporary file
echo "$ext_filename" > /tmp/filename_output.txt
