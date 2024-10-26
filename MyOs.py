import os
import sys
import hashlib
import getpass
import time
import platform
import psutil
import webbrowser

# Fajl za čuvanje korisničkih podataka
USER_DATA_FILE = 'users.txt'

# Simulacija fajl sistema
FILE_SYSTEM = {
    'home': {
        'user': {
            'documents': {},
            'pictures': {},
            'downloads': {}
        }
    },
    'system': {
        'config': {},
        'logs': {}
    }
}

current_directory = ['home', 'user']  # Početni direktorijum

# Lista imena sistema
SYSTEM_NAMES = ["HeliosOS", "AstraOS", "NebulaOS", "OrionOS"]

# Lista jezika
LANGUAGES = {
    "1": "english",
    "2": "serbian"
}
ASTRAOS_ASCII_ART = boot_art = r"""
   ____            _    ____   ____  ____   _____ 
  / ___|  ___  __| | _|  _ \ / ___|/ ___| | ____|
 | |     / _ \/ _` || || |_) | |     \___ \ |  _|  
 | |___ |  __/ (_| || ||  __/| |___   ___) || |___ 
  \____| \___|\__,_||_||_|    \____| |____/ |_____|
                 Welcome to AstraOS - Fast and Secure!
"""

# Tekstovi za različite jezike
TEXT = {
    "welcome": {
        "english": "Welcome to {system_name}!",
        "serbian": "Dobrodošli u {system_name}!"
    },
    "booting": {
        "english": "Booting {system_name}...",
        "serbian": "Pokrećemo {system_name}..."
    },
    "system_loaded": {
        "english": "System loaded successfully!",
        "serbian": "Sistem je uspešno učitan!"
    },
    "choose_language": {
        "english": "Choose your language:",
        "serbian": "Izaberite jezik:"
    },
    "main_menu": {
        "english": "\nMain Menu:",
        "serbian": "\nGlavni Meni:"
    },
    "options": {
        "english": "1. Login\n2. Create Account\n3. Exit",
        "serbian": "1. Prijavi se\n2. Kreiraj nalog\n3. Izlaz"
    },
    "invalid_option": {
        "english": "Invalid option. Please try again.",
        "serbian": "Nevažeća opcija. Molimo pokušajte ponovo."
    },
    "login_success": {
        "english": "Successfully logged in as '{username}'!",
        "serbian": "Uspešno ste se prijavili kao '{username}'!"
    },
    "login_failure": {
        "english": "Invalid username or password.",
        "serbian": "Nevažeće korisničko ime ili lozinka."
    },
    "account_created": {
        "english": "Account for user '{username}' created successfully!",
        "serbian": "Nalog za korisnika '{username}' je uspešno kreiran!"
    },
    "username_exists": {
        "english": "Username already exists. Please try again.",
        "serbian": "Ovo korisničko ime već postoji. Molimo pokušajte ponovo."
    },
    "password_mismatch": {
        "english": "Passwords do not match. Please try again.",
        "serbian": "Lozinke se ne podudaraju. Molimo pokušajte ponovo."
    },
    "prompt_command": {
        "english": "Enter command: ",
        "serbian": "Unesite komandu: "
    },
    "unknown_command": {
        "english": "Unknown command. Type 'help' for a list of commands.",
        "serbian": "Nepoznata komanda. Unesite 'help' za listu komandi."
    },
    "shutdown_message": {
        "english": "Shutting down...",
        "serbian": "Isključujemo sistem..."
    }
}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    users = {}
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as f:
            for line in f:
                try:
                    username, password = line.strip().split(':')
                    users[username] = password
                except ValueError:
                    continue
    return users

def save_user(username, password):
    with open(USER_DATA_FILE, 'a') as f:
        f.write(f"{username}:{hash_password(password)}\n")

def create_account(language):
    users = load_users()
    while True:
        username = input("Enter username: " if language == "english" else "Unesite korisničko ime: ")
        if username in users:
            print(TEXT["username_exists"][language])
        else:
            break
    while True:
        password = getpass.getpass("Enter password: " if language == "english" else "Unesite lozinku: ")
        password_confirm = getpass.getpass("Confirm password: " if language == "english" else "Potvrdite lozinku: ")
        if password != password_confirm:
            print(TEXT["password_mismatch"][language])
        else:
            break
    save_user(username, password)
    print(TEXT["account_created"][language].format(username=username))

