import time
import subprocess as sub
import server
import concurrent.futures as futures
from multiprocessing import Pool

def main():

  # Pool of two concurrent processes
  pool = Pool(2)

  for output, error in pool.imap(
  #with futures.ProcessPoolExecutor(max_workers=2) as executor:
    #future_pyserver = executor.submit(server.main())
    print("Started py TCP server")
    # Sleep so that PCLServer's TCP client doesn't start before our python server
    #time.sleep(.2)
    #future_pcl      = executor.submit(sub.call("/home/ddodel/Documents/github-repos/PCLServer/build/server"))
    #print("Started PCL Server")
  #while future_pyserver.running() and future_pcl.running():
    #futures.wait()

if __name__ == '__main__':
  main()
