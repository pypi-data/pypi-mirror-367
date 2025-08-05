from ctfsolver.src.ctfsolver import CTFSolver


def find_usage():
    """
    Description: This function is used to find the usage of the CTFSolver class in the current directory
    """
    solver = CTFSolver()
    search_string = "from ctfsolver import CTFSolver"
    exclude_dirs = ["app_venv", ".git"]
    current_directory = "."

    try:

        solver.search_files(
            directory=current_directory,
            exclude_dirs=exclude_dirs,
            search_string=search_string,
            display=True,
        )
    except KeyboardInterrupt as k:
        print("Stopping the search")
    except Exception as e:
        print(e)


if __name__ == "__main__":

    find_usage()
