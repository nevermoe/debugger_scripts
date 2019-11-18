import gdb
import traceback

# installation
"""
cat <<EOT >> ~/.gdbinit 
define xxd
    dump binary memory dump.bin $arg0 ((void*)$arg0)+$arg1
    shell xxd dump.bin
    shell rm dump.bin
end

source `pwd`/gdb_utilities.py >> ~/.gdbinit
EOT
"""

class StopAtRead64(gdb.Command):
    def __init__(self):
        super(StopAtRead64, self).__init__('stop_at_read64', gdb.COMMAND_NONE)

    def invoke(self, target_fd, from_tty):
        gdb.execute('set pagination off')
        gdb.execute('handle all nostop pass noprint')
        gdb.execute('disable breakpoints')
        gdb.execute('set scheduler-locking step')

        ret = gdb.execute('info address read', False, True)
        ret = ret.split()
        read_addr = None
        for addr in ret:
            if addr.startswith('0x'):
                read_addr = addr
                break

        gdb.execute('break *(%s)' % (read_addr))

        fd = ''
        while target_fd not in fd:
            gdb.execute('continue')
            fd = gdb.execute('info register r0', False, True)
            print "fd: %s" % fd

        print "found fd: %s" % fd

StopAtRead64()

class StopAtOpen64(gdb.Command):
    def __init__(self):
        super(StopAtOpen64, self).__init__('stop_at_open64', gdb.COMMAND_NONE)

    def invoke(self, target_file, from_tty):
        gdb.execute('set pagination off')
        gdb.execute('handle all nostop pass noprint')
        gdb.execute('disable breakpoints')
        gdb.execute('set scheduler-locking step')

        ret = gdb.execute('info address open', False, True)
        ret = ret.split()
        open_addr = None
        for addr in ret:
            if addr.startswith('0x'):
                open_addr = addr
                break

        gdb.execute('break *(%s)' % (open_addr))

        file_name = ''
        fd = ''
        while target_file not in file_name:
            gdb.execute('continue')
            file_name = gdb.execute('x/s $r0', False, True)
            print "file opened: %s" % (file_name.rstrip())

        lr = gdb.execute('info registers lr', False, True)
        lr = lr.split()[1]
        lr = int(lr,16) & 0xFFFFFFFE

        # execute until open return
        gdb.execute('break *0x%x' % lr)
        gdb.execute('set scheduler-locking on') # lock thread
        gdb.execute('continue')
        gdb.execute('set scheduler-locking step') # unlock thread

        # get fd from r0
        fd = gdb.execute('info register r0', False, True)

        print "file opened: %s\n fd: %s" % (file_name.rstrip(), fd)

StopAtOpen64()

class StopBeforeInit64(gdb.Command):
    def __init__(self):
        super(StopBeforeInit64, self).__init__('stop_before_init64', gdb.COMMAND_NONE)

    def invoke(self, target_library, from_tty):
        gdb.execute('set pagination off')
        gdb.execute('handle all nostop pass noprint')
        gdb.execute('disable breakpoints')
        gdb.execute('set scheduler-locking step')

        # match __dl__Z9do_dlopenPKciPK17android_dlextinfoPv or __dl__Z9do_dlopenPKciPK17android_dlextinfo 
        ret = gdb.execute('info functions do_dlopen.*android_dlextinfo', False, True)
        dlopen_addr = None
        words = ret.split()
        for word in words:
            if word.startswith('0x'):
                dlopen_addr = word
                break

        gdb.execute('break *(%s)' % (dlopen_addr))

        library_name = ''
        while target_library not in library_name:
            gdb.execute('continue')
            library_name = gdb.execute('x/s $r0', False, True)
            print "library_name: %s " % library_name

        # # match __dl__ZN6soinfo17call_constructorsEv (Android 6.0.1)
        # ret = gdb.execute('info functions call_constructors', False, True)
        # call_constructors_addr = None
        # words = ret.split()
        # for word in words:
        #      if word.startswith('0x'):
        #          call_constructors_addr = word
        #          break

        # gdb.execute('break *(%s)' % (call_constructors_addr))

        # # execute until call_constructors
        # gdb.execute('set scheduler-locking on') # lock thread
        # gdb.execute('continue')
        # gdb.execute('set scheduler-locking step') # unlock thread

        # print "library %s loaded before init array executed" % library_name

