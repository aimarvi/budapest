import time

def read_trigger(dev='/dev/hidraw1'):
    with open(dev, 'rb') as f:
        print('Listening for trigger...')
        while True:
            data = f.read(8)
            if not data:
                continue
            return True

if __name__=='__main__':
    while not read_trigger():
        continue

    print('yay!')
