import ipaddress

# Get input from user
ip_input = input("Enter an IP address and subnet mask in CIDR notation (e.g. 192.168.1.1/29): ")

# Parse the input into an IPv4Network object
subnet = ipaddress.IPv4Network(ip_input)

# Print the list of IP addresses in the subnet
for ip in subnet:
    print(ip)