StopBeforeInit64()

class StopAtLoad64(gdb.Command):
    def __init__(self):
        super(StopAtLoad64, self).__init__('stop_at_load64', gdb.COMMAND_NONE)

    def invoke(self, target_library, from_tty):
        gdb.execute('set pagination off')
        gdb.execute('handle all nostop pass noprint')
        gdb.execute('disable breakpoints')
        gdb.execute('set scheduler-locking step')

        # match __dl__Z9do_dlopenPKciPK17android_dlextinfoPv or __dl__Z9do_dlopenPKciPK17android_dlextinfo 
        ret = gdb.execute('info functions do_dlopen.*android_dlextinfo', False, True)
        dlopen_addr = None
        words = ret.split()
        for word in words:
            if word.startswith('0x'):
                dlopen_addr = word
                break

        gdb.execute('break *(%s)' % (dlopen_addr))

        library_name = ''
        while target_library not in library_name:
            gdb.execute('continue')
            library_name = gdb.execute('x/s $x0', False, True)
            print "library_name: %s " % library_name

        lr = gdb.execute('info registers lr', False, True)
        lr = lr.split()[1]
        lr = int(lr,16) & 0xFFFFFFFE

        # execute until dlopen return
        gdb.execute('break *0x%x' % lr)
        gdb.execute('set scheduler-locking on') # lock thread
        gdb.execute('continue')
        gdb.execute('set scheduler-locking step') # unlock thread

        print "library %s loaded" % library_name

StopAtLoad64()


class FullSearch(gdb.Command):
    def __init__(self):
        super(FullSearch, self).__init__('full_search', gdb.COMMAND_NONE)

    def invoke(self, argv, from_tty):
        proc_mappings = gdb.execute('info proc mappings', False, True)
        
        #[/sn] parameter
        sn = argv.split(' ')[0]
        if not sn.startswith('/'):
            sn = ''
        bytes = argv.strip(sn)

        for line in proc_mappings.splitlines():
            arr = line.strip().split(' ')
            start_addr = arr[0].strip()

            if start_addr.startswith('0x'):
                end_addr = arr[1].strip()

                try:
                    # print 'find %s %s, %s, %s' % (sn, start_addr, end_addr, bytes)
                    result = gdb.execute('find %s %s, %s, %s' % (sn, start_addr, end_addr, bytes), False, True )
                    if "Pattern not found." not in result:
                        print result
                except Exception as e:
                    print traceback.format_exc()

FullSearch()

class InfoLib(gdb.Command):
    def __init__(self):
        super(InfoLib, self).__init__('infolib', gdb.COMMAND_NONE)

    def invoke(self, lib, from_tty):
        proc_mappings = gdb.execute('info proc mappings', False, True)
        
        for line in proc_mappings.splitlines():
            if lib in line:
                print line

InfoLib()


class LogStepOver(gdb.Command):
    def __init__(self):
        super(LogStepOver, self).__init__('log_step_over', gdb.COMMAND_NONE)

    def invoke(self, addr, from_tty):
        gdb.execute('set pagination off')
        gdb.execute('handle all nostop pass noprint')
        gdb.execute('set scheduler-locking on') # lock thread

        while True:
            pc = gdb.execute('info register pc', False, True)
            pc = pc.split()[1]
            print "executing: 0x%x" % int(pc,16)
            if int(pc, 16) == int(addr, 16):
                break
            ret = gdb.execute('ni', False, True)

        gdb.execute('set scheduler-locking step') # unlock thread

LogStepOver()
