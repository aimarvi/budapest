import time
import os
import fcntl

def read_trigger(dev='/dev/hidraw1'):
    with open(dev, 'rb') as f:
        print('Listening for trigger...')
        while True:
            data = f.read(8)
            if not data:
                continue
            return True

def check_trigger(dev='/dev/hidraw1'):
    try:
        with open(dev, 'rb') as f:
            f.read(8)  # discard stale data
            f.setblocking(False)  # don't block on read
            data = f.read(8)
            if data and data[0] != 0:
                return True
    except Exception as e:
        print(f"Trigger read error: {e}")
    return False

def check_trigger_continuous(f):
    try:
        data = f.read(8)
        if data and data[0] != 0:
            return True
    except BlockingIOError:
        pass  # no data available
    return False

def check_trigger_fd(fd):
    try:
        data = os.read(fd, 8)
        if data and data[0] != 0:
            return True
    except BlockingIOError:
        pass  # No data available
    return False

if __name__=='__main__':
    # Open the device in read-only mode
    fd = os.open('/dev/hidraw1', os.O_RDONLY)
    
    # Set the file descriptor to non-blocking
    flags = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

    print('yay!')
