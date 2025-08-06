import subprocess

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    def initialize(self, version, build_data):
        print("--- Running URDF generation script ---")
        # Ensure you are in the project root
        # and execute the build script.
        subprocess.run(["python", "build.py"], check=True)
        print("--- URDF generation complete ---")
