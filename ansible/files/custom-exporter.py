
from slack_sdk import WebClient
from prometheus_client import start_http_server, Gauge
from hvac_lib import HVACClient
import psutil, time, socket, subprocess, re
from datetime import datetime, timedelta

THRESHOLD_TIME = 5  # minutes
last_slack_msg = None
throttle_interval = timedelta(minutes=THRESHOLD_TIME)

def ping(host):
    try:
        process = subprocess.Popen(
            ["ping", "-c", "1", host],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        output, error = process.communicate()
        if error:
            return None
        rtt_match = re.search(r"time=([\d.]+) ms", output.decode())
        print(rtt_match)
        if rtt_match:
            rtt = float(rtt_match.group(1))
            return rtt
        else:
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def exceeds_threshold(value, threshold, state):
    
    now = datetime.now()
    # Technically, this check is not needed since the function is only called when the value exceeds the threshold, but it is kept for clarity and a sanity check.
    if value > threshold:
        if state['start_time'] is None:
            state['start_time'] = now
        elif (now - state['start_time']) > timedelta(minutes=THRESHOLD_TIME) and state['alerted'] is False:
            state['alerted'] = True
            return True
    else:
        state['start_time'] = None
        state['alerted'] = False
    return False
    

def send_slack_message(bot_token, channel, message):
    # It uses the Slack SDK to send the message and handles throttling to avoid sending too many messages in a short time.
    global last_slack_msg
    now = datetime.now()
    # Initialize the Slack client
    client = WebClient(token=bot_token)
    
    # Send the message to Slack
    if last_slack_msg is None or (now - last_slack_msg) >= throttle_interval:
        try:
            response = client.chat_postMessage(
                channel=channel,
                text=message
            )
            last_slack_msg = now
            return response
        except Exception as e:
            print(f"Error sending message to Slack: {e}")
            return None

def collect_metrics():
    # Connect to Vault to retrieve the Slack API bot token
    vault_client = HVACClient()
    slack_token = vault_client.read("secret/data/slack_api_token")["bot_token"]
    # Get the hostname and IP address of the machine
    # This is useful for identifying the machine in the Slack message
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)

    cpu_usage = Gauge('custom_cpu_usage_percent', 'CPU usage percentage')
    memory_usage = Gauge('custom_memory_usage_percent', 'Memory usage percentage')
    disk_usage = Gauge('custom_disk_usage_percent', 'Disk usage percentage')
    network_latency = Gauge('custom_network_latency', 'Network latency in ms')

    # Define a list of process names to check useful for monitoring production processes
    required_processes = ["etcd","kubelet","coredns"]
    # Get the list of currently running processes
    running_processes = [proc.info['name'] for proc in psutil.process_iter(['name'])]
    # Check if each required process is running
    missing_processes = [proc for proc in required_processes if proc not in running_processes]
    state = {'start_time': None, 'alerted': False}

    while True:
        # Check network latency to a specific host
        latency = ping("8.8.8.8")
        if latency is not None:
            network_latency.set(latency)
        # Retrieve system metrics
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        # Set the metrics for Prometheus
        cpu_usage.set(cpu)
        memory_usage.set(memory)
        disk_usage.set(disk)


        # Check if the CPU or memory usage exceeds 80% for more than 5 minutes
        # Commented out the missing_processes check for now, but it can be uncommented if needed as it is useful for monitoring production processes

        if cpu > 80 and exceeds_threshold(cpu, 80, state):
            send_slack_message(slack_token, '#monitoring', f"High CPU usage detected: {cpu}% on {hostname} - ({ip_address}) for over 5 minutes")
        if memory > 80 and exceeds_threshold(memory, 80, state):
            send_slack_message(slack_token, '#monitoring', f"High Memory usage detected: {memory}% on {hostname} - ({ip_address}) for over 5 minutes")
        if disk > 80:
            send_slack_message(slack_token, '#monitoring', f"High Disk usage detected: {disk}% on {hostname} - ({ip_address})")
        if latency is not None and latency > 200:
            send_slack_message(slack_token, '#monitoring', f"High network latency detected: {latency}ms on {hostname} - ({ip_address})")
        # if missing_processes:
        #     send_slack_message(slack_token, '#monitoring', f"Missing processes detected: {', '.join(missing_processes)} on {hostname} - ({ip_address})")

        time.sleep(15)

if __name__ == "__main__":
    # Start the Prometheus server
    start_http_server(9101) 
    # Define the metrics
    collect_metrics()