#coding=utf-8
import threading
import re
import serial
import queue

default_response = b'(OK;|ERR;)'
DEFAULT_PORT = '/dev/cu.usbserial'

def read_job(nonblock_port, q, exit_event):
    in_buffer = bytearray()
    while True:
        n = nonblock_port.in_waiting
        if (n > 0):
            in_buffer = in_buffer + nonblock_port.read(n)
        pattern = re.compile(default_response)
        match = re.search(pattern, in_buffer)
        if match:
            break
        if exit_event.is_set():
            break
    q.put(in_buffer)

def mark_exit_event(exit_event):
    exit_event.set()


def read_sync(port, timeout):
    '''@summary: sync access port until we get default_response or timeout, return bytesarray type data

    @param port: port name
    @param timeout: wait time before aborting, floating value in second
    '''
    exit_event = threading.Event()

    q = queue.Queue()
    thd = threading.Thread(target=read_job, kwargs={'nonblock_port': port,
                                                    'q': q,
                                                    'exit_event': exit_event})
    timer = threading.Timer(timeout, mark_exit_event, [exit_event])
    thd.start()
    timer.start()
    thd.join()
    timer.cancel()
    return q.get()

def test_read_sync():
    global DEFAULT_PORT
    port = DEFAULT_PORT
    port = serial.Serial(port, 9600, timeout=0)
    port.write(b'AT;')
    print(read_sync(port, 2))

if __name__ == '__main__':
    test_read_sync()