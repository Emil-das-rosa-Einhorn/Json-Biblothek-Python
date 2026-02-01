import json
import os
import shutil

file_Name = 'config.json'

pfad = os.path.join(os.path.dirname(__file__), file_Name)
backup_pfad = pfad + ".bak"
reset_pfad = pfad + ".reset"

config_autoCreate = False
config_Print = False
config_set_reset = False
config_autoLoad = False
config_check = False
passed = True

konflikte = []

ignore = {
    # --- 1. Python Built-ins (Systemfunktionen) ---
    'abs', 'bool', 'dict', 'dir', 'eval', 'exec', 'exit', 'float', 'globals', 
    'help', 'id', 'input', 'int', 'len', 'list', 'locals', 'max', 'min', 
    'open', 'print', 'quit', 'range', 'set', 'str', 'sum', 'type', 'vars',

    # --- 2. Importierte Module & Bibliotheken ---
    'json', 'math', 'os', 'portalocker', 'shutil', 'sqlite3', 'sys', 'time', 'zmq',

    # --- 3. Deine Bibliotheks-Funktionen & Variablen ---
    'add', 'addlist', 'backup', 'backup_pfad', 'config_autoCreate', 'config_autoLoad', 
    'config_check', 'config_Print', 'config_set_reset', 'delete', 'dump', 'edit', 
    'editor', 'file_Name', 'filename', 'get', 'ignore', 'info', 'konflikte', 'libconfig', 
    'load', 'passed', 'pfad', 'Print', 'reset_pfad', 'scan_keys', 'search', 'setreset', 
    'show', 'validate',

    # --- 4. Python Interne Namen (Dunder-Methods) ---
    '__annotations__', '__builtins__', '__cached__', '__doc__', '__file__', 
    '__loader__', '__name__', '__package__', '__spec__'
}

def health_check(autoCreate=None):
    if not os.path.exists(pfad):
        if autoCreate or config_autoCreate:
            backup_pfad = pfad + ".bak"
            if os.path.exists(backup_pfad):
                os.rename(backup_pfad, pfad)     
                print("[INFO] Config has been restored from backup!")
                backup()
                return True
            else:
                standard_daten = {"Version": 1.0}
                with open(pfad, 'w', encoding='utf-8') as f:
                    json.dump(standard_daten, f, indent=4)
                backup()
                return True
        return False

    try:
        with open(pfad, 'r', encoding='utf-8') as f:
            pass
        backup()
        return True

    except (json.JSONDecodeError, ValueError):
        if autoCreate or config_autoCreate:
            print("[WARNING] Config file corrupted! Attempting to load backup...")
            
            backup_pfad = pfad + ".bak"
            
            if os.path.exists(backup_pfad):
                os.remove(pfad)
                os.rename(backup_pfad, pfad)
                
                with open(pfad, 'r', encoding='utf-8') as f:
                   pass
                print("[INFO] Config has been restored from backup!")
                backup()
                return True
            else:
                print("[ERROR] No backup available. Recovery failed.")
                return False
        else:
            print ("[ERROR] Configuration restore from backup is disabled.")
            return False

def scan_keys():
    if not health_check():
        return False
    try:
        with open(pfad, 'r', encoding='utf-8') as f:
            _daten = json.load(f)

    except Exception as e:
        print(f"[ERROR] Failed to scan keys: {e}")
        return False
    
    for key in _daten.keys():
        if key in ignore:
            konflikte.append(key)
            print(f"[WARNING] Key conflict detected: '{key}' is a reserved keyword and cannot be used as a variable name.")