def login(language):
    users = load_users()
    username = input("Username: " if language == "english" else "Korisničko ime: ")
    password = getpass.getpass("Password: " if language == "english" else "Lozinka: ")
    hashed_password = hash_password(password)
    if username in users and users[username] == hashed_password:
        print(TEXT["login_success"][language].format(username=username))
        return username
    else:
        print(TEXT["login_failure"][language])
        return None

def show_boot_screen(system_name, language):
    os.system('cls' if os.name == 'nt' else 'clear')
    print("#" * 50)
    print("#" + " " * 48 + "#")
    print("#" + f"  {system_name.center(46)}  " + "#")
    print("#" + " " * 48 + "#")
    print("#" * 50)
    print(TEXT["booting"][language].format(system_name=system_name))
    for i in range(1, 6):
        print(f"{i * 20}%")
        time.sleep(0.5)
    print(TEXT["system_loaded"][language])
    time.sleep(1)

def choose_system_name():
    print("Choose system name:")
    for idx, name in enumerate(SYSTEM_NAMES, 1):
        print(f"{idx}. {name}")
    while True:
        choice = input("Option (1-4): ")
        if choice in ['1', '2', '3', '4']:
            return SYSTEM_NAMES[int(choice) - 1]
        else:
            print("Invalid choice. Please try again.")

def choose_language():
    print("\n" + TEXT["choose_language"]["english"])
    for key, lang in LANGUAGES.items():
        print(f"{key}. {lang.capitalize()}")
    while True:
        choice = input("Option (1/2): ")
        if choice in LANGUAGES:
            return LANGUAGES[choice]
        else:
            print("Invalid choice. Defaulting to English.")
            return "english"

def get_current_directory_path():
    return '/' + '/'.join(current_directory)

def navigate_to_directory(path, language):
    global current_directory
    if path.startswith('/'):
        # Absolutna putanja
        new_path = path.strip('/').split('/')
    else:
        # Relativna putanja
        new_path = current_directory + path.strip().split('/')
    
    temp_fs = FILE_SYSTEM
    for folder in new_path:
        if folder in temp_fs:
            temp_fs = temp_fs[folder]
        else:
            print(f"Directory '{folder}' does not exist." if language == "english" else f"Direktorijum '{folder}' ne postoji.")
            return
    current_directory = new_path

def list_directory(language):
    temp_fs = FILE_SYSTEM
    for folder in current_directory:
        temp_fs = temp_fs[folder]
    for item in temp_fs:
        print(item)

def show_sysinfo(language):
    print("\n--- System Information ---" if language == "english" else "\n--- Informacije o sistemu ---")
    print(f"Operating System: {platform.system()} {platform.release()}" if language == "english" else f"Operativni sistem: {platform.system()} {platform.release()}")
    print(f"Platform: {platform.platform()}" if language == "english" else f"Platforma: {platform.platform()}")
    print(f"Processor: {platform.processor()}" if language == "english" else f"Procesor: {platform.processor()}")
    print(f"Python Version: {platform.python_version()}" if language == "english" else f"Verzija Python-a: {platform.python_version()}")
    print(f"Total RAM: {round(psutil.virtual_memory().total / (1024 **3))} GB" if language == "english" else f"Ukupna RAM: {round(psutil.virtual_memory().total / (1024 **3))} GB")
    print(f"Available RAM: {round(psutil.virtual_memory().available / (1024 **3))} GB\n" if language == "english" else f"Slobodna RAM: {round(psutil.virtual_memory().available / (1024 **3))} GB\n")

