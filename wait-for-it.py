#!/bin/usr/env python

from optparse import OptionParser
import socket
import time
import sys
class OptionException(Exception):
    def __init__(self, value):
        self.value = value

class wait_for_app:
    def log(self, loginfo):
        if self.options.quiet is not False:
            print(loginfo)

    def build_log(self, type, app, time=0, tries=0):
        # 1=enable_timeout,2=disable_timeout,3=success_msg,4=unavailable,5=timeout_msg
        loginfo = {
             1:"%s: waiting %d seconds for %s" %(sys.argv[0],time,app),
             2:"%s: waiting for %s without a timeout" %(sys.argv[0],app),
             3:"%s: %s is available after %d seconds and %d tries" %(sys.argv[0],app,time,tries),
             4:"%s: %s is unavailable" %(sys.argv[0],app),
             5:"%s: timeout occurred after waiting %d seconds for %s" %(sys.argv[0],time,app),
        }.get(type)
        return loginfo

    def wait_for(self, host, port, timeout, retry_interval):
        tries = 0
        start_ts = None
        start_time = current = time.time()
        end_time = start_time + timeout

        while current < end_time:
            tries += 1
            self.app = ("%s:%d") %(host,port)
            sk = socket.socket()
            elapsed = current - start_time
            remaining_timeout = timeout - elapsed
            logmsg = self.build_log(2, self.app, remaining_timeout)
            if timeout != 0:
                logmsg = self.build_log(1, self.app, end_time - current)
                sk.settimeout(remaining_timeout)
            self.log(logmsg)
            if start_ts is None:
                start_ts = int(time.time())
            try:
                sk.connect((host,port))
                end_ts = int(time.time())
                diff_ts= end_ts - start_ts
                logmsg = self.build_log(3,self.app,diff_ts,tries)
                self.log(logmsg)
                return
            except:
                # if we fail, sleep a bit
                time.sleep(retry_interval)
            current = time.time()

        end_ts = int(time.time())
        diff_ts= end_ts - start_ts
        logmsg = self.build_log(5, self.app, diff_ts)
        self.log(logmsg)



    def get_parser(self):
        parser = OptionParser()
        parser.add_option('-a','--address',dest='address',help='Host or IP under test')
        parser.add_option('-p','--port',dest='port',help='TCP port under test')
        parser.add_option('-t','--timeout',dest='timeout',default='15',help='Timeout in seconds, zero for no timeout')
        parser.add_option('-i','--retry-interval',dest='retry',default=1,help='Retry interval in seconds.')
        parser.add_option('-q','--quiet',dest='quiet',action='store_false',help='Don\'t output any status messages')
        return parser

    def verify_options(self):
        if self.options.address is None:
            raise OptionException("The address must be set!")
        elif self.options.port is None:
            raise OptionException("The port must be set!")
        elif str(self.options.port).isnumeric() is False:
            raise OptionException("The value of port must be number!")
        elif str(self.options.retry).isnumeric() is False:
            raise OptionException("The value of port must be number!")
        elif int(self.options.retry) < 0:
            raise OptionException("The value of retry must be non-negative!")

    def start_up(self):
        try:
            parser = self.get_parser()
            self.options,self.args=parser.parse_args()
            self.verify_options()
            self.wait_for(self.options.address, int(self.options.port), int(self.options.timeout), int(self.options.retry))
        except OptionException as err:
            print(err)
            parser.print_help()
        except socket.timeout as err:
            logmsg = self.build_log(5, self.app, int(self.options.timeout))
            self.log(logmsg)
        except ConnectionRefusedError as err:
            logmsg = self.build_log(4, self.app)
            self.log(logmsg)

if __name__=='__main__':
    w=wait_for_app()
    w.start_up()

