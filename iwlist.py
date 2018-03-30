import re
import subprocess

cellNumberRe = re.compile(r"^Cell\s+(?P<cellnumber>.+)\s+-\s+Address:\s(?P<mac>.+)$")
iwlist_regexps = [
    re.compile(r"^ESSID:\"(?P<essid>.*)\"$"),
    re.compile(r"^Protocol:(?P<protocol>.+)$"),
    re.compile(r"^Mode:(?P<mode>.+)$"),
    re.compile(r"^Frequency:(?P<frequency>[\d.]+) (?P<frequency_units>.+) \(Channel (?P<channel>\d+)\)$"),
    re.compile(r"^Encryption key:(?P<encryption>.+)$"),
    re.compile(r"^Quality=(?P<signal_quality>\d+)/(?P<signal_total>\d+)\s+Signal level=(?P<signal_level_dBm>.+) d.+$"),
    re.compile(r"^Signal level=(?P<signal_quality>\d+)/(?P<signal_total>\d+).*$"),
]

iwconfig_regexps = [
    re.compile(r"ESSID:\"(?P<essid>.*)\"$"),
    re.compile(r"Access Point: (?P<mac>.+)$"),
]

# Runs the comnmand to scan the list of networks.
# Must run as super user.
def scan(interface='wlan0'):
    # First check if we're connected to anything
    cmd = ["iwconfig", interface]
    lines = subprocess.check_output(cmd)
    lines = lines.decode('utf-8').split('\n')
    connection = {}
    for line in lines:
        line = line.strip()
        for expression in iwconfig_regexps:
            result = expression.search(line)
            if result is not None:
                connection.update(result.groupdict())
                continue
    # Now parse the wireless scan
    cmd = ["iwlist", interface, "scan"]
    lines = subprocess.check_output(cmd)
    lines = lines.decode('utf-8').split('\n')
    cells = []
    for line in lines:
        line = line.strip()
        cellNumber = cellNumberRe.search(line)
        if cellNumber is not None:
            cells.append(cellNumber.groupdict())
            cells[-1]['connected'] = cells[-1]['mac'] == connection.get('mac', None)
            continue
        for expression in iwlist_regexps:
            result = expression.search(line)
            if result is not None:
                cells[-1].update(result.groupdict())
                continue
    return cells

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        wireless_int = sys.argv[1]
    else:
        wireless_int = 'wlan0'

    print(scan(wireless_int))
