import time

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

if __name__=='__main__':
    while not read_trigger():
        continue

    print('yay!')