def show_devices(language):
    print("\n--- Connected Devices ---" if language == "english" else "\n--- Povezani uređaji ---")
    # Ovo je simulacija, u stvarnosti bi trebalo koristiti specifične module za detekciju uređaja
    print("1. USB Device: Flash Drive" if language == "english" else "1. USB uređaj: Flash Drive")
    print("2. Network Adapter: Ethernet" if language == "english" else "2. Mrežni adapter: Ethernet")
    print("3. Graphics Card: NVIDIA GeForce RTX 3080" if language == "english" else "3. Grafička kartica: NVIDIA GeForce RTX 3080")
    print("4. Peripheral: Logitech Keyboard\n" if language == "english" else "4. Zvanični uređaj: Logitech Keyboard\n")

def create_file(filename, language):
    temp_fs = FILE_SYSTEM
    for folder in current_directory:
        temp_fs = temp_fs[folder]
    if filename in temp_fs:
        print(f"File or directory '{filename}' already exists." if language == "english" else f"Fajl ili direktorijum '{filename}' već postoji.")
    else:
        temp_fs[filename] = {"content": ""}
        print(f"File '{filename}' created." if language == "english" else f"Fajl '{filename}' je kreiran.")

def remove_file(filename, language):
    temp_fs = FILE_SYSTEM
    for folder in current_directory[:-1]:
        temp_fs = temp_fs[folder]
    if filename in temp_fs:
        del temp_fs[filename]
        print(f"File or directory '{filename}' removed." if language == "english" else f"Fajl ili direktorijum '{filename}' je obrisan.")
    else:
        print(f"File or directory '{filename}' does not exist." if language == "english" else f"Fajl ili direktorijum '{filename}' ne postoji.")

def view_file(filename, language):
    temp_fs = FILE_SYSTEM
    for folder in current_directory:
        temp_fs = temp_fs[folder]
    if filename in temp_fs:
        file = temp_fs[filename]
        if "content" in file:
            print("\n--- File Content ---" if language == "english" else "\n--- Sadržaj Fajla ---")
            print(file["content"])
        else:
            print(f"'{filename}' is a directory." if language == "english" else f"'{filename}' je direktorijum.")
    else:
        print(f"File '{filename}' does not exist." if language == "english" else f"Fajl '{filename}' ne postoji.")

def edit_file(filename, language):
    temp_fs = FILE_SYSTEM
    for folder in current_directory:
        temp_fs = temp_fs[folder]
    if filename in temp_fs:
        file = temp_fs[filename]
        if "content" in file:
            print("Enter content (type 'END' on a new line to finish):" if language == "english" else "Unesite sadržaj (unesite 'END' na novoj liniji da završite):")
            lines = []
            while True:
                line = input()
                if line.strip().upper() == "END":
                    break
                lines.append(line)
            file["content"] = "\n".join(lines)
            print(f"File '{filename}' updated." if language == "english" else f"Fajl '{filename}' je ažuriran.")
        else:
            print(f"'{filename}' is a directory." if language == "english" else f"'{filename}' je direktorijum.")
    else:
        print(f"File '{filename}' does not exist." if language == "english" else f"Fajl '{filename}' ne postoji.")

def run_program(filename, language):
    temp_fs = FILE_SYSTEM
    for folder in current_directory:
        temp_fs = temp_fs[folder]
    if filename in temp_fs:
        file = temp_fs[filename]
        if "content" in file:
            print(f"Running '{filename}'..." if language == "english" else f"Pokrećem '{filename}'...")
            try:
                exec(file["content"])
            except Exception as e:
                print(f"Error running '{filename}': {e}" if language == "english" else f"Greška pri pokretanju '{filename}': {e}")
        else:
            print(f"'{filename}' is a directory." if language == "english" else f"'{filename}' je direktorijum.")
    else:
        print(f"File '{filename}' does not exist." if language == "english" else f"Fajl '{filename}' ne postoji.")

def open_google(language):
    try:
        webbrowser.open("https://www.google.com")
        print("Google opened in your default browser." if language == "english" else "Google je otvoren u vašem podrazumevanom pregledaču.")
    except Exception as e:
        print(f"Failed to open Google: {e}" if language == "english" else f"Neuspešno otvaranje Google-a: {e}")

