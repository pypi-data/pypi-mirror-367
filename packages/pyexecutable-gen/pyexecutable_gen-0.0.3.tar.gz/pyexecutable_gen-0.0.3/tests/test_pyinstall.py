import pyexecutable_gen as exe
import unittest
from pathlib import Path

class Test_comands_static(unittest.TestCase):
    def setUp(self):
        self.script_path = "testscript.py"
        self.exe = exe.builder( self.script_path )
        self.exe.set_collect_all("pyinstaller")

    def test_onedir(self):
        self.exe.set_onedir(True)
        fullcommand = self.exe.get_full_command_list()
        self.assertIn("--onedir",fullcommand,"onedire is set but its not found in command")

    def test_onefile(self):
        self.exe.set_onefile(True)
        fullcommand = self.exe.get_full_command_list()
        self.assertIn("--onefile",fullcommand,"onefile is set but its not found in command")


class Test_comands_dynamic(unittest.TestCase):
    def test_exe_file_name(self):
        script_path = str(Path(__file__).parent / "testfile.py" )
        ex = exe.builder(script_path)
        ex.set_loglevel("ERROR")
        ex.set_name("XXXapp")
        ex.build_executable()
        exepath = ex.get_executable_path()
        self.assertEqual( Path(exepath).name , "XXXapp.exe", "custom name set by api and prodcued file is different")

    def test_exe_file_and_folder(self):

        script_path = str(Path(__file__).parent / "testfile.py" )
        ex = exe.builder(script_path)
        ex.set_loglevel("ERROR")
        folder = ex.get_executable_data_folder()
        ex.build_executable()
        file = ex.get_executable_path()
        self.assertTrue(Path(folder).is_dir() , "is dir failed so executables data not in folder ")
        self.assertTrue(Path(file).is_file(), "is file check failed so executable not exists as file ")

if __name__ == "__main__":
    unittest.main()



