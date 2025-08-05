from ctfsolver.src.ctfsolver import CTFSolver


def main():
    """
    Description :
        Calls the function via
        ```bash
        python -m ctfsolver.folders
        ```

        And creates the folders for the file
    """
    s = CTFSolver()
    s.create_parent_folder()


if __name__ == "__main__":
    main()
