from subprocess import Popen, PIPE

def main():


    """
    Small File for executing SPFN and PCL Servers
    :return: void
    """
    logfile = open('test-spfn.log', 'w')
    logerr = open('spfn-error.log', 'w')

    cmds_list = [['/home/ddodel/miniconda3/bin/python', 'server.py']#, '-ip "127.0.0.1"', '-p 4445']
        ,['/home/ddodel/Documents/github-repos/PCLServer/build/server']
        ,['/home/ddodel/miniconda3/bin/python', './tests/client.py']]
    procs_list = [Popen(cmd, stdout=logfile, stderr=logerr) for cmd in cmds_list]
    for proc in procs_list:
        proc.wait()
        #logfile.flush()

if __name__ == "__main__":
  main()
