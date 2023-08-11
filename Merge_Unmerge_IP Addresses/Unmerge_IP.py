import ipaddress

# Open the input file in read-only mode
with open("merged_IP.txt", "r") as input_file:
    # Read all the lines in the input file
    input_lines = input_file.readlines()

# Open the output file in write mode
with open("unmerged_IP.txt", "w") as output_file:
    # Iterate over each line in the input file
    for line in input_lines:
        # Split the line into IP address and subnet mask
        ip_address, subnet_mask = line.strip().split("/")
        # Create an IPv4Network object with the IP address and subnet mask
        network = ipaddress.IPv4Network(line.strip())
        # Iterate over each IP address in the network
        for ip_address in network:
            # Write the IP address to the output file
            output_file.write(str(ip_address) + "\n")
