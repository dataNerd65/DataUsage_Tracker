import subprocess
import datetime
import os

def get_available_interfaces():
    result = subprocess.run(['vnstat', '--iflist'], stdout=subprocess.PIPE)
    output = result.stdout.decode('utf-8').strip()
    interfaces = output.split(':')[1].strip().split()
    return interfaces

def get_data_usage(interface):
    result = subprocess.run(['vnstat', '-i', interface, '--oneline'], stdout=subprocess.PIPE)
    output = result.stdout.decode('utf-8').strip()

    if "Error" in output:
        return None, None

    data = output.split(';')
    if len(data) > 4:
        rx_mib = data[3]  # Received data in MiB
        tx_mib = data[4]  # Transmitted data in MiB

        # Convert MiB to MB
        rx_mb = float(rx_mib.split()[0]) * 1.048576
        tx_mb = float(tx_mib.split()[0]) * 1.048576

        return rx_mb, tx_mb
    else:
        print(f"Unexpected vnstat output format for {interface}: {output}")
        return None, None

def log_data_usage(interface, log_file, daily_usage):
    rx_mb, tx_mb = get_data_usage(interface)
    if rx_mb is not None and tx_mb is not None:
        daily_usage[interface]['rx'] += rx_mb
        daily_usage[interface]['tx'] += tx_mb
    else:
        print(f"Failed to log data usage for {interface}")

def reset_log_file(log_file):
    with open(log_file, 'w') as f:
        f.write("Date, Interface, RX (MB), TX (MB)\n")

def log_daily_summary(log_file, daily_usage):
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(log_file, 'a') as f:
        for interface, usage in daily_usage.items():
            f.write(f"{now}, {interface}, RX: {usage['rx']:.2f} MB, TX: {usage['tx']:.2f} MB\n")

if __name__ == "__main__":
    interfaces = ['enp0s31f6', 'wlp1s0']
    log_file = '/home/peter-kiarie/System_Testing/Data_logfile'  # Path to logfile

    # Initialize daily usage dictionary
    daily_usage = {interface: {'rx': 0.0, 'tx': 0.0} for interface in interfaces}

    # Reset log file at midnight
    if datetime.datetime.now().strftime('%H:%M') == '00:00':
        log_daily_summary(log_file, daily_usage)
        reset_log_file(log_file)
        daily_usage = {interface: {'rx': 0.0, 'tx': 0.0} for interface in interfaces}

    available_interfaces = get_available_interfaces()
    for interface in interfaces:
        if interface in available_interfaces:
            log_data_usage(interface, log_file, daily_usage)
        else:
            print(f"Interface {interface} not found in vnstat database.")
    