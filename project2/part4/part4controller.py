# Part 4 of UWCSE's Project 3
#
# based on Lab Final from UCSC's Networking Class
# which is based on of_tutorial by James McCauley

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import IPAddr, IPAddr6, EthAddr

from pox.lib.packet.ipv4 import ipv4

from pox.lib.packet.arp import arp
from pox.lib.packet.ethernet import ethernet

log = core.getLogger()


#statically allocate a routing table for hosts
#MACs used only in part 4
IPS = {
  "h10" : ("10.0.1.10", '00:00:00:00:00:01', 1),
  "h20" : ("10.0.2.20", '00:00:00:00:00:02', 2),
  "h30" : ("10.0.3.30", '00:00:00:00:00:03', 3),
  "hnotrust" : ("172.16.10.100", '00:00:00:00:00:05', 4),
  "serv1" : ("10.0.4.10", '00:00:00:00:00:04', 5),
}

IPREST = {
  "10.0.1.10": ('00:00:00:00:00:01', 1),
  "10.0.2.20": ('00:00:00:00:00:02', 2),
  "10.0.3.30": ('00:00:00:00:00:03', 3),
  "172.16.10.100": ('00:00:00:00:00:05', 4),
  "10.0.4.10": ('00:00:00:00:00:04', 5),
}


IPROUTER = {
  "10.0.1.10" : "10.0.1.1",
  "10.0.2.20" : "10.0.2.2",
  "10.0.3.30" : "10.0.3.3",
  "172.16.10.100" : "172.16.10.10",
  "10.0.4.10": "10.0.4.1",

}


'''
def ip_to_mac(ip):
    for entry in IPS:
        print "testing entry", entry
        if IPS[entry][0] == ip:
            return entry[3]
    print "could not match ip", ip
'''

