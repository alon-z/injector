from sys import argv
from subprocess import run

import time
import signal
import os

#args
def usage():
    print("USAGE: %s [--pid <target of pid to be injected>]" % argv[0])
    print("")
    print("Try '%s -h' for more options." % argv[0])
    exit()

#help
def help():
    print("USAGE: %s [--pid <target of pid to be injected>]" % argv[0])
    print("")
    print("optional arguments:")
    print("   -h                       print this help")
    print("   --pid pid                target of pid to be injected")
    print("")
    print("examples:")
    print("    injector --pid 4586     # bind to socket of pid 4586")
    exit()
    
def cleanup(signum, frame):
  print('cleanup')
  pcleanup = run(['gdb', '-batch','-ex', 'attach {}'.format(pid), '-ex', 'p (size_t) dup2(0,1)', '-ex', 'quit'])
  exit(1)
 
    
#arguments
pid=""

if __name__ == '__main__':
  if os.geteuid() != 0:
    exit("You need to have root privileges to run this script.")

  # arguments handle
  if len(argv) == 1:
    usage()
  elif len(argv) == 2:
    if str(argv[1]) == '-h':
      help()
    else:
      usage()
  elif len(argv) == 3:
    if str(argv[1]) == '--pid':
      pid = argv[2]
    else:
      usage()
  elif len(argv) > 3:
    usage()
 
  # get current tty from pid's stdout
  tty=os.readlink('/proc/{}/fd/1'.format(pid))
 
  tmpfile='/tmp/proc-{}'.format(pid)
  # move stdout to a different file
  p1 = run(['gdb', '-batch','-ex', 'attach {}'.format(pid), '-ex', 'p close(1)', '-ex', 'p creat("{}", 0600)'.format(tmpfile), '-ex', 'quit'])

  # set cleanup if proccess gets terminated
  signal.signal(signal.SIGINT, cleanup)

  # file check loop, get each line and pass it after check
  with open(tmpfile, 'r') as f:
    while True:
      new = f.readline()
      if new:
        if 'SECRET' in new:
          print('found a secret')
        else:
          #pipe = open('/proc/{}/fd/0'.format(pid), 'a')
          pipe = open(tty, 'a')
          pipe.write(new)
          pipe.close()
      else:
        time.sleep(0.5)
