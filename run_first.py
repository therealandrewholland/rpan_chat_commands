import ctypes, sys, os

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    
os.system('cmd /c "py -3.6 -m pip install -r \"%s\\requirements.txt\""' % os.getcwd())
