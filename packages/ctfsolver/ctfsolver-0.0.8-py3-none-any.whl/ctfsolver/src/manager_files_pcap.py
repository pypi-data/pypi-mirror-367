from scapy.all import rdpcap


class ManagerFilePcap:
    def __init__(self, *args, **kwargs):
        pass

    def initializing_all_ancestors(self, *args, **kwargs):
        """
        Description:
            Initializes all the ancestors of the class
        """

    def pcap_open(self, file=None, save=False):
        """
        Description:
            Open the pcap file with scapy and saves it in self.packets

        Args:
            file (Path, optional): File to open. Defaults to None.
            save (bool, optional): Save the output. Defaults to False.

        """

        if file is None:
            file = self.challenge_file

        self.packets = rdpcap(file.as_posix())

        if save:
            return self.packets

    def searching_text_in_packets(self, text, packets=None, display=False):
        """
        Description:
        Search for a text in the packets that have been opened with scapy

        Args:
            text (str): Text to search in the packets
            packets (list, optional): List of packets to search in. Defaults to None.
            display (bool, optional): Display the packet if the text is found. Defaults to False.

        Returns:
            str: Text found in the packet if found
        """

        if packets is None:
            packets = self.packets

        for i, packet in enumerate(packets):
            if packet.haslayer("Raw"):
                if text.encode() in packet["Raw"].load:
                    if display:
                        print(f"Found {text} in packet {i}")
                        print(packet.show())
                        print(packet.summary())
                    return packet["Raw"].load.decode("utf-8")
