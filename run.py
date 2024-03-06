import subprocess
import os
import sys


def run_node_script():
    # Define the command to run the Node.js script, assuming the correct Node version is already in use
    node_script_path = os.path.join('InterplanataryAssociation', 'src', 'NormalAgent', 'NormalAgent.js')

    if sys.platform.startswith('darwin'):
        # macOS: Use nvm to set Node.js version and run the script
        nvm_command = f'source ~/.nvm/nvm.sh && nvm use 21 && node {node_script_path}'
        subprocess.Popen(['bash', '-c', nvm_command])
    elif sys.platform.startswith('win32'):
        # Windows: Assume nvm-windows has set the correct Node.js version
        # Note: Adjust the command if you need to specify a path to node.exe
        subprocess.Popen(['powershell', '-Command', f'node {node_script_path}'],
                         creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        print("Unsupported OS")


if __name__ == "__main__":
    run_node_script()

    # Run another Python script
    subprocess.run(['python', 'src/node_interface.py'], check=True)
