# debugger_scripts

## Installation
Installation scripts are in `lldb_utilities.py` and `gdb_utilities.py`. Please efer to the python file.

## Features
### gdb
1. display a range memory in `xxd` format 
    ```
    xxd {addr} {size}
    ```
2. search the whole memory
This command is just like the `find` command in gdb: 
[https://sourceware.org/gdb/onlinedocs/gdb/Searching-Memory.html](https://sourceware.org/gdb/onlinedocs/gdb/Searching-Memory.html), 
except that it searches in the whole valid memory mappings.

    e.g.:
    ```
    full_search /b 0xff,0xff,0xff,0xfc
    ```
3. stop when library is loaded
    ```
    stop_at_load {libname}
    ```
    This is useful when you do an early trace that most libraries are not loaded yet. It's similar to the feature provided by IDA.
4. stop when file is opened
    ```
    stop_at_open {filename}
    ```
    After the file is opened, the `fd` will be printed for further using.
5. stop when file is read
    ```
    stop_at_read {fd}
    ```
    The `fd` is obtained from `stop_at_open` in the 4th feature.
### lldb