def libconfig (check=None,autoLoad=None,autoCreate=None,Print=None,set_reset=None, fileName=None):

    global config_autoCreate, config_Print, config_set_reset, config_autoLoad, config_check, passed

    if fileName is not None:
        filename(fileName)

    if autoCreate is not None:
        config_autoCreate = autoCreate
    else:
        config_autoCreate = False

    if Print is not None:
        config_Print = Print
    else:
        config_Print = False

    if set_reset is not None:

        config_set_reset = set_reset
    else:
        config_set_reset = False

    if autoLoad is not None:

        config_autoLoad = autoLoad
    else:
        config_autoLoad = False

    if check is not None:

        config_check = check
    else:
        config_check = False
    
    if config_check:
        if os.path.exists(pfad):
            passed = True
        else:
            if config_autoLoad:
                print("[INFO] Auto loading config...")
                load()
                if os.path.exists(pfad):
                    passed = True
                else:
                    print("[ERROR] No Config found and unable to auto load! Please create a config file or disable 'Config check' in libconfig.")
                    passed = False
            else:
                print("[ERROR] No Config found! Please create a config file or disable 'Config check' in libconfig.")
                passed = False
    
    if not setreset():
        if not config_set_reset:
            print ("[WARNING] 'Set reset point' is disabled.")
            if passed:
                pass
        else:
            print ("[WARNING] Could not set reset point. Ensure that the config file exists or 'Set reset point' is enabled.")
            passed = False
        
    return passed

def filename(filename):
    global pfad, backup_pfad, reset_pfad
    pfad = os.path.join(os.path.dirname(__file__), filename)
    backup_pfad = pfad + ".bak"
    reset_pfad = pfad + ".reset"
    if os.path.exists(pfad):
        return True
    else:
        return False

def info():
    
    header = """
    ============================================================
    JSON LIBRARY - DOCUMENTATION (v2.1)
    ============================================================

    """
    
    config_info = f"Config Path: {pfad}"

    functions = """

    AVAILABLE FUNCTIONS:
    [Functions marked with [X] return 'True' if executed 
    successfully and 'False' upon failure]

    1. libconfig(check=True/None,autoLoad=True/None,autoCreate=True/None,Print=True/None,set_reset=True/None, fileName="Filename"/None) [X]
       Configures the library settings.
        - check=True/None: Enables/disables config file existence check on initialization.
        - autoLoad=True/None: Enables/disables automatic loading of the config file on initialization
        - autoCreate=True/None: Enables/disables automatic creation of a base config if none exists.
        - Print=True/None: Enables/disables terminal output
        - set_reset=True/None: Enables/disables the ability to set reset points.
        - fileName="Filename"/None: Sets a custom name for the Json file.

    2. filename(filename)
       Sets the name of the config file.

    3. setreset(set_reset=TrueNone) [X]
       Sets a reset point by creating a .reset backup of the current config file.
         - set_reset=True/None: Enables/disables the ability to set reset points.
    
    4. reset() [X]
       Restores the config file from the .reset backup.
    
    5. load(autoCreate=True/None) [X]
       Loads JSON data into global memory.
       - autoCreate=True: Creates a base config if none exists 
         or restors it form the Backup.
         If the argument is omitted, no config file is created.
       - Should the config file be corrupted, the function 
         attempts to restore the file from the backup.

    6. show(Print=True/None)
       Returns all loaded variable names as a list.
       If set to 'True', output is displayed in the terminal.

    7. editor()
       Interactive terminal menu for changing values.
       - '/?' shows all keys | 'exit' terminates the mode.

    8. edit(Var, Val) [X]
       Changes an EXISTING value directly via code. 

    9. dump(dict) [X]
       Updates EXISTING values in the JSON. 
       Prevents accidental creation of new keys.

    10. add(Varname, Varvalue) [X]
       Creates a NEW data point in the JSON file.

    11. addlist(dict) [X]
       Adds multiple NEW data points simultaneously.
       Example: j.addlist({"D1": 10, "D2": 20})

    12. search(Varname) [X]
       Checks if a variable exists in the config (True/False).

    13. delete(name) [X]
       Permanently deletes a data point from the file and memory.

    14. backup() [X]
        Creates a backup/current state of the config file (Config.json.bak)

    15. get(key, group=None, default=None)
        Secure data access.
        - I = jsonBib.get("Name", group="group", default="DefaultValue")
        - The Key is the name of the data point to retrieve.
        - The Group (optional) specifies a subgroup within the JSON structure.
        - The DefaultValue (optional) is used if "Name" is not in the config file.

    16. getAll()
        Returns all data points in the config file as a dictionary.

    17. validate(Var, Valmin, Valmax=None) [X]
        Validates if a variable meets specified conditions.
        - For numerical values, both minimum and maximum can be set.
        - For boolean or None values, only Valmin is required.

    CONTROLS & SECURITY:
    - The delete function permanently removes data from the config file.
    - Use 'Ctrl+C' or 'exit' to safely cancel the editor.
    ============================================================
    """
    print(header)
    print(config_info)
    print(functions)

