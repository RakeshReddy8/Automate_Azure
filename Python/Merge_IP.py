import ipaddress

# Read the IP addresses and subnets from a file
with open('input.txt', 'r') as f:
    lines = [line.strip() for line in f]

# Convert each line to an IPv4Network object and add it to a list
networks = []
for line in lines:
    network = ipaddress.IPv4Network(line)
    networks.append(network)

# Merge the networks into the smallest possible set of subnets
merged_networks = ipaddress.collapse_addresses(networks)

# Write the merged subnets to a file
with open('output.txt', 'w') as f:
    for network in merged_networks:
        f.write(str(network) + '\n') 
