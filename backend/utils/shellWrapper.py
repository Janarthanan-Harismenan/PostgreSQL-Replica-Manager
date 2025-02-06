class ShellWrapper:
    def __init__(self, shell):
        self.shell = shell

    def send(self, command):
        self.shell.stdin.write(command)
        self.shell.stdin.flush()

    def close(self):
        self.shell.terminate()
        self.shell.wait()
        self.shell.stdin.close()
        
    def recv_ready(self):
        return self.shell.stdout.channel.recv_ready()
    
    def recv(self, size):
        return self.shell.stdout.read(size)