def backup():
    if os.path.exists(pfad):
        shutil.copy(pfad, pfad + ".bak")
        return True
    return False

def load(autoCreate=None):
    scan_keys()
    if health_check(autoCreate=autoCreate):
        with open(pfad, 'r', encoding='utf-8') as f:
            _daten = json.load(f)
            globals().update(_daten)
            print ("[INFO] Config file loaded successfully.")
            return True
    else:
        return False

def setreset(set_reset=None):
    if config_set_reset or set_reset:
        if not health_check():
            return False
        try:
            if os.path.exists(pfad):
                shutil.copy(pfad, pfad + ".reset")
                print(f"[INFO] Reset point set successfully. Reset point saved as '{reset_pfad}'")
                return True
            return False
        except Exception as e:
            print(f"[ERROR] Failed to set reset point: {e}")
            return False
    else:
        return False

def show (Print=None):
    variablen = [name for name in globals() if not name.startswith("__") and name not in ignore]
    if Print or config_Print:
        print (variablen)
    else:
        pass
    return variablen

def dump(neue_daten):
    if not health_check():
        return False
    backup()
    try:
        with open(pfad, 'r', encoding='utf-8') as f:
            daten = json.load(f)
    except FileNotFoundError:
        print("[ERROR] File not found. No updates possible.")
        return False

    filtered_data = {}
    rejected_keys = []

    for key, wert in neue_daten.items():
        if key in daten:
            filtered_data[key] = wert
        else:
            rejected_keys.append(key)

    if filtered_data:
        daten.update(filtered_data)
        with open(pfad, 'w', encoding='utf-8') as f:
            json.dump(daten, f, indent=4, ensure_ascii=False)
        print(f"Update successful: {list(filtered_data.keys())} updated.")
    
    if rejected_keys:
        print(f"[INFO] New data points ignored: {rejected_keys} (Do not exist in config).")
        return False
    backup()
    return True

def editor():
    if not health_check():
        return False
    
    while True:
        load(autoCreate=False)
        try:

            try:
                dataPoint = (input("Please enter the name of the variable you would like to change:"))
                if dataPoint == "/?":
                    show(True)
                    continue
                elif dataPoint == "exit":
                    print ("[INFO] Editor session ended.")
                    break

                else:
                    dataVar = globals()[dataPoint]
                    print (f"{dataPoint} is currently set to: {dataVar}")
                    newValin = (input("Please enter the new value: "))

                if newValin == "False":
                    newValin = False
                    daten = {dataPoint: newValin}
                    dump (daten)
                    continue
                elif newValin == "True":
                    newValin = True
                    daten = {dataPoint: newValin}
                    dump (daten)
                    continue
                elif newValin == "None":
                    newValin = None
                    daten = {dataPoint: newValin}
                    dump (daten)
                    continue
                else:

                    try:
                        newVal = int(newValin)
                        print ("detected int")
                    
                    except ValueError:
                        try:
                            newVal = float(newValin)
                            print ("detected Var")
                        
                        except ValueError:
                            newVal = newValin
                            print ("detected String")
                
            except KeyError:
                print(f"""[ERROR] The data point '{dataPoint}' does not exist in the config file. 
 Type /? to see a list of all variables.""")

            except Exception as e:
                #print (e)
                print ("[ERROR] Invalid input")

            else:
                daten = {dataPoint: newVal}
                dump (daten)
        except KeyboardInterrupt:
            print ("[INFO] Editor session ended.")
            break

def edit(Var, Val):

    if not health_check():
        return False
    try:

        try:
            dataPoint = Var

            if dataPoint == "/?":
                show(True)
                return True
            else:
                dataVar = globals()[dataPoint]
                print (f"{dataPoint} is currently set to: {dataVar}")
                newVal = Val
            
        except KeyError:
            print(f"[ERROR] The data point '{dataPoint}' does not exist in the config file.")
            return False

        except Exception as e:
            print (e)
            print ("[ERROR] Invalid input")
            return False

        else:
            daten = {dataPoint: newVal}
            dump (daten)
    except KeyboardInterrupt:
        print ("[INFO] Editor session ended.")
        return False
    
    return True

