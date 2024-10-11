import os

class directory:
    def __init__(self) -> None:
        self.cwd = os.getcwd()
    
    def change_dir(self, dir):
        if dir not in os.listdir():
            raise FileNotFoundError
        self.cwd = os.path.join(self.cwd, dir)
        os.chdir(self.cwd)

    
    def return_to_dir(self):
        self.cwd =os.path.split(self.cwd)[0]
        os.chdir(self.cwd)