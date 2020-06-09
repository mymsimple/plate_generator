from configparser import ConfigParser
CFG = ConfigParser()
CFG.read("config/config.cfg")
print("配置文件：" ,CFG.sections())