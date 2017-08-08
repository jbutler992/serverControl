#Server Management web UI
#
#Jeremiah Butler

import web, json, subprocess, HTML
from web import form


render = web.template.render('templates/')

urls = ('/', 'index',
        '/getPowerStatus', 'getPowerStatus',
        '/powerOn',  'powerOn',
        '/powerOff',  'powerOff')
        

app = web.application(urls, globals())

def getConfigJSON():
    configFile = open('config.json', 'r')
    config = json.load(configFile)
    configFile.close()
    return config

def getServerNames(jsonConfig):
    serverNames = []
    for server in jsonConfig["Servers"]:
        serverNames.append(str(server))
    return serverNames

def getServerDisplayName(jsonConfig, serverName):
    return str(jsonConfig["Servers"][serverName]["DisplayName"])

def getIPMIPowerStatus(ipmiInfo, ipmiCommands):
    if(ipmiInfo[0] == "0.0.0.0"):
        return 'IPMI Not Supported'
    powerStatusCommand = ipmiCommands["PowerStatus"]
    command = "ipmitool -I lan -U "+ipmiInfo[1]+" -P "+ipmiInfo[2]+" -H "+ipmiInfo[0]+" "+powerStatusCommand
    status = runIPMICommand(command)
    return status

def IPMIPowerOff(ipmiInfo, ipmiCommands, shutdownType):
    if(shutdownType == "shutdown"):
        powerOffCommand = str(ipmiCommands["Shutdown"])
    else:
        powerOffCommand = str(ipmiCommands["PowerOff"])
    command = "ipmitool -I lan -U "+ipmiInfo[1]+" -P "+ipmiInfo[2]+" -H "+ipmiInfo[0]+" "+powerOffCommand
    status = runIPMICommand(command)
    return status

def IPMIPowerOn(ipmiInfo, ipmiCommands):
    powerOnCommand = str(ipmiCommands["PowerOn"])
    command = "ipmitool -I lan -U "+ipmiInfo[1]+" -P "+ipmiInfo[2]+" -H "+ipmiInfo[0]+" "+powerOnCommand
    status = runIPMICommand(command)
    return status

def getIPMICommands(jsonConfig):
    return jsonConfig["IPMI_Commands"]

def getIPMIConnectionInfo(jsonConfig, serverName):
    credentials = []
    credentials.append(str(jsonConfig["Servers"][serverName]["IPMI_IP"]))
    credentials.append(str(jsonConfig["Servers"][serverName]["IPMI_User"]))
    credentials.append(str(jsonConfig["Servers"][serverName]["IPMI_Password"]))
    return credentials

def runIPMICommand(command):
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output = process.communicate()
    result = output[0].replace('\n', '')
    return result

config = getConfigJSON()
ipmiCommands = getIPMICommands(config)
serverNames = getServerNames(config)

class index:
    def GET(self):
        return render.base()

class getPowerStatus:
    def POST(self):
        web.header('Content-Type', 'application/json')
        serverInfo = []
        for name in serverNames:
            displayName = getServerDisplayName(config, name)
            connectionInfo = getIPMIConnectionInfo(config, name)
            powerStatus = getIPMIPowerStatus(connectionInfo, ipmiCommands)
            powerOnButton = """<input type="button" onclick="powerOn('"""+name+"""')" value="Power On">"""
            shutdownButton = """<input type="button" onclick="powerOff('"""+name+"""','shutdown')" value="Shutdown">"""
            powerOffButton = """<input type="button" onclick="powerOff('"""+name+"""','powerOff')" value="Power Off">"""
            serverInfo.append((displayName, str(powerStatus), powerOnButton, shutdownButton, powerOffButton))
        statusTable = HTML.table(serverInfo, header_row=['Server', 'Power Status', 'Power On', 'Shutdown', 'Power Off'])
        return json.dumps({'powerStatus': statusTable})

class powerOn:
    def POST(self):
        web.header('Content-Type', 'application/json')
        serverName = web.input()
        connectionInfo = getIPMIConnectionInfo(config, serverName.serverName)
        IPMIPowerOn(connectionInfo, ipmiCommands)
        return

class powerOff:
    def POST(self):
        web.header('Content-Type', 'application/json')
        serverInfo = web.input()
        connectionInfo = getIPMIConnectionInfo(config, serverInfo.serverName)
        IPMIPowerOff(connectionInfo, ipmiCommands, serverInfo.shutdownType)
        return


if __name__=="__main__":
    web.internalerror = web.debugerror
    app.run()