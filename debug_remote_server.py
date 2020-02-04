import subprocess 
import thread
import sys
import os
from pwn import *
import readline
context.log_level = "CRITICAL"
bind_port = 55667
if(len(sys.argv) > 1):
    bind_port = int(sys.argv[1],10)
'''
popen = None
def gdb_attach_func(sh):
    global popen
    pid = sh.recv()
    sh.close()
    print("pid: " + str(pid))
    #popen = subprocess.Popen(['gdb','attach',pid],stdin=subprocess.PIPE)
    popen = subprocess.Popen(['gdb','attach',pid],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
    thread.start_new_thread(gdb_msg_show,())
    while True:

        command = raw_input(term.text.bold_red("pwndbg> ")).strip()
        if(command == ''):
            continue
        popen.stdin.write(command + "\n")
        if command == 'quit':
            popen.terminate()
            break
def gdb_msg_show():
    global popen
    while True:
        line = popen.stdout.readline()
        pos = line.find("pwndbg>")
        if pos != -1:
            print line.replace("pwndbg>","")
            continue
        if line == '' and popen.poll() != None:
            break
        print line,
'''
gdb_process = None
sh = None
def gdb_attach_func(sh):
    global gdb_process
    payload = sh.recv()
    pid = payload[payload.find("pid=") + len("pid="):payload.find("\n")]
    gdb_script_list = payload.split("gdb_script=")
    del gdb_script_list[0]
    for i in range(0,len(gdb_script_list)):
        gdb_script_list[i] = gdb_script_list[i].strip()
    print("pid: %s"%pid)
    print("gdb_scirpt_list: %s"%gdb_script_list)
    context.log_level = "CRITICAL"
    gdb_process = process(["gdb"],shell=True)
    gdb_process.sendline("attach %s"%pid)
    gdb_process.recvuntil("pwndbg>")
    for i in gdb_script_list:
        gdb_process.sendline(i)
        print "\n%s"%gdb_process.recvuntil("pwndbg> "),
        print gdb_process.recv()
    #gdb_process.interactive(prompt="")
    sh.send("Done")
    sh.close()
    prompt = ''
    go = threading.Event()
    def recv_thread():
        while not go.isSet():
            try:
                cur = gdb_process.recv(timeout=0.05)
                cur = cur.replace(gdb_process.newline, b'\n')
                if cur:
                    stdout = sys.stdout
                    if not term.term_mode:
                        stdout = getattr(stdout, 'buffer', stdout)
                    stdout.write(cur)
                    stdout.flush()
            except EOFError:
                break
    t = context.Thread(target = recv_thread)
    t.daemon = True
    t.start()
    try:
        while not go.isSet():
            if term.term_mode:
                data = term.readline.readline(prompt=prompt, float=True)
            else:
                stdin = getattr(sys.stdin, 'buffer', sys.stdin)
                data = stdin.read(1)
            if data:
                try:
                    if(data != 'quit\n'):
                        gdb_process.send(data)
                    else:
                        gdb_process.terminate()
                        return
                except EOFError:
                    go.set()
            else:
                go.set()
    except KeyboardInterrupt:
        go.set()
    while t.is_alive():
        t.join(timeout=0.1)
def gdb_remote_server_start():
    global bind_port
    while True:
        try:
            print("Debug server start!\nbind port %d"%bind_port)
            gdb_server = listen(bind_port)
            sh = gdb_server.wait_for_connection()
            gdb_attach_func(sh)
        except KeyboardInterrupt:
            gdb_server.close()
            if 'sh' in dir():
                sh.close()
            if gdb_process is not None:
                gdb_process.terminate()
            break
            continue
        except EOFError:
            gdb_server.close()
            if 'sh' in dir():
                sh.close()
            continue
if __name__ == "__main__":
    gdb_remote_server_start()
