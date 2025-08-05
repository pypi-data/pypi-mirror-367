import pwn


class ManagerConnections:
    def __init__(self, *args, **kwargs) -> None:
        self.pwn = pwn

        self.url = kwargs.get("url")
        self.port = kwargs.get("port")
        self.conn_type = kwargs.get("conn")
        self.conn = None
        self.menu_num = None
        self.menu_text = None
        self.debug = kwargs.get("debug", False)

    def initiate_connection(self):
        """
        Description
            Shortcut to initialte the connection based on the self.conn_type (local or remote)
        """
        self.connect(self.conn_type)

    def connect(self, *args, **kwargs) -> None:
        """
        Description:
            Connects to the challenge based on the connection type.
            If the connection type is remote, it connects to the url and port provided.
            If the connection type is local, it starts a process with the file provided.


            local:
                kwargs :
                    argv: Any | None = None,
                    shell: bool = False,
                    executable: Any | None = None,
                    cwd: Any | None = None,
                    env: Any | None = None,
                    ignore_environ: Any | None = None,
                    stdin: int = PIPE,
                    stdout: PTY | int = PTY if not IS_WINDOWS else PIPE,
                    stderr: int = STDOUT,
                    close_fds: bool = True,
                    preexec_fn: Any = lambda : None,
                    raw: bool = True,
                    aslr: Any | None = None,
                    setuid: Any | None = None,
                    where: str = 'local',
                    display: Any | None = None,
                    alarm: Any | None = None,
                    creationflags: int = 0

        """
        if self.conn_type == "remote" and self.url and self.port:
            self.conn = self.pwn.remote(self.url, self.port)
        elif self.conn_type == "local" and self.file:
            self.conn = self.pwn.process(str(self.challenge_file), **kwargs)

    def recv_menu(self, number=1, display=False, save=False):
        """
        Depracated function. Use recv_lines instead.
        """
        raise DeprecationWarning("recv_menu is deprecated. Use recv_lines instead.")

    def recv_lines(self, number=1, display=False, save=False):
        """
        Description:
            Receives the output of the menu based on the number of lines provided.
            If display is True, it prints the output of everything received.
            If save is True, it saves the output in a list and returns it.

        Args:
            number (int, optional): Number of lines to receive . Defaults to 1.
            display (bool, optional): Displayes the lines received. Defaults to False.
            save (bool, optional): Saves the lines received to a list. Defaults to False.

        Returns:
            list: list of the lines received if save is True
        """
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

        # Sets up the menu options of the class instance
        if menu_num is None and self.menu_num is None:
            raise ValueError("Menu number not provided")

        if menu_num:
            self.menu_num = menu_num

        if menu_text is None and self.menu_text is None:
            raise ValueError("Menu text not provided")

        if menu_text:
            self.menu_text = menu_text

        return self.recv_send(
            choice,
            lines=self.menu_num,
            text_until=self.menu_text,
            display=display,
            save=save,
        )

    def recv_send(self, text, lines=None, text_until=None, display=False, save=False):
        """
        Description:
            Receives lines and sends a response.
            It can receive a number or lines, and/or specific text.
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

        if lines is None:
            lines = 0

        out_lines = self.recv_lines(number=lines, display=display, save=save)

        if save:
            result.extend(out_lines)

        if text_until:
            out_text_until = self.recv_until(text=text_until)

        if save:
            result.append(out_text_until)

        if display:
            print(out_text_until)

        self.send(text)

        if save:
            return result

    def send(self, text) -> None:
        """
        Description:
            Sends the text to the connection after it encodes it.
            Wrapper for self.conn.sendline(str(text).encode())

        Args:
            text (str): Text to send
        """
        # Check if the text is str or bytes and encode it
        self.conn.sendline(str(text).encode())

    def recv_until(self, text, **kwargs) -> bytes:
        """
        Description:
            Receive data until one of `delims`(text) provided is encountered. It encodes the text before sending it.
            Wrapper for self.conn.recvuntil(text.encode())
            Can also drop the ending if drop is True. If the request is not satisfied before ``timeout`` seconds pass, all data is buffered and an empty string (``''``) is returned.
        Args:
            text (str): Text to receive until
            **kwargs: Additional keyword arguments to pass to the recv
                - drop (bool, optional): Drop the ending.  If :const:`True` it is removed from the end of the return value. Defaults to False.
                - timeout (int, optional): Timeout in seconds. Defaults to default.

        Raises:
            exceptions.EOFError: The connection closed before the request could be satisfied

        Returns:
            A string containing bytes received from the socket,
            or ``''`` if a timeout occurred while waiting.

        """

        # Handles the connection closed before the request could be satisfied
        try:
            return self.conn.recvuntil(text.encode(), **kwargs)
        except EOFError:
            print("Connection closed before the request could be satisfied")
            return b""
