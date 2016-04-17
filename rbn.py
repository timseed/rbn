import telnetlib
import re
from dxcc import dxcc_all, dxcc
from itertools import product
import logging
import collections



class HamBand(object):
    """
    COnvert from Khz to Meters in Ham Speak terms not literally
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.Band = [160, 80, 60, 40, 30, 20, 18, 15, 12, 10]
        self.ContestBand = [80, 40, 20, 15, 10]
        self.Freq = [(1800, 2000),
                     (3500, 4000),
                     (5000, 5100),
                     (7000, 7300),
                     (10100, 10150),
                     (14000, 14350),
                     (18068, 18168),
                     (21000, 21450),
                     (24890, 24990),
                     (2800, 29700)]
        self._band_plan = list(zip(self.Band, self.Freq))

    def M(self, Khz):
        '''
        Convert Khz to Meters
        :return: String in Meters
        '''

        Khz = float(Khz)
        Khz = int(Khz)

        rv = None
        for b in self._band_plan:
            if Khz >= b[1][0] and Khz <= b[1][1]:
                rv = b[0]
                break
        return rv

    def Index(self, M):
        "Return the INDEX of the Band"
        if M in self.Band:
            return self.Band.index(M)
        else:
            return -1


class RBFields:
    filler1, filler2, skimmer, freq, dx, mode, sn, filler3, wpm, filler4, msg, when = range(12)


class telnet3(telnetlib.Telnet):
    def read_until(self, expected, timeout=None):
        expected = bytes(expected, encoding='utf-8')
        received = super(telnet3, self).read_until(expected, timeout)
        logging.info('read_util length =' + str(len(received)))
        logging.info('data=>' + str(received, encoding='utf-8'))
        return str(received, encoding='utf-8')

    def write(self, buffer):
        logging.info('write data =>' + buffer + '<=')
        buffer = bytes(buffer, encoding='utf-8')
        super(telnet3, self).write(buffer)

    def expect(self, list, timeout=None):
        for index, item in enumerate(list):
            list[index] = bytes(item, encoding='utf-8')
        match_index, match_object, match_text = super(telnet3, self).expect(list, timeout)
        return match_index, match_object, str(match_text, encoding='utf-8')


class rbn(object):

    rbn_tup=collections.namedtuple('rbn_tup','Skimmer Call Country Freq Band SigLevel')

    def __init__(self, node="telnet.reversebeacon.net", port="7000", username='A45WG', password=None, mode_filter='CW'):
        self.logger = logging.getLogger(__name__)
        self._bandplans = HamBand()
        self._dxcclist = dxcc_all()
        self._dxcclist.read()
        self._node = node
        self._port = port
        self._username = username
        self._password = password
        self._mode_filter = mode_filter
        try:
            self._tn = telnet3(self._node, self._port)
            self._tn.read_until("Please enter your call: ")
            self._tn.write(self._username + "\n")
            self._tn.read_until("\r")
            self.logger.info("logged in")
            if self._password is not None:
                self._tn.read_until("Password: ")
                self._tn.write(self._password + "\n")
            self.logger.info("logged in")
            self.logger.info("rbn class initialized")
        except Exception as e:
            self.logger.error('There has been an error starting rbn {}'.format(str(e)))

    def process_line(self, multi_line):
        """
        Break the Telnet RBN Line into Fields so we can process them easier
        :param multi_line:
        :return:
        """
        self.logger.info("process_line")
        spots = []
        for line in multi_line.split('\n'):
            try:
                fields = [a.upper() for a in re.sub('[\s]+', ' ', line).split(' ')]
                if fields[RBFields.mode] == self._mode_filter:
                    M = self._bandplans.M(fields[RBFields.freq])
                    #
                    # Find the Country
                    #
                    dx_ctry = self._dxcclist.find(fields[RBFields.dx])
                    if dx_ctry is not None:
                        self.logger.debug('' + fields[RBFields.dx] + ' ' + dx_ctry.Country_Name() + ' ' + fields[
                            RBFields.freq] + ' ' + str(M))
                        next_beacon = rbn.rbn_tup(fields[RBFields.skimmer],
                                       fields[RBFields.dx],
                                       dx_ctry.Country_Name(),
                                       fields[RBFields.freq],
                                       str(M),
                                       fields[RBFields.sn])
                        spots.append(next_beacon)
                    else:
                        self.logger.debug('' + fields[RBFields.dx] + ' UNK ' + fields[RBFields.freq] + ' ' + str(M))
                        next_beacon = rbn.rbn_tup(fields[RBFields.skimmer],
                                                  fields[RBFields.dx],
                                                  'UNK',
                                                  fields[RBFields.freq],
                                                  str(M),
                                                  fields[RBFields.sn]
                                                  )
                        spots.append(next_beacon)
            except IndexError:
                pass
        return spots

    def loop(self, lines=10):
        """
        Get n posts from the RBN Network
        :param lines:
        :return:
        """
        self.logger.info("running loop")
        while lines > 0:
            a = self._tn.read_until('ZZZ', 1)
            if len(a) > 0:
                self.logger.info("Got some data")
                # print(''+a,end='')
                self.process_line(a)
            else:
                self.logger.warning('No Data received')
            lines = lines - 1


if __name__ == "__main__":
    r = rbn()
    r.loop()
    wc = WorkedCountries()
    cc = ContestCountries()
