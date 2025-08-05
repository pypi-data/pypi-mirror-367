from ctfsolver import CTFSolver
from pathlib import Path


class Templater(CTFSolver):
    def find_folder(self, folder_name):
        for i in range(len(self.file_called_frame)):
            file_called_path = Path(self.file_called_frame[i].filename)
            parent = Path(file_called_path).parent
            if parent.name == folder_name:
                return parent
        return None

    def main(self):

        # Find the folder that called this script
        parent = self.find_folder("template")
        if parent is None:
            raise Exception(
                "Could not find the template folder that called this script"
            )

        file = Path(parent, "solution_template.py")
        with open(file, "r") as f:
            template = f.read()

        with open(Path(self.folder_payloads, "solution.py"), "w") as f:
            f.write(template)


if __name__ == "__main__":
    templater = Templater()
    templater.main()
