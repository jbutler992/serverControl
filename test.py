import json, subprocess

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

def getServerDisplayNames(jsonConfig):
    displayNames = []
    for server in jsonConfig["Servers"]:
        displayNames.append(str(jsonConfig["Servers"][server]["DisplayName"]))
    return displayNames

def getIPMIPowerStatus(ipmiInfo, ipmiCommands):
    powerStatusCommand = ipmiCommands["PowerStatus"]
    command = "ipmitool -I lan -U "+ipmiInfo[1]+" -P "+ipmiInfo[2]+" -H "+ipmiInfo[0]+" "+powerStatusCommand
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
for name in serverNames:
    print name
    connectionInfo = getIPMIConnectionInfo(config, name)
    print getIPMIPowerStatus(connectionInfo, ipmiCommands)