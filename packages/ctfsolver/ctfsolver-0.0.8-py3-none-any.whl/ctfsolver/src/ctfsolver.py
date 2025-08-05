from .manager_file import ManagerFile
from .manager_connections import ManagerConnections
from .manager_crypto import ManagerCrypto


class CTFSolver(ManagerFile, ManagerConnections, ManagerCrypto):
    def __init__(self, *args, **kwargs) -> None:
        self.initializing_all_ancestors(*args, **kwargs)
        self.debug = kwargs.get("debug", False)

    def initializing_all_ancestors(self, *args, **kwargs):
        ManagerFile.__init__(self, *args, **kwargs)
        ManagerCrypto.__init__(self, *args, **kwargs)
        ManagerConnections.__init__(self, *args, **kwargs)

    def main(self):
        pass

    def __str__(self):
        return f"CTFSolver({self.parent})"

    def __str__(self):
        return f"CTFSolver({self.parent})"


if __name__ == "__main__":
    s = CTFSolver()
