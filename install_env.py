import subprocess
import sys
import requests
import git
import os
from Util.GitRemoteProgress import GitRemoteProgress

def is_installed(command):
    try:
        subprocess.check_call([command, '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except:
        return False


def download_file(url, filename):
    response = requests.get(url)
    with open(filename, 'wb') as file:
        file.write(response.content)


def is_winget_available():
    try:
        subprocess.check_call(['winget', '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except:
        return False


def install_on_windows():
    if is_winget_available():
        install_nvm_with_winget()
    else:
        print("winget is not available. Please install winget or nvm-windows manually.")

        # Check if Node.js and Git are installed after ensuring nvm-windows is set up
    if not is_installed('node'):
        print("Installing Node.js using nvm-windows...")
        # Note: You'll need to open a new PowerShell or Command Prompt session
        # after nvm-windows installation for 'nvm' command to be recognized.
        subprocess.run(['nvm', 'install', '21'], check=True)
        subprocess.run(['nvm', 'use', '21'], check=True)

    if not is_installed('git'):
        print("Git not found. Downloading and installing Git...")
        # Assuming a direct link to the Windows installer for Git
        git_installer = "Git-2.29.0-64-bit.exe"
        download_file("https://github.com/git-for-windows/git/releases/download/v2.29.0.windows.1/" + git_installer,
                      git_installer)
        subprocess.run([git_installer, '/VERYSILENT'], check=True)


def install_nvm_with_winget():
    if not is_installed('nvm'):
        print("nvm-windows not found. Installing nvm-windows...")
        subprocess.run(['winget', 'install', 'CoreyButler.NVMforWindows'], check=True)
        print("nvm-windows installed successfully.")

def is_installed(command):
    try:
        subprocess.check_call([command, '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except:
        return False

def install_nvm_on_unix():
    if not is_installed('nvm'):
        print("nvm not found. Installing nvm...")
        # This installs nvm by downloading the install script and executing it
        subprocess.run(['brew install nvm'], check=True)

        # Source nvm script to make nvm available in the current session
        subprocess.run(['.','$HOME/.nvm/nvm.sh'], shell=True, check=True)

def install_on_mac():
    if not is_installed('brew'):
        print("Homebrew not found. Installing Homebrew...")
        subprocess.run(['/bin/bash', '-c', "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"], check=True)

    if not is_installed('nvm'):
        install_nvm_on_unix()

    if not is_installed('node'):
        print("Node.js not found. Downloading and installing Node.js v21...")
        # Assuming a direct link to the MacOS installer for Node.js v21
        node_installer = "node-v21.0.0.pkg"
        download_file("https://nodejs.org/dist/v21.0.0/" + node_installer, node_installer)
        subprocess.run(['sudo', 'installer', '-pkg', node_installer, '-target', '/'], check=True)

    if not is_installed('git'):
        print("Git not found. Installing Git...")
        # On MacOS, Git can be installed via Homebrew as an example
        subprocess.run(['brew', 'install', 'git'], check=True)



if __name__ == "__main__":
    current_dir = os.getcwd()
    print("installing requirements..")
    subprocess.run(['pip', 'install', '-r', 'requirements.txt'],  cwd=current_dir, check=True)

    print("Installing Node.js and Git...")
    if sys.platform.startswith('win'):
        install_on_windows()
    elif sys.platform.startswith('darwin'):
        install_on_mac()
    else:
        print("Unsupported OS")

    print("Cloning the repository...")
    # URL of the repository you want to clone
    git_url = 'https://github.com/longpp17/InterplanataryAssociation.git'

    # Cloning the repository
    git.Repo.clone_from(git_url, current_dir + '/InterplanataryAssociation', progress=GitRemoteProgress())

    print("Installing the required Node.js packages...")
    # Install the required Node.js packages
    subprocess.run(['npm', 'install', ], cwd= current_dir + '/InterplanataryAssociation', check=True)
