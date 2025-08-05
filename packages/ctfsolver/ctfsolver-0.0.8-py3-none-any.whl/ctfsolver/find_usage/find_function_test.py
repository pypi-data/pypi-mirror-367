from ..src.ctfsolver import CTFSolver


def find_function():
    """
    Description: This function is used to find the usage of the CTFSolver class in the current directory
    """
    solver = CTFSolver()
    search_string = "from ctfsolver import CTFSolver"
    exclude_dirs = ["app_venv", ".git"]
    current_directory = "."

    print(solver.get_self_functions())


if __name__ == "__main__":
    find_function()
