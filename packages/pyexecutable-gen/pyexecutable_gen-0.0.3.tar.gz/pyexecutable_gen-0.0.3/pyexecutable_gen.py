import PyInstaller.__main__
import sys,os
from pathlib import Path
import logging

"""
pyinstaller wrapper for programmatically generating executable from py file
14/5/2025  github.com/its-me-abi
written as part of unofficial anvil desktop project
"""

logger = logging.getLogger(__name__)

class builder:
    def __init__( self, script_path, dist_path = "",build_path = ""):
        self.script_path = script_path
        self.build_path = build_path
        self.dist_path = dist_path
        self.confirm = True
        self.data_folders = {}
        self.extra = []
        self.clean = False
        self.loglevel = "INFO"
        self.onedir_or_onefile = "--onedir" # pyinstaller choose onedir as default
        self.hidden_import = []
        self.icon = None
        self.console = True
        self.name = ""
        self.collect_all = []

    def set_name(self,val):
        self.name = val

    def set_confirm(self,val):
        self.confirm = val

    def set_console(self,val):
        self.console = val

    def set_icon(self,val):
        self.icon = val

    def get_hidden_Import(self):
        all = []
        for value in self.hidden_import:
            one = f"--hidden-import={value}"
            all += [one]
        return all

    def set_hidden_import(self,name):
        self.hidden_import.append(name)

    def set_onedir(self,val):
        if val:
           self.onedir_or_onefile = "--onedir"

    def set_onefile(self,val):
        if val:
           self.onedir_or_onefile = "--onefile"

    def set_loglevel(self, args):
        self.loglevel = args

    def set_clean(self,args):
        self.clean = args

    def set_extra_args(self,args):
        self.extra = args

    def set_data_folders(self,src,dest):
        self.data_folders[src] = dest

    def get_data_folders(self):
        data_folders = []
        if os.name == "nt":
            sep = ";"
        else:
            sep = ":"
        for key ,value in self.data_folders.items():
            one_map = f"--add-data={key}{sep}{value}"
            data_folders += [one_map]

        return data_folders

    def get_logLevel(self):
        level = f"--log-level={self.loglevel}"
        return [level]

    def get_collect_all(self):
        all = []
        for one_package in self.collect_all:
            one_argument = ["--collect-all",one_package]
            all += one_argument
        return all

    def set_collect_all(self,packagename):
        self.collect_all.append(packagename)

    def get_full_command_list(self):
        if self.script_path:
            comand = [self.script_path]
            if self.data_folders:
                comand += self.get_data_folders()
            if self.build_path:
                comand += ["--workpath",self.build_path]
            if self.dist_path:
                comand += ["--distpath", self.dist_path]

            if self.clean:
                comand += ["--clean"]
            comand+= self.get_logLevel()
            if self.onedir_or_onefile == "--onedir":
                comand += ["--onedir"]
            else:
                comand += ["--onefile"]
            if self.hidden_import:
                comand += self.get_hidden_Import()
            if self.icon:
                comand += [self.icon]
            if not self.console:
                comand += ["--noconsole"]
            if self.confirm:
                comand += ["--noconfirm"]
            if self.extra:
                comand+=self.extra
            if self.name:
                comand += ["--name",self.name]
            if self.collect_all:
                comand += self.get_collect_all()
            logger.info( "pyinstaller full command is = %s "%comand )
            return comand
        else:
            raise ValueError("nothing is provided as script path")

    def get_executable_data_folder(self):
        "when --ondir option is enabled there willbe a foldner named internal it contains data of users."
        val = Path ( self.get_executable_path() ).parent / "_internal"
        return val

    def get_executable_path(self):
        script_path = Path(self.script_path)
        dist_path = Path(self.dist_path).absolute() if self.dist_path else Path("dist").absolute()
        exe_name = self.name if self.name else script_path.stem
        exe_file = Path(f"{exe_name}.exe")
        if self.onedir_or_onefile == "--onedir":
            exe_dir = dist_path / exe_name
            if os.name == "nt":
                exe_file = exe_dir / f"{exe_name}.exe"
            else:
                exe_file = exe_dir / exe_name
        else:
            if os.name == "nt":
                exe_file = dist_path / f"{exe_name}.exe"
            else:
                exe_file = dist_path / exe_name
        return str(exe_file)

    def build_executable(self):
        try:
            command = self.get_full_command_list()
            PyInstaller.__main__.run(command)
            return True

        except Exception as e:
            logger.warning(f"pyintsaller Build failed with error: {e}" )

