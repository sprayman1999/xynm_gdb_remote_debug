# xynm_gdb_remote_debug
适用于同一个系统两个终端，一个为exp，另一个gdb调试的情况，全自动附加.
一般适用于docker中pwn编写。
exp文件附上以下代码:
```
def debug_remote(pid,gdb_script = []):
    global gdb_attach_remote_port
    sh = remote("127.0.0.1",gdb_attach_remote_port)
    payload = "pid=%s\n"%pid
    for i in gdb_script:
        payload += "gdb_script=%s\n"%i
    sh.send(payload)
    sh.recvuntil("Done")
    sh.close()
```
然后再需要debug的时候,调用一下代码即可
```
debug_remote(io.pid)
debug_remote(io.pid,gdb_script = ['vmmap','heap'])
```

启动服务器
```
python debug_remote_server.py
```
然后运行exp，即可看到gdb交互
