import subprocess
import datetime
import os

def get_available_interfaces():
    result = subprocess.run(['vnstat', '--iflist'], stdout=subprocess.PIPE)
    output = result.stdout.decode('utf-8').strip()
    print(f"Available interfaces: {output}") # Debugging
    interfaces = output.split(':')[1].strip().split()
    return interfaces

def get_data_usage(interface):
    result = subprocess.run(['vnstat', '-i', interface, '--oneline'], stdout=subprocess.PIPE)
    output = result.stdout.decode('utf-8').strip()
    print(f"vnstat output for {interface}: {output}") # Debugging

    if "Error" in output:
        print(f"Error: {output}")
        return None, None
   
    data = output.split(';')
    if len(data) > 4:
        rx_mib = data[3] # Received data
        tx_mib = data[4] # Transmitted data

        # Convert MiB to MB
        rx_mb = float(rx_mib.split()[0]) * 1.048576
        tx_mb = float(tx_mib.split()[0]) * 1.048576
        return rx_mib, tx_mib, rx_mb, tx_mb
    else:
        print(f"Unexpected vnstat output format for {interface}: {output}")
        return None, None, None, None

def log_data_usage(interface, log_file):
    rx_mib, tx_mib, rx_mb, tx_mb = get_data_usage(interface)
    if rx_mib is not None and tx_mib is not None:
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(log_file, 'a') as f:
            f.write(f"{now}, {interface}, RX(Received): {rx_mib} ({rx_mb:.2f} MB), TX(Transmitted): {tx_mib} ({tx_mb:.2f} MB)\n")
    else:
        print(f"Failed to log data usage for {interface}")
def reset_log_file(log_file):
    with open(log_file, 'w') as f:
        f.write("Date, Interface, RX (MiB), RX (MB), TX (MiB), TX (MB)\n")

if __name__ == "__main__":
    interfaces = ['enp0s31f6', 'wlp1s0'] # Severe correction needed
    log_file = '/home/peter-kiarie/System_Testing/Data_logfile' # Path to logfile

    # Resetting logfile at midnight
    if datetime.datetime.now().strftime('%H:%M') == '00:00':
        reset_log_file(log_file)

    available_interfaces = get_available_interfaces()
    for interface in interfaces:
        if interface in available_interfaces:
            log_data_usage(interface, log_file)
        else:
            print(f"Interface {interface} not found in vnstat database.")

    