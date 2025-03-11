from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.cli import CLI

class MyTopo(Topo):
    def build(self):
        # Add Hosts
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        h4 = self.addHost('h4')
        h5 = self.addHost('h5')
        h6 = self.addHost('h6')
        h7 = self.addHost('h7')

        # Add Switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')

        # Add Links with Bandwidth Constraints
        self.addLink(s1, s2, bw=100)  # 100 Mbps
        self.addLink(s2, s3, bw=50, loss=1)  # 50 Mbps + 1% loss
        self.addLink(s3, s4, bw=100)  # 100 Mbps

        # Connect Hosts
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s2)
        self.addLink(h4, s3)
        self.addLink(h5, s3)
        self.addLink(h6, s4)
        self.addLink(h7, s4)

topo = MyTopo()
net = Mininet(topo=topo, link=TCLink)
net.start()
CLI(net)
net.stop()