class Part4Controller (object):
  """
  A Connection object for that switch is passed to the __init__ function.
  """
  def __init__ (self, connection):
    print (connection.dpid)
    # Keep track of the connection to the switch so that we can
    # send it messages!
    self.connection = connection

    # This binds our PacketIn event listener
    connection.addListeners(self)
    #use the dpid to figure out what switch is being created
    if (connection.dpid == 1):
      self.s1_setup()
    elif (connection.dpid == 2):
      self.s2_setup()
    elif (connection.dpid == 3):
      self.s3_setup()
    elif (connection.dpid == 21):
      self.cores21_setup()
    elif (connection.dpid == 31):
      self.dcs31_setup()
    else:
      print ("UNKNOWN SWITCH")
      exit(1)

	#core.openflow.addListenerByName("PacketIn", self._handle_PacketIn)


  def allow_all(self):
	fm = of.ofp_flow_mod()
	fm.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
	self.connection.send(fm)


  def s1_setup(self):
	self.allow_all()

  def s2_setup(self):
	self.allow_all()

  def s3_setup(self):
	self.allow_all()
  

  def cores21_setup(self):

    # drop ICMP packets from hnotrust
    fm = of.ofp_flow_mod()
    fm.match.dl_type = 0x0800
    fm.match.nw_proto = 1
    fm.match.nw_src = IPS['hnotrust'][0]
    self.connection.send(fm)
    	
    # --- direct IP packets --- #
    '''
    self.setup_ip_flow_mod('h10')
    self.setup_ip_flow_mod('h20')
    self.setup_ip_flow_mod('h30')
    self.setup_ip_flow_mod('hnotrust')
    self.setup_ip_flow_mod('serv1')
    '''
    # --- respond to ARPs --- #
    '''
    self.setup_arp_flow_mod('h10')
    self.setup_arp_flow_mod('h20')
    self.setup_arp_flow_mod('h30')
    self.setup_arp_flow_mod('hnotrust')
    self.setup_arp_flow_mod('serv1')
    '''
    
    #self.allow_all()


  def setup_ip_flow_mod(self, dst):

	fm = of.ofp_flow_mod()
	fm.match.dl_type = 0x0800
	fm.match.nw_dst = IPS[dst][0]
	fm.actions.append(of.ofp_action_output(port=IPS[dst][2]))
        fm.actions.append(of.ofp_action_dl_addr.set_dst(EthAddr(IPS[dst][1])))
	fm.actions.append(of.ofp_action_dl_addr.set_src(EthAddr("00:00:00:00:00:07")))
	#fm.actions.append(of.ofp_action_nw_addr.set_src(IPROUTER[str(IPS[dst][0])]))
	self.connection.send(fm)


  def setup_arp_flow_mod(self, dst):

    fm = of.ofp_flow_mod()
    fm.match.dl_type = 0x0806
    fm.match.nw_dst = IPS[dst][0]
    fm.actions.append(of.ofp_action_nw_addr.set_dst(IPS[dst][0]))
    fm.actions.append(of.ofp_action_dl_addr.set_dst(IPS[dst][1]))
    self.connection.send(fm)


  def dcs31_setup(self):

    # drop IP packets from hnotrust
	fm = of.ofp_flow_mod()
	fm.match.dl_type = 0x0800
	fm.match.nw_src = IPS['hnotrust'][0]
	self.connection.send(fm)

	self.allow_all()

	
  #used in part 4 to handle individual ARP packets
  #not needed for part 3 (USE RULES!)
  #causes the switch to output packet_in on out_port
  #def resend_packet(self, packet_in, out_port):
    #msg = of.ofp_packet_out()
	#r = arp()
	#r.opcode = arp.REPLY
    #msg.data = packet_in
    #action = of.ofp_action_output(port = out_port)
    #msg.actions.append(action)
    #self.connection.send(msg)

  def _handle_PacketIn (self, event):
    """
    Packets not handled by the router rules will be
    forwarded to this method to be handled by the controller
    """

    packet = event.parsed # This is the parsed packet data.
    if not packet.parsed:
      log.warning("Ignoring incomplete packet")
      return
    packet_in = event.ofp # The actual ofp_packet_in message.
    
    # this is incomplete and probably wrong; read at your own risk
    print "handling packet", packet
    match = of.ofp_match.from_packet(packet)
    matchip = of.ofp_match.from_packet(packet)
    if ( packet.type == ethernet.IP_TYPE): #and matchip.dl_src == EthAddr("00:00:00:00:00:07")) :
	r = ipv4()
	r.hwsrc = EthAddr("00:00:00:00:00:07")
	r.hwdst = EthAddr(IPREST[str(packet.payload.src)][0])
	r.protosrc = IPROUTER[str(packet.payload.protodst)]
	r.protodst = packet.payload.protodst
	print "mac src", r.hwsrc
	print "mac dst", r.hwdst
	print "ip src", r.protosrc
	print "ip dst", r.protodst
	e = ethernet(type=packet.IP_TYPE, src=r.hwsrc,dst=r.hwdst)
	e.set_payload(r)
	msg = of.ofp_packet_out()
	msg.data = e.pack()
	msg.actions.append(of.ofp_action_output(port = IPREST[str(packet.src)][1]))
	self.connection.send(msg)
    elif ( match.dl_type == packet.ARP_TYPE and match.nw_proto == arp.REQUEST):
        print "generating response"
        reply = arp()
        reply.opcode = arp.REPLY
        reply.hwdst = packet.src#match.dl_src
        print "dl_dst", #match.dl_dst
	print "protosrc" , packet.payload.protosrc
   	print "ip router", IPROUTER[str(packet.payload.protosrc)]
	reply.protosrc = IPAddr(IPROUTER[str(packet.payload.protosrc)])#IPAddr("10.0.1.1")
        reply.protodst = packet.payload.protosrc#match.nw_src
        reply.hwsrc = EthAddr("00:00:00:00:00:07")
        e = ethernet(type=packet.ARP_TYPE, src=reply.hwsrc, dst=reply.hwdst)
        e.set_payload(reply)
        msg = of.ofp_packet_out()
        msg.data = e.pack()
        #print "msg", msg
        msg.actions.append(of.ofp_action_output(port = of.OFPP_IN_PORT))
        #print "out port",
	msg.in_port = event.port
        event.connection.send(msg)
    
    #resend_packet(packet_in, packet_in.in_port)
    #print ("Unhandled packet from " + str(self.connection.dpid) + ":" + packet.dump())


def launch ():
  """
  Starts the component
  """
  def start_switch (event):
    log.debug("Controlling %s" % (event.connection,))
    Part4Controller(event.connection)
  core.openflow.addListenerByName("ConnectionUp", start_switch)
