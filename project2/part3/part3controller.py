# Part 3 of UWCSE's Project 3
#
# based on Lab Final from UCSC's Networking Class
# which is based on of_tutorial by James McCauley

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import IPAddr, IPAddr6, EthAddr

log = core.getLogger()

#statically allocate a routing table for hosts
#MACs used only in part 4
IPS = {
  "h10" : ("10.0.1.10", '00:00:00:00:00:01'),
  "h20" : ("10.0.2.20", '00:00:00:00:00:02'),
  "h30" : ("10.0.3.30", '00:00:00:00:00:03'),
  "serv1" : ("10.0.4.10", '00:00:00:00:00:04'),
  "hnotrust" : ("172.16.10.100", '00:00:00:00:00:05'),
}
"""
MACTOIP = {
  '00:00:00:00:00:01' : "10.0.1.10",
  '00:00:00:00:00:02' : "10.0.2.20",
  '00:00:00:00:00:03' : "10.0.3.30",
  '00:00:00:00:00:04' : "10.0.4.10",
  '00:00:00:00:00:05' : "172.16.10.100",
}

IPPort{}
"""
class Part3Controller (object):
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
	#fm = of.ofp_flow_mod()
	#fm.match.dl_type = 0x0800
	#fm.match.nw_proto = 1
	#fm.match.nw_src = IPS['hnotrust'][0]
	#self.connection.send(fm)
	
	        
        fmh10 = of.ofp_flow_mod()
        fmh10.match.dl_type = 0x0800
        fmh10.match.nw_src = IPS['h10'][0]
        fmh10.actions.append(of.ofp_action_output(port = 1))
        self.connection.send(fmh10)

        fmh20 = of.ofp_flow_mod()
        fmh20.match.dl_type = 0x0800
        fmh20.match.nw_src = IPS['h20'][0]
        fmh20.actions.append(of.ofp_action_output(port = 2))
        self.connection.send(fmh20)

        fmh30 = of.ofp_flow_mod()
        fmh30.match.dl_type = 0x0800
        fmh30.match.nw_src = IPS['h30'][0]
        fmh30.actions.append(of.ofp_action_output(port = 3))
        self.connection.send(fmh30)

        fmhserv1 = of.ofp_flow_mod()
        fmhserv1.match.dl_type = 0x0800
        fmhserv1.match.nw_src = IPS['serv1'][0]
        fmhserv1.actions.append(of.ofp_action_output(port = 55))
        self.connection.send(fmhserv1)

        fmhhnotrust = of.ofp_flow_mod()
        fmhhnotrust.match.dl_type = 0x0800
        fmhhnotrust.match.new_src = IPS['hnotrust'][0]
        #fmhhnotrust.actions.append(of.ofp_action_output(port = 4))
        self.connection.send(fmhhnotrust)
	

	self.allow_all()

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
  def resend_packet(self, packet_in, out_port):
    msg = of.ofp_packet_out()
    msg.data = packet_in
    action = of.ofp_action_output(port = out_port)
    msg.actions.append(action)
    self.connection.send(msg)

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
    print ("Unhandled packet from " + str(self.connection.dpid) + ":" + packet.dump())

def launch ():
  """
  Starts the component
  """
  def start_switch (event):
    log.debug("Controlling %s" % (event.connection,))
    Part3Controller(event.connection)
  core.openflow.addListenerByName("ConnectionUp", start_switch)