def search (Varsearch):

    if not health_check():
        return False
    
    Varonlist = False

    Varlist = show(Print=False)

    for GlobVar in Varlist:
        if GlobVar == Varsearch:
            Varonlist = True
        else:
            pass

    if Varonlist:
        return True
    else:
        return False
    
def add(Varname,Varvalue):

    if not health_check():
        return False
    
    for a in ignore:
        if Varname == a:
            print(f"[ERROR] '{Varname}' is a reserved keyword and cannot be used as a variable name.")
            return False
    newVardata = {Varname: Varvalue}
    try:
        with open(pfad, 'r', encoding='utf-8') as f:
            daten = json.load(f)
    except FileNotFoundError:
        daten = {}
        return False

    daten.update(newVardata)

    with open(pfad, 'w', encoding='utf-8') as f:
        json.dump(daten, f, indent=4, ensure_ascii=False)
    
    print(f"Update successful: {list(newVardata.keys())} updated.")
    backup()
    return True

def addlist(newVarlist):

    if not health_check():
        return False

    for a in ignore:
        if a in newVarlist:
            print(f"[ERROR] '{a}' is a reserved keyword and cannot be used as a variable name.")
            return False
        
    try:
        with open(pfad, 'r', encoding='utf-8') as f:
            daten = json.load(f)
    except FileNotFoundError:
        daten = {}
        return False

    daten.update(newVarlist)

    with open(pfad, 'w', encoding='utf-8') as f:
        json.dump(daten, f, indent=4, ensure_ascii=False)
    
    print(f"Update successful: {list(newVarlist.keys())} updated.")
    return True

def delete(name):

    if not health_check():
        return False

    try:
        with open(pfad, 'r', encoding='utf-8') as f:
            daten = json.load(f)
        
        if name in daten:
            del daten[name]
            
            with open(pfad, 'w', encoding='utf-8') as f:
                json.dump(daten, f, indent=4, ensure_ascii=False)
            
            if name in globals():
                del globals()[name]
                
            print(f"[INFO] '{name}' deleted successfully.")
            backup ()
            return True
        else:
            print(f"[ERROR] '{name}' does not exist and cannot be deleted.")
            return False
            
    except Exception as e:
        print(f"[ERROR] Failed to delete: {e}")
        return False
    
def get(key, group=None, default=None):
    try:
        with open(pfad, 'r', encoding='utf-8') as f:
            daten = json.load(f)

        if group is not None:
            if group in daten and key in daten[group]:
                wert = daten[group][key]
            else:
                return default

        else:
            def find_recursive(obj, target):
                if target in obj:
                    return obj[target]
                for v in obj.values():
                    if isinstance(v, dict):
                        res = find_recursive(v, target)
                        if res is not None:
                            return res
                return None
            
            wert = find_recursive(daten, key)

        if wert is None:
            return default
    
        return wert

    except Exception as e:
        print(f"[ERROR] get failed for '{key}': {e}")
        return default
    
def getAll():
    health_check()
    backup()
    try:
        with open(pfad, 'r', encoding='utf-8') as f:
            daten = json.load(f)
        return daten
    except Exception as e:
        print(f"[ERROR] getAll failed: {e}")
        return None

def reset():
    try:
        if os.path.exists(reset_pfad):
            if os.path.exists(pfad):
                os.remove(pfad)
            os.rename(reset_pfad, pfad)
            setreset()
            load()
            print("[INFO] Config has been restored and loaded from .reset!")
            return True
        else:
            print("[ERROR] No reset file found. Reset failed.")
            return False
    except Exception as e:
        print(f"[ERROR] Failed to reset configuration: {e}")
        return False
    
def validate(Var, Valmin, Valmax=None):

    if not health_check():
        return False
    
    if Var not in globals():
        print(f"[ERROR] The variable '{Var}' does not exist.")
        return False
    if Valmax is not None and isinstance(Valmax, (bool, str, type(None))):
        print("[ERROR] Valmax must be a number.")
        return False
    if not isinstance(Valmin, (bool, type(None))):
        if isinstance(Valmin, (int, float)):
            if Valmax is not None:
                if Valmin <= get(Var) <= Valmax:
                    return True
                else:
                    return False
            else:
                if get(Var) == Valmin:
                    return True
                else:
                    return False
    else:
        if get(Var) == Valmin:
            return True
        else:
            return False