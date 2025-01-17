import asyncio
import subprocess
import logging
import os

from configparser import ConfigParser

C = ConfigParser()
C.read('.ugitstat')

class uGitServerProtocol:
    def get_git_log(self):
        git = subprocess.check_output(['git', 'log', '--oneline', '-1'])
        return git.decode('utf-8').split(' ', 1)[0]

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        message = data.decode('utf-8')
        data = 'GIT ' + self.get_git_log()
        logging.debug('Received %r from %s' % (message, addr))
        logging.debug('Send %r to %s' % ('GIT ' + self.get_git_log(), addr))
        self.transport.sendto(data.encode('utf-8'), addr)


if __name__ == '__main__':
    os.chdir(C['server'].get('repository', '.'))
    logging.basicConfig(format='%(asctime)s %(message)s', level = int(C['server']['logging']))
    loop = asyncio.new_event_loop()
    logging.info("Starting uGitStat UDP server")
    listen = loop.create_datagram_endpoint(
        uGitServerProtocol, local_addr=(C['server']['host'], 19798))
    transport, protocol = loop.run_until_complete(listen)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    transport.close()
    loop.close()