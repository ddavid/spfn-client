from subprocess import Popen, PIPE

def main():
  cmds_list  = [['/home/ddodel/miniconda3/bin/python', 'server.py'],['/home/ddodel/Documents/github-repos/PCLServer/build/server']]
  procs_list = [Popen(cmd, stdout=PIPE, stderr=PIPE) for cmd in cmds_list]
  for proc in procs_list:
    proc.wait()

if __name__ == "__main__":
  main()
