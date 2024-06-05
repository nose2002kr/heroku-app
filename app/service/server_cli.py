import subprocess
from typing import Callable
from shlex import split
import sys

import asyncio
from asyncio.streams import StreamReader

async def request_to_proceed_commend_on_cli(
        command_line: str,
        progressFn: Callable[[str], None],
        wrapUpFn: Callable[[], None]):
    
    try:
        args = split(command_line)
        if len(args) <= 0:
            raise 'argument is too few.'
        
        #print(f'request_to_proceed_commend_on_cli; {split(command_line)}')

        process: subprocess.Popen = None
        try:
            process = await asyncio.create_subprocess_exec(*args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except FileNotFoundError:
            if sys.platform == 'win32':
                extensions = ['.exe', '.cmd', '.bat']
                for ext in extensions:
                    fixed_args = args.copy()
                    fixed_args[0] = fixed_args[0] + ext
                    try:
                        process = await asyncio.create_subprocess_exec(*fixed_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        #print('fixed by ' + fixed_args.__str__())
                        break
                    except FileNotFoundError:
                        #print('failed with ' + ext)
                        pass
        
        async def read_output(pipe: StreamReader, prefix: str):
            """
            Read lines from a pipe and call the callback function with each line.

            :param pipe: Pipe to read from (process.stdout or process.stderr)
            :param prefix: Prefix to add to each line (for distinguishing stdout and stderr)
            """
            while True:
                buf = await pipe.readline()
                if not buf:
                    break
                await progressFn(str(buf, 'utf-8').strip())

        await asyncio.gather(
            read_output(process.stderr,'stdout'),
            read_output(process.stdout,'stderr'))

    except Exception as e:
        await progressFn(e.__str__())
        await wrapUpFn(1008)
        return
        #print(e)
    
    await wrapUpFn()
