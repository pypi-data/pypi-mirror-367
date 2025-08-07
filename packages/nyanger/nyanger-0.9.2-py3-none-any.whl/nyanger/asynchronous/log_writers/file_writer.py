#     Nyanger is a simple logger designed to be simple to use and simple to modify.
#
#     Copyright (C) 2024  Kirill Harmatulla Shakirov  kirill.shakirov@protonmail.com
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.

import asyncio
from nyanger.asynchronous.nyan import LogLevel, LogMessage, LogWriter


class FileWriter(LogWriter):
    """
    Simple implementation of LogWriter.
    Writes log messages to file
    """
    def __init__(self, file_name: str, loging_level: LogLevel = LogLevel.DEBUG):
        """
        Initialize FileWriter instance.
        :param file_name: log file name
        :param loging_level: messages with severity less than this field value will be filtered out.
        """
        self._loging_level = loging_level
        self._file_name = file_name
        self._log_file = None

    async def start(self, loop: asyncio.AbstractEventLoop):
        self._log_file = open(self._file_name, mode="ta")

    async def write(self, msg: LogMessage):
        """
        Formats and writes msg to log file.
        :param msg: message to be logged.
        """
        if msg.severity.value <= self._loging_level.value:
            log_text = f"{msg.time.isoformat()} {msg.severity.name}: {msg.text}\n"
            await asyncio.to_thread(self._log_file.write, (log_text,))
            # await asyncio.to_thread(self._log_file.flush)

    async def stop(self):
        self._log_file.flush()
        self._log_file.close()
