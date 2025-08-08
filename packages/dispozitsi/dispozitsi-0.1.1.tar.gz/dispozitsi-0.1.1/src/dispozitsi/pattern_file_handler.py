# Copyright (C) 2025 Spuzkov

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

import codecs

loaded_patterns = {}

class PatternFileHandler:
    def __init__(self):
        self.lines = []

    def load_patterns(self):
        """
        Reads through file(s) and then appends patterns dictionary
        with a pattern name as key and pattern regex as value.
        """
        try:
            with codecs.open("src/dispozitsi/patterns/grok-patterns", "r", encoding="utf-8") as pattern_file:
                for line in pattern_file:
                    striped_line = line.strip()
                    if not striped_line or striped_line.startswith("#"):
                        continue
                    name, pattern = striped_line.split(" ", maxsplit=1)
                    loaded_patterns[name] = pattern
        except FileNotFoundError:
            # TODO: Raise cusotm error that will be handled in the app
            pass
