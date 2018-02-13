#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.cli import CLI
from mininet.node import RemoteController


class part4_topo(Topo):

  def build(self):

    h10 = self.addHost('h10', mac='00:00:00:00:00:01', ip='10.0.1.10/24', defaultRoute='h10-eth0')
    h20 = self.addHost('h20', mac='00:00:00:00:00:02', ip='10.0.2.20/24', defaultRoute='h20-eth0')
    h30 = self.addHost('h30', mac='00:00:00:00:00:03', ip='10.0.3.30/24', defaultRoute='h30-eth0')

    s1 = self.addSwitch('s1')
    s2 = self.addSwitch('s2')
    s3 = self.addSwitch('s3')

    serv1 = self.addHost('serv1', mac='00:00:00:00:00:04', ip='10.0.4.10/24', defaultRoute='serv1-eth0')
    hnotrust = self.addHost('hnotrust', mac='00:00:00:00:00:05', ip='172.16.10.100/24', defaultRoute='hnotrust-eth0')

    cores21 = self.addSwitch('cores21')
    dcs31 = self.addSwitch('dcs31')

    self.addLink(h10, s1)
    self.addLink(h20, s2)
    self.addLink(h30, s3)

    self.addLink(dcs31, serv1)

    self.addLink(cores21, s1, 		port1=1)
    self.addLink(cores21, s2, 		port1=2)
    self.addLink(cores21, s3, 		port1=3)
    self.addLink(cores21, hnotrust, port1=4)
    self.addLink(cores21, dcs31, 	port1=5)


topos = {'part4' : part4_topo}


def configure():

  topo = part4_topo()
  net = Mininet(topo=topo, controller=RemoteController)
  net.start()
  CLI(net)
  net.stop()


if __name__ == '__main__':
  configure()
