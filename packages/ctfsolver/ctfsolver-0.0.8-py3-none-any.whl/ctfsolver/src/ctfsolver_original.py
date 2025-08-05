from pathlib import Path
import pwn
import inspect
from scapy.all import rdpcap
import Evtx.Evtx as evtx
import re
import base64


class CTFSolver:
    def __init__(self, *args, **kwargs) -> None:
        self.pwn = pwn
        self.Path = Path
        self.get_parent()

        self.file = kwargs.get("file")
        self.get_challenge_file()
        self.url = kwargs.get("url")
        self.port = kwargs.get("port")
        self.conn_type = kwargs.get("conn")
        self.conn = None
        self.menu_num = None
        self.menu_text = None
        self.debug = kwargs.get("debug", False)
        # self.initiate_connection()

    def initiate_connection(self):
        self.connect(self.conn_type)

    def create_parent_folder(self):
        """ """

        self.folder_data = Path(self.parent, "data")
        self.folder_files = Path(self.parent, "files")
        self.folder_payloads = Path(self.parent, "payloads")

        folder_list = [
            self.folder_payloads,
            self.folder_data,
            self.folder_files,
        ]

        for folder in folder_list:
            if not folder.exists():
                folder.mkdir()

    def get_parent(self):
        """
        Description:
        Create object for the class for parent, payloads, data and files folder paths for the challenge
        """
        self.parent = None
        self.folder_payloads = None
        self.folder_data = None
        self.folder_files = None

        self.file_called_frame = inspect.stack()
        self.file_called_path = Path(self.file_called_frame[-1].filename)
        self.parent = Path(self.file_called_path).parent

        if self.parent.name == "payloads":
            self.folder_payloads = self.parent
            self.parent = self.parent.parent
        self.folder_data = Path(self.parent, "data")
        self.folder_files = Path(self.parent, "files")
        self.folder_payloads = Path(self.parent, "payloads")

    def prepare_space(self, files=None, folder=None, test_text="picoCTF{test}"):
        """
        Description:
        Prepare the space for the challenge by creating the folders if they don't exist
        """
        files = files if files else []
        folder = folder if folder else self.folder_files

        for file in files:
            if not Path(folder, file).exists():
                with open(Path(folder, file), "w") as f:
                    f.write(test_text)

    def get_challenge_file(self):
        if self.file and self.folder_data:
            self.challenge_file = Path(self.folder_files, self.file)
        elif not self.folder_data:
            if self.debug:
                print("Data folder not found")

    def connect(self, *args, **kwargs) -> None:
        if self.conn_type == "remote" and self.url and self.port:
            self.conn = pwn.remote(self.url, self.port)
        elif self.conn_type == "local" and self.file:
            self.conn = pwn.process(str(self.challenge_file))

    def recv_menu(self, number=1, display=False, save=False):
        if save:
            result = []
        for _ in range(number):
            out = self.conn.recvline()
            if display:
                print(out)
            if save:
                result.append(out)
        if save:
            return result

    def send_menu(
        self, choice, menu_num=None, menu_text=None, display=False, save=False
    ):
        """
        Description:
            Gets the menu num either from the class or from the function call and saves it to the class.
            Gets the menu text that the menu is providing, receives until the menu asks for choice and then send out the choice.
            If save is True, it saves the output of the menu in a list and returns it.
            If display is True, it prints the output of everything received.

        Args:
            choice (int or str): Choice to send to the menu
            menu_num (int, optional): Number of options printed in the menu. Defaults to None.
            menu_text (str, optional): Text that the menu asks before sending your choice. Defaults to None.
            display (bool, optional): Variable to print every received line. Defaults to False.
            save (bool, optional): . Defaults to False.
        Returns:
            list: List of output of the menu if save is True
        """
        if save:
            result = []
        if menu_num is None and self.menu_num is None:
            raise ValueError("Menu number not provided")

        if menu_num:
            self.menu_num = menu_num

        if menu_text is None and self.menu_text is None:
            raise ValueError("Menu text not provided")

        if menu_text:
            self.menu_text = menu_text

        out = self.recv_menu(number=self.menu_num, display=display, save=save)
        if save:
            result.extend(out)

        out = self.conn.recvuntil(self.menu_text.encode())
        if save:
            result.append(out)

        if display:
            print(out)

        self.conn.sendline(str(choice).encode())

        if save:
            return result

    def pcap_open(self, file=None):
        """
        Description:
        Open the pcap file with scapy and saves it in self.packets
        """

        if not file:
            file = self.challenge_file

        self.packets = rdpcap(file.as_posix())

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

        if not packets:
            packets = self.packets

        for i, packet in enumerate(packets):
            if packet.haslayer("Raw"):
                if text.encode() in packet["Raw"].load:
                    if display:
                        print(f"Found {text} in packet {i}")
                        print(packet.show())
                        print(packet.summary())
                    return packet["Raw"].load.decode("utf-8")

    def decode_base64(self, text):
        """
        Description:
        Decode the base64 text

        Args:
            text (str): Base64 encoded text

        Returns:
            str: Decoded text
        """
        try:
            return base64.b64decode(text).decode("utf-8")
        except Exception as e:
            print(e)
            return None

    def re_match_base64_string(self, text, strict=False):
        """
        Description:
        Find the base64 string in the text

        Args:
            text (str): Text to search for base64 string
            strict (bool, optional): If True, it will only return the base64 string. Defaults to False.

        Returns:
            str: list of Base64 string found in the text
        """
        if strict:
            base64_pattern = r"[A-Za-z0-9+/]{4,}={1,2}"
        else:
            base64_pattern = r"[A-Za-z0-9+/]{4,}={0,2}"
        base64_strings = re.findall(base64_pattern, text)
        return base64_strings

    def re_match_flag(self, text, origin):
        """
        Description:
        Find the flag in the text

        Args:
            text (str): Text to search for the flag
            origin (str): Origin of the flag

        Returns:
            str: list of flag found in the text
        """
        flag_pattern = rf"{origin}{{[A-Za-z0-9_]+}}"
        return re.findall(flag_pattern, text)

    def re_match_partial_flag(self, text, origin):
        """
        Description:
        Find the flag in the text or partial flag

        Args:
            text (str): Text to search for the flag
            origin (str): Origin of the flag

        Returns:
            str: list of flag found in the text
        """
        flag_pattern = rf"({origin}{{[^ ]*|[^ ]*}})"
        return re.findall(flag_pattern, text)

    def search_for_pattern_in_file(
        self, file, func=None, display=False, save=False, *args, **kwargs
    ):
        """
        Description:
        Search for a pattern in the file and return the output

        Args:
            file (str): File to search for the pattern
            func (function, optional): Function to search for the pattern. Defaults to None.
            display (bool, optional): Display the output. Defaults to False.
            save (bool, optional): Save the output. Defaults to False.

        Returns:
            list: List of output if save is True

        """
        if save:
            output = []
        if func is None:
            return None

        with open(file, "r") as f:
            for line in f:
                result = func(line, *args, **kwargs)
                if result is not None:
                    if display:
                        print(result)
                    if save:
                        output.extend(result)
        if save:
            return output

    def search_for_base64(self, file, *args, **kwargs):
        """
        Description:
        Search for base64 string in the file

        Args:
            file (str): File to search for the base64 string
            display (bool, optional): Display the output. Defaults to False.
            save (bool, optional): Save the output. Defaults to False.

        Returns:
            list: List of output if save is True
        """
        display = kwargs.get("display", False)
        save = kwargs.get("save", False)
        strict = kwargs.get("strict", False)

        out = self.search_for_pattern_in_file(
            file, self.re_match_base64_string, display=display, save=save, strict=strict
        )
        if display:
            print(out)
        if save:
            return out

    def exec_on_files(self, folder, func, *args, **kwargs):
        """
        Description:
        Execute a function on all the files in the folder with the arguments provided

        Args:
            folder (str): Folder to execute the function
            func (function): Function to execute

        Returns:
            list: List of output of the function
        """

        save = kwargs.get("save", False)
        display = kwargs.get("display", False)
        if save:
            output = []
        for file in folder.iterdir():
            out = func(file, *args, **kwargs)
            if save and out is not None:
                output.extend(out)
            if display and out is not None:
                print(out)
        if save:
            return output

    def main(self):
        pass

    # def __del__(self):
    #     self.conn.close()

    # def __exit__(self, exc_type, exc_value, traceback):
    #     self.conn.close()

    # Todo
    # Add cryptography solutions
    # Add web solutions

    def __str__(self):
        return f"CTFSolver({self.parent})"


if __name__ == "__main__":
    s = CTFSolver(conn="remote")
    s.main()