def command_line_interface(username, language):
    global current_directory
    print(f"\nWelcome, {username}! Type 'help' for a list of commands." if language == "english" else f"\nDobrodošli, {username}! Unesite 'help' za listu komandi.")
    while True:
        current_path = get_current_directory_path()
        prompt = f"{username}@{SYSTEM_NAMES[0]}:{current_path}$ " if language == "english" else f"{username}@{SYSTEM_NAMES[0]}:{current_path}$ "
        command = input(prompt).strip().lower()
        
        if command == 'help':
            if language == "english":
                print("\n--- Available Commands ---")
                print("help - Show this help message")
                print("echo [text] - Display the entered text")
                print("logout - Log out of the system")
                print("shutdown - Shut down the system")
                print("ls - List contents of the current directory")
                print("cd [path] - Change the current directory")
                print("sysinfo - Show system information")
                print("devices - Show connected devices")
                print("touch [filename] - Create a new file or directory")
                print("rm [filename] - Remove a file or directory")
                print("view [filename] - View the content of a file")
                print("edit [filename] - Edit the content of a file")
                print("run [filename] - Run a script from a file")
                print("open google - Open Google in your default browser")
                print("mkdir [dirname] - Create a new directory")
                print("rmdir [dirname] - Remove a directory (must be empty)")
            elif language == "serbian":
                print("\n--- Dostupne Komande ---")
                print("help - Prikaži ovu listu komandi")
                print("echo [text] - Prikazuje uneseni tekst")
                print("logout - Odjavljuje se iz sistema")
                print("shutdown - Isključuje sistem")
                print("ls - Prikazuje sadržaj trenutnog direktorijuma")
                print("cd [path] - Menja trenutni direktorijum")
                print("sysinfo - Prikazuje sistemske informacije")
                print("devices - Prikazuje listu povezanih uređaja")
                print("touch [filename] - Kreira novi fajl ili direktorijum")
                print("rm [filename] - Briše fajl ili direktorijum")
                print("view [filename] - Prikazuje sadržaj fajla")
                print("edit [filename] - Uređuje sadržaj fajla")
                print("run [filename] - Pokreće skriptu iz fajla")
                print("open google - Otvara Google u vašem podrazumevanom pregledaču")
                print("mkdir [dirname] - Kreira novi direktorijum")
                print("rmdir [dirname] - Briše direktorijum (mora biti prazan)")
        elif command.startswith('echo '):
            print(command[5:])
        elif command == 'logout':
            print("Logging out..." if language == "english" else "Odjavljujemo se...")
            break
        elif command == 'shutdown':
            print(TEXT["shutdown_message"][language])
            sys.exit()
        elif command == 'ls':
            list_directory(language)
        elif command.startswith('cd '):
            path = command[3:].strip()
            navigate_to_directory(path, language)
        elif command == 'sysinfo':
            show_sysinfo(language)
        elif command == 'devices':
            show_devices(language)
        elif command.startswith('touch '):
            filename = command[6:].strip()
            create_file(filename, language)
        elif command.startswith('rm '):
            filename = command[3:].strip()
            remove_file(filename, language)
        elif command.startswith('view '):
            filename = command[5:].strip()
            view_file(filename, language)
        elif command.startswith('edit '):
            filename = command[5:].strip()
            edit_file(filename, language)
        elif command.startswith('run '):
            filename = command[4:].strip()
            run_program(filename, language)
        elif command == 'open google':
            open_google(language)
        elif command.startswith('mkdir '):
            dirname = command[6:].strip()
            create_file(dirname, language)
        elif command.startswith('rmdir '):
            dirname = command[6:].strip()
            remove_file(dirname, language)
        else:
            print(TEXT["unknown_command"][language])

def main_menu(system_name, language):
    while True:
        print("\n" + TEXT["main_menu"][language])
        print(TEXT["options"][language])
        choice = input("Option (1/2/3): " if language == "english" else "Opcija (1/2/3): ").strip()
        if choice == '1':
            user = login(language)
            if user:
                command_line_interface(user, language)
        elif choice == '2':
            create_account(language)
        elif choice == '3':
            print(TEXT["shutdown_message"][language])
            sys.exit()
        else:
            print(TEXT["invalid_option"][language])

def pyos():
    system_name = choose_system_name()
    language = choose_language()
    show_boot_screen(system_name, language)
    main_menu(system_name, language)

if __name__ == "__main__":
    pyos()