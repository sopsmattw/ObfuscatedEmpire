import base64, os.path
from lib.common import helpers

class Module:

    def __init__(self, mainMenu, params=[]):

        self.info = {
            'Name': 'Find-Fruit',

            'Author': ['@424f424f'],

            'Description': ("Searches a network range for potentially vulnerable web services."),

            'Background' : True,

            'OutputExtension' : None,

            'NeedsAdmin' : False,

            'OpsecSafe' : True,

            'MinPSVersion' : '2',

            'Comments': [
                'Inspired by mattifestation Get-HttpStatus in PowerSploit'
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
            'Rhosts' : {
                'Description'   :   'Specify the CIDR range or host to scan.',
                'Required'      :   True,
                'Value'         :   ''
            },
            'Port' : {
                'Description'   :   'Specify the port to scan.',
                'Required'      :   False,
                'Value'         :   ''
            },
            'Path' : {
                'Description'   :   'Specify the path to a dictionary file.',
                'Required'      :   False,
                'Value'         :   ''
            },
            'Timeout' : {
                'Description'   :   'Set timeout for each connection in milliseconds',
                'Required'      :   False,
                'Value'         :   '50'
            },
            'UseSSL' : {
                'Description'   :   'Force SSL useage.',
                'Required'      :   False,
                'Value'         :   ''
            },
            'ShowAll' : {
                'Description'   :   'Switch. Show all results (default is to only show 200s).',
                'Required'      :   False,
                'Value'         :   ''
            },
            'Threads' : {
                'Description'   :   'The maximum concurrent threads to execute.',
                'Required'      :   False,
                'Value'         :   '10'
            },
            'FoundOnly' : {
                'Description'   :   'Switch. Show only found sites',
                'Required'      :   False,
                'Value'         :   'True'
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
        moduleSource = self.mainMenu.installPath + "/data/module_source/recon/Find-Fruit.ps1"
        if obfuscate:
            moduleSource = self.mainMenu.installPath + "/data/obfuscated_module_source/recon/Find-Fruit.ps1"
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

        script += "\nFind-Fruit"

        showAll = self.options['ShowAll']['Value'].lower()

        for option,values in self.options.iteritems():
            if option.lower() != "agent" and option.lower() != "showall":
                if values['Value'] and values['Value'] != '':
                    if values['Value'].lower() == "true":
                        # if we're just adding a switch
                        script += " -" + str(option)
                    else:
                        script += " -" + str(option) + " " + str(values['Value'])

        if showAll != "true":
            script += " | ?{$_.Status -eq 'OK'}"

        script += " | Format-Table -AutoSize | Out-String"

        return script

    def obfuscate(self, obfuscationCommand="", forceReobfuscation=False):
        if self.is_obfuscated() and not forceReobfuscation:
            return

        # read in the common module source code
        moduleSource = self.mainMenu.installPath + "/data/module_source/recon/Find-Fruit.ps1"
        try:
            f = open(moduleSource, 'r')
        except:
            print helpers.color("[!] Could not read module source path at: " + str(moduleSource))
            return ""

        moduleCode = f.read()
        f.close()

        # obfuscate and write to obfuscated source path
        obfuscatedSource = self.mainMenu.installPath + "/data/obfuscated_module_source/recon/Find-Fruit.ps1"
        obfuscatedCode = helpers.obfuscate(psScript=moduleCode, installPath=self.mainMenu.installPath, obfuscationCommand=obfuscationCommand)
        try:
            f = open(obfuscatedSource, 'w')
        except:
            print helpers.color("[!] Could not read obfuscated module source path at: " + str(obfuscatedSource))
            return ""
        f.write(obfuscatedCode)
        f.close()

    def is_obfuscated(self):
        obfuscatedSource = self.mainMenu.installPath + "/data/obfuscated_module_source/recon/Find-Fruit.ps1"
        return os.path.isfile(obfuscatedSource)
