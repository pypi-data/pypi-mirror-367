from pathlib import Path
import inspect
import os
import ast
from .manager_files_pcap import ManagerFilePcap


class ManagerFile(ManagerFilePcap):
    def __init__(self, *args, **kwargs):
        self.Path = Path
        self.file = kwargs.get("file")
        self.debug = kwargs.get("debug", False)
        self.folders_name_list = kwargs.get("folders_name_list", None)
        self.folders_names_must = ["data", "files", "payloads"]
        self.setup_named_folder_list()
        self.get_parent()
        self.setup_named_folders()
        self.get_challenge_file()

    def initializing_all_ancestors(self, *args, **kwargs):
        """
        Description:
            Initializes all the ancestors of the class
        """
        ManagerFilePcap.__init__(self, *args, **kwargs)

    def get_parent(self):
        """
        Description:
            Get the parent folder of the file that called the class
        """
        self.parent = None

        self.file_called_frame = inspect.stack()
        self.file_called_path = Path(self.file_called_frame[-1].filename)
        self.parent = Path(self.file_called_path).parent.resolve()

        if self.parent.name in self.folders_name_list:
            self.parent = self.parent.parent

    def setup_named_folder_list(self):
        """
        Description:
        Setup the main named folder list. If the user has provided a list, add the must folders to it
        """
        if self.folders_name_list is None:
            self.folders_name_list = self.folders_names_must
        elif len(self.folders_name_list) > 1:
            self.folders_name_list.extend(self.folders_names_must)
            self.folders_name_list = list(set(self.folders_name_list))

    def setup_named_folders(self):
        """
        Description:
        Create folders for the challenge. (data, files, payloads)
        """

        self.folder_payloads = None
        self.folder_data = None
        self.folder_files = None

        self.folder_data = Path(self.parent, "data")
        self.folder_files = Path(self.parent, "files")
        self.folder_payloads = Path(self.parent, "payloads")

    def create_parent_folder(self):
        """
        Description:
            Create the parent folder of the file that called the class if they don't exist
        """

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

    def prepare_space(self, files=None, folder=None, test_text="picoCTF{test}"):
        """
        Description:
           Prepare the space for the challenge by creating the folders if they don't exist, create files from the file list provided
        """
        files = files if files else []
        folder = folder if folder else self.folder_files

        for file in files:
            if not Path(folder, file).exists():
                with open(Path(folder, file), "w") as f:
                    f.write(test_text)

    def get_challenge_file(self):
        """
        Description:
            Get the challenge file and assign it to the self.challenge_file for ease of access
        """
        if self.file and self.folder_files:
            self.challenge_file = Path(self.folder_files, self.file)
        elif not self.folder_files:
            if self.debug:
                print("Data folder not found")

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

    def search_files(
        self, directory, exclude_dirs, search_string, save=False, display=False
    ):
        """
        Description:
        Search for a string in the files in the directory

        Args:
            directory (str): Directory to search for the string
            exclude_dirs (list): List of directories to exclude
            search_string (str): String to search for
            save (bool, optional): Save the output. Defaults to False.
            display (bool, optional): Display the output. Defaults to False.

        Returns:
            list: List of output if save is True
        """
        if save:
            output = []

        for root, dirs, files in os.walk(directory):
            # Exclude specified directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            for file in files:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r") as f:
                        # Check if the search string is in the file
                        if search_string in f.read():
                            if display:
                                print(file_path)
                            if save:
                                output.append(file_path)
                except (IOError, UnicodeDecodeError):
                    # Handle files that cannot be opened or read
                    continue

        if save:
            return output

    def search_for_base64(self, file, *args, **kwargs):
        """
        Depracated, checkout search_for_base64_file
        """
        return self.search_for_base64_file(file, *args, **kwargs)

    def search_for_base64_file(self, file, *args, **kwargs):
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

    def get_self_functions(self):
        """
        Description:
        Get the functions of the class
        """

        return [
            func
            for func in dir(self)
            if callable(getattr(self, func)) and not func.startswith("__")
        ]

    def get_function_reference(self, function, file):
        """
        Description:
        Get the reference of the function in the file
        """

        if function not in self.get_self_functions():
            raise ValueError(f"Function {function} not found in the class")

        output = []

        with open(file, "r") as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if function in line:
                    output.append(line)
        return output

    def get_functions_from_file(self, file_path):
        """
        Description:
        Get the functions from the file
        """

        output = []
        with open(file_path, "r") as file_path:
            file_content = file_path.read()

        # Parse the file content into an AST
        tree = ast.parse(file_content)

        # Define a visitor class to find the function definition
        class FunctionDefFinder(ast.NodeVisitor):
            def __init__(self):
                self.function_def = None

            def visit_FunctionDef(self, node):
                output.append(node.name)
                # Continue visiting other nodes
                self.generic_visit(node)

        # Create an instance of the visitor and visit the AST
        finder = FunctionDefFinder()
        finder.visit(tree)

        # If the function was found, return its definition
        return output

    def find_function_from_file(self, file_path, function_name):
        """
        Description:
        Get the functions from the file
        """

        with open(file_path, "r") as file_path:
            file_content = file_path.read()

        # Parse the file content into an AST
        tree = ast.parse(file_content)

        # Define a visitor class to find the function definition
        class FunctionDefFinder(ast.NodeVisitor):
            def __init__(self):
                self.function_def = None

            def visit_FunctionDef(self, node):
                if node.name == function_name:
                    self.function_def = node
                # Continue visiting other nodes
                self.generic_visit(node)

        # Create an instance of the visitor and visit the AST
        finder = FunctionDefFinder()
        finder.visit(tree)

        # If the function was found, return its definition
        if finder.function_def:
            return ast.unparse(finder.function_def)
        else:
            return None
