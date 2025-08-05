import Evtx.Evtx as evtx
from .manager_file import ManagerFile
from .manager_connections import ManagerConnections
from .manager_crypto import ManagerCrypto


class CTFSolver(ManagerFile, ManagerConnections, ManagerCrypto):
    def __init__(self, *args, **kwargs) -> None:
        self.initializing_all_ancestors(*args, **kwargs)
        self.debug = kwargs.get("debug", False)

    def initializing_all_ancestors(self, *args, **kwargs):
        # for i, ancestor in enumerate(self.__class__.mro()):
        #     if i == 0 or i == len(self.__class__.mro()) - 1:
        #         continue
        #     ancestor.__init__(self, *args, **kwargs)
        ManagerConnections.__init__(self, *args, **kwargs)
        ManagerFile.__init__(self, *args, **kwargs)
        ManagerCrypto.__init__(self, *args, **kwargs)

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
    s = CTFSolver()
    # s.main()
    # print(CTFSolver.mro())
