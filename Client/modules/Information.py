# mac addr# uptime# computer type# host# port# bios date# bios id
# # bios type# bios vendor# server location# mutex# uuid
# # active cpu/ram/disk usage# tracemap#dxdiag#cpuinfo)
import platform, psutil, os, json, datetime, tempfile, subprocess, time, xmltodict
from xmljson import badgerfish as bf


class Win32:
    # TODO: Generate a test report file of dxdiag
    report_path = os.path.join(tempfile.gettempdir(), 'report.xml')    
    def genReport():
        if os.path.exists(report_path):
            os.remove(report_path)
        subprocess.call(["dxdiag",  "-x", report_path])
        report = open(report_path,"r")
        xml = report.read()
        report.close()
        info = xmltodict.parse(xml)
        return info['DxDiag']

    def getInfo():
        dxdiag = genReport()
        information = {
            "system": {
                "name": dxdiag['SystemInformation']['MachineName'],            
                "manufacturer": dxdiag['SystemInformation']['SystemManufacturer'],
                "model": dxdiag['SystemInformation']['SystemModel'],
                "os": dxdiag['SystemInformation']['OperatingSystem'],
                "windir": dxdiag['SystemInformation']['WindowsDir'],                              
                "language": dxdiag['SystemInformation']['Language'],
                "bios": dxdiag['SystemInformation']['BIOS']
            },
            "cpu": {
                "model": dxdiag['SystemInformation']['Processor'],
                "real_cpu": psutil.cpu_count(logical=False),
                "logical_cpu": psutil.cpu_count(logical=True),
                "max_cpu_freq": psutil.cpu_freq()[2]
            },
            "gpu": getGpu(),
            "ram": {
                "total_ram": dxdiag['SystemInformation']['Memory'][:4],
                "swap_ram": bytes2human(psutil.swap_memory()[0])
            },
            "disk": getDisks(),
            "sound": getSound(),
            "net": {},
            "misc": {
                "boot_time": datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S"),
                "users": getUsers(),
                "battery": getBattery()
            }
        }
        #print(json.dumps(information,indent=4))
        os.remove(report_path)
        return json.dumps(information)

    def bytes2human(n):
        symbols = ('KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB')
        prefix = {}
        for i, s in enumerate(symbols):
            prefix[s] = 1 << (i + 1) * 10
        for s in reversed(symbols):
            if n >= prefix[s]:
                value = float(n) / prefix[s]
                return '%.1f%s' % (value, s)
        return "%s" % n

    def secs2hours(secs):
        mm, ss = divmod(secs, 60)
        hh, mm = divmod(mm, 60)
        return "%d:%02d:%02d" % (hh, mm, ss)

    def getDisks():
        disks = {}
        for part in psutil.disk_partitions(all=False):
            if os.name == 'nt':
                if 'cdrom' in part.opts or part.fstype == '': #Skip CD-ROM
                    continue
            usage = psutil.disk_usage(part.mountpoint)
            disks[part.device] = {"total": bytes2human(usage.total), "used": bytes2human(usage.used), "free": bytes2human(usage.free)}
        return disks

    def getUsers():
        users = {}
        index = 0
        for user in psutil.users():
            users[index] = {"name": user.name,"terminal": user.terminal,"host": user.host,"pid": user.pid}
            index = index + 1
        return users

    def getBattery():
        info = psutil.sensors_battery()
        battery = {"percent": info[0], "power_plugged": info[2]}
        if str(info[1]) == 'BatteryTime.POWER_TIME_UNLIMITED':
            battery["time_left"] = 'unlimited'
        else:
            battery["time_left"] = info[1]
        return battery

    def getGpu():
        if not os.path.exists(report_path):
            info = genReport()
        else:
            report = open(report_path,"r")
            xml = report.read()
            report.close()
            info = xmltodict.parse(xml)
        devices = info['DxDiag']['DisplayDevices']['DisplayDevice']
        gpus = {}
        index = 0
        for gpu in devices:
            gpu_info = {
                "card_name": gpu['CardName'],
                "manufacturer": gpu['Manufacturer'],
                "device_key": gpu['DeviceKey'],
                "display_memory": gpu['DisplayMemory'],
                "dedicated_memory": gpu['DedicatedMemory'],
                "shared_memory": gpu['SharedMemory'],
                "current_mode": gpu['CurrentMode'],
                #"monitor_name": gpu['MonitorName'],
                #"monitor_id": gpu['MonitorId'],
                "vendor_id": gpu['VendorID'],
                "device_id": gpu['DeviceID'],
                "subsys_id": gpu['SubSysID']
            }
            gpus[index] = gpu_info
            index = index + 1
        return gpus

    def getSound():
        if not os.path.exists(report_path):
            info = genReport()
        else:
            report = open(report_path,"r")
            xml = report.read()
            report.close()
            info = xmltodict.parse(xml)
        devices = info['DxDiag']['DirectSound']
        sound = {
            "sound_device": {
                "caption": devices['SoundDevices']['SoundDevice']['Description'],
                "hardware_id": devices['SoundDevices']['SoundDevice']['HardwareID']
            },
            "sound_capture_device":{
                "caption": devices['SoundCaptureDevices']['SoundCaptureDevice']['Description'],
            }
        }
        return sound

class Linux:
    def getInfo():
        information = {
            "system": {
                "name": dxdiag['SystemInformation']['MachineName'],            
                "manufacturer": dxdiag['SystemInformation']['SystemManufacturer'],
                "model": dxdiag['SystemInformation']['SystemModel'],
                "os": dxdiag['SystemInformation']['OperatingSystem'],
                "language": dxdiag['SystemInformation']['Language'],
                "bios": dxdiag['SystemInformation']['BIOS']
            },
            "cpu": {
                "model": subprocess.check_output(['bash','-c','less /proc/cpuinfo | grep "model name" | head -1']).decode('utf-8').strip()[13:]
                "real_cpu": psutil.cpu_count(logical=False),
                "logical_cpu": psutil.cpu_count(logical=True),
                "max_cpu_freq": psutil.cpu_freq()[2]
            },
            "gpu": getGpu(),
            "ram": {
                "total_ram": dxdiag['SystemInformation']['Memory'][:4],
                "swap_ram": bytes2human(psutil.swap_memory()[0])
            },
            "disk": getDisks(),
            "sound": getSound(),
            "net": {},
            "misc": {
                "boot_time": datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S"),
                "users": getUsers(),
                "battery": getBattery()
            }
        }
        print(json.dumps(information,indent=4))
        return json.dumps(information)