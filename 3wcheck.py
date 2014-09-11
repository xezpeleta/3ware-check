# /usr/bin/python

import sys
import logging
import subprocess
import shlex

logging.basicConfig(level=logging.INFO)
#logging.basicConfig(level=logging.DEBUG)


class Utils:
  @staticmethod
  def hardwareDetected():
    p1 = subprocess.Popen(shlex.split('lspci'),stdout=subprocess.PIPE)
    p2 = subprocess.Popen(shlex.split('grep -i 3ware'), stdin=p1.stdout,
                                                        stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    p1.stdout.close()
    out, err = p2.communicate()
    retcode = p2.returncode

    if retcode == 0:
      logging.debug('3ware hardware detected')
      return True
    else:
      logging.error('3ware hardware detection error ' + err)
      return False

  @staticmethod
  def softwareDetected():
    global twcli
    # Trying with tw-cli
    p = subprocess.Popen(shlex.split('whereis tw-cli'), stdout=subprocess.PIPE)
    out, err = p.communicate()
    retcode = p.returncode
    if len(out.split()) > 1:
      path = out.split()[1]
      if path != '':
        twcli = path
        logging.debug('3ware software detected: ' + path)
        return True
    else:
      # Trying with tw_cli
      p = subprocess.Popen(shlex.split('whereis tw_cli'), stdout=subprocess.PIPE)
      out, err = p.communicate()
      retcode = p.returncode
      if len(out.split()) > 1:
        path = out.split()[1]
        if path != '':
          twcli = path
          logging.debug('3ware software detected: ' + path)
          return True
    if twcli == '':
      logging.error('3ware software not detected: ' + path)

  @staticmethod
  def removeHeaders(output):
    if isinstance(output, str):
      output = output.split('\n')

    for index, line in enumerate(output):
      if line[0:4] == '----':
        output.pop(index)
        output.pop(index-1)
    return output

  @staticmethod
  def parseCommand(param):
    cmdoutput = []
    p = subprocess.Popen(shlex.split(twcli + ' ' + param), stdout=subprocess.PIPE)
    #logging.debug('Exec: twcli ' + param)
    out, err = p.communicate()
    retcode = p.returncode

    if retcode == 0:
      return out
    else:
      logging.error('ERROR: ' + str(err))

    return cmdoutput

class Raid:
  controllers = []

  #def __init__(self):
  #  self.controllers = getControllers()

  def getControllers(self):
    output = Utils.parseCommand('show')

    # Remove header and separator
    out = Utils.removeHeaders(output)
    #print out
    for line in out:
      if line is not '':
        cname = line.split()[0]
        if len(self.controllers) > 0:
          if self.getController(cname) is None:
            self.controllers.append(Raid.Controller(cname))
        else:
          self.controllers.append(Raid.Controller(cname))
    return self.controllers

    def getController(self, name):
      for c in self.controllers:
        if c.getName == name:
          return c

  class Controller:
    name = ''
    model = ''
    units = []

    def __init__(self, name):
      if self.name == '':
        self.name = name

    def getName(self):
      return self.name

    def getModel(self):
      if self.model == '':
        output = Utils.parseCommand('show')
        output = Utils.removeHeaders(output)
        for line in output:
          if line is not '':
            if len(line.split()) > 2:
              if line.split()[0] == self.name:
                self.model = line.split()[1]
      return self.model

    def getUnits(self):
      c = self
      output = Utils.parseCommand('/' + self.getName() + ' show')
      output = Utils.removeHeaders(output)
      # Get only Unit list
      for index,line in enumerate(output):
        if line is '':
          if len(output[:index]) > 0:
            output = output[:index]
      for line in output:
        if line is not '':
          uname = line.split()[0]
          if len(self.units) > 0:
            if self.getUnit(uname) is None:
              self.units.append(Raid.Controller.Unit(c, uname))
          else:
            self.units.append(Raid.Controller.Unit(c, uname))
      return self.units

    def getUnit(self, name):
      for u in self.units:
        if u.getName == name:
          return u

    class Unit:
      name = ''
      utype = ''
      status = ''
      size = 0 #GB
      ports = []
      controller = ''

      def __init__(self, c, uname):
        if self.name == '':
          self.name = uname
        if self.controller == '':
          self.controller = c.getName()
        if self.utype == '' and self.status == '' and self.size == 0:
          output = Utils.parseCommand('/' + self.controller + '/' + self.name + ' show')
          output = Utils.removeHeaders(output)
          for line in output:
            if len(line.split()) > 7:
              if line.split()[0] == self.name:
                self.utype = line.split()[1]
                self.status = line.split()[2]
                self.size = float(line.split()[7])
                logging.debug('Unit %s: Type=%s | Status=%s | Size=%i' % (self.name, self.utype, self.status, self.size))

      def getName(self):
        return self.name

      def getUtype(self):
        return self.utype

      def getStatus(self):
        return self.status

      def getSize(self):
        return self.size

      def getPorts(self):
        c = Raid.Controller(self.controller)
        output = Utils.parseCommand('/' + self.controller + ' show')
        output = Utils.removeHeaders(output)
        for line in output:
          if len(line.split()) > 2 and line.split()[2] == self.getName():
            pname = line.split()[0]
            if self.getPort(pname) is None:
              self.ports.append(Raid.Controller.Unit.Port(c, pname))
        return self.ports

      def getPort(self, name):
        for p in self.ports:
          if p.getName == name:
            return p

      class Port:
        name = ''
        status = ''
        size = 0
        serial = ''
        unit = ''
        controller = ''

        def __init__(self, c, pname):
          if self.name == '':
            self.name = pname
          if self.controller == '':
            self.controller = c.getName()
          if self.status == '' and self.size == 0 and self.serial == '' and self.unit == '':
            output = Utils.parseCommand('/' + self.controller + '/' + self.name + ' show')
            output = Utils.removeHeaders(output)
            for line in output:
              if line is not '':
                if len(line.split()) > 4 and line.split()[0] == self.name:
                  self.status = line.split()[1]
                  self.unit = line.split()[2]
                  self.size = float(line.split()[3])
                  self.serial = line.split()[6]
                  logging.debug('Port %s: Status=%s | Size=%i | Serial=%s | Unit=%s' % (self.name, self.status, self.size, self.serial, self.unit))

        def getName(self):
          return self.name

        def getStatus(self):
          return self.status

        def getSize(self):
          return self.size

        def getSerial(self):
          return self.serial

        def getUnit(self):
          return self.unit

        '''
          getReallocatedSectors()
            Returns reallocated sectors for the drive
            Compatible with 9650SE and higher
        '''
        def getReallocatedSectors(self):
          rasect = None
          pname = self.name
          output = Utils.parseCommand('/' + self.controller + '/' + pname + ' show rasect')
          if isinstance(output, str):
            rasect = int(output.split('=')[1].strip())
          else:
            rasect = False
          return rasect

        '''
          getPowerOnHours()
            Returns the number of power on hours for the drive
            Compatible with 9650SE and higher
        '''
        def getPowerOnHours(self):
          pohrs = 0
          pname = self.name
          output = Utils.parseCommand('/' + self.controller + '/' + pname + ' show pohrs')
          if isinstance(output, str):
            pohrs = int(output.split('=')[1].strip())
          else:
            pohrs = False
          return pohrs


twcli = None

def main():
  # Hardware detection
  if not Utils.hardwareDetected():
    print('ERROR: 3ware hardware not detected')
    sys.exit(1)

  # Software detection
  if not Utils.softwareDetected():
    print('ERROR: 3ware software not detected')
    sys.exit(2)

  # Raid controller detection
  r = Raid()
  controllers = r.getControllers()
  for c in controllers:
    units = c.getUnits()
    for u in units:
      ports = u.getPorts()
      status = 'ok'
      for p in ports:
        rasect = p.getReallocatedSectors()
        pohrs = p.getPowerOnHours()
        if rasect is False:
          status = 'unknown'
          print 'UNKNOWN: RAID not compatible'
          sys.exit(3)
        if rasect > 10:
          status = 'critical'
          print 'CRITICAL: Drive %s/%s/%s (Serial: %s | Size: %iGB) - Reallocated Sectors: %i' % (c.getName(), u.getName(), p.getName(), p.getSerial(), p.getSize(), rasect)
        elif rasect > 0:
          status = 'warning'
          print 'WARNING: Drive %s/%s/%s (Serial: %s | Size: %iGB) - Reallocated Sectors: %i' % (c.getName(), u.getName(), p.getName(), p.getSerial(), p.getSize(), rasect)
  if status == 'ok':
    print 'OK'

if __name__ == "__main__":
  main()
