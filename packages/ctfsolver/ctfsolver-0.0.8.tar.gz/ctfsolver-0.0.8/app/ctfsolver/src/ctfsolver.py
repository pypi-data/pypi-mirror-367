from .manager_file import ManagerFile
from .manager_connections import ManagerConnections
from .manager_crypto import ManagerCrypto


class CTFSolver(ManagerFile, ManagerConnections, ManagerCrypto):
    def __init__(self, *args, **kwargs) -> None:
        self.initializing_all_ancestors(*args, **kwargs)
        self.debug = kwargs.get("debug", False)

    def initializing_all_ancestors(self, *args, **kwargs):
        """
        Description:
            Initializes all the ancestors of the class
        """
        ManagerFile.__init__(self, *args, **kwargs)
        ManagerCrypto.__init__(self, *args, **kwargs)
        ManagerConnections.__init__(self, *args, **kwargs)

    def main(self):
        """
        Description:
            Placeholder for the main function
        """
        pass

    def __str__(self):
        """
        Description:
            Returns the string representation of the class, mainly the name of the parent folder

        Returns:
            _type_: _description_
        """
        return f"CTFSolver({self.parent})"


if __name__ == "__main__":
    s = CTFSolver()
