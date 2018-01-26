#!/usr/bin/env python

# MIT License
# 
# Copyright (c) 2018 Dan Persons (dpersonsdev@gmail.com)
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from ldsiparser import __version__
import ldsiparser.parse
import sys
import os.path
from argparse import ArgumentParser
from configparser import ConfigParser
from threading import Thread


class ParseCore:

    def __init__(self, standalone=True, conf=None):
        """Initialize live parser"""

        self.standalone = standalone
        self.conf = conf
        self.args = None
        self.arg_parser = ArgumentParser()

        self.db = {}
        self.threads = []


    def get_args(self):
        """Set argument options"""

        self.arg_parser.add_argument('--version', action = 'version',
                version = '%(prog)s ' + str(__version__))
        self.arg_parser.add_argument('-c',
                action = 'store', dest = 'config',
                default = 'config/parser.conf',
                help = ('set the config file'))

        self.args = self.arg_parser.parse_args()


    def get_config(self):
        """Read the config file"""

        config = ConfigParser()
        if self.standalone:
            if os.path.isfile(self.args.config):
                myconf = self.args.config
            else: myconf = 'config/parser.conf'
        else:
            if os.path.isfile(self.conf):
                myconf = self.conf
            else: myconf = 'config/parser.conf'
        config.read(myconf)

        self.plist = []

        self.db['dbfile'] = config.get('database', 'dbfile')
        
        for sec in config.sections():
            if sec != 'database':
                p = {}
                p['filename'] = config.get(sec, 'filename')
                try:
                    p['parser'] = config.get(sec, 'parser')
                except Exception:
                    p['parser'] = 'syslogbsd'
                #p['helpers'] = config.get(sec, 'helpers')
                self.plist.append(p)


    def run_parse(self, conf=None):
        try:
            if self.standalone:
                self.get_args()
            self.get_config()
            for entry in self.plist:
                thread = Thread(name=parse,
                        target=ldsiparser.parse.start_parse,
                        args=(self.db, entry))
                thread.daemon = True
                thread.start()
                self.threads.append(thread)

                while True:
                    sleep(3600)

        except KeyboardInterrupt:
            pass
        # except Exception as err:
        #     print('Error: ' + str(err))


    
def parse(conffile='config/parser.conf'):
    parser = ParseCore(standalone=False, conf=conffile)
    parser.run_parse()
