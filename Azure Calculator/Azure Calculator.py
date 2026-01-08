#Step 1: Get user inputs
vm_count = input("Enter VM count: ")
vm_hours = input("Enter VM hours: ")
vm_rate = input("Enter VM rate: ")

storage_gb = input("Enter Storage GB: ")
storage_rate = input("Enter Storage rate: ")

egress_gb = input("Enter Outbound Data transfer in GB: ")
egress_rate = input("Enter Outbound Data transfer rate: ")

#Step 2: Do the math
compute_cost = float(vm_hours) * float(vm_rate) * float(vm_count)
storage_cost = float(storage_gb) * float(storage_rate)
network_cost = float(egress_gb) * float(egress_rate)
total_cost = compute_cost + storage_cost + network_cost

#Step 3: Print the results
print(f"Compute Cost: ${compute_cost:.2f}")
print(f"Storage Cost: ${storage_cost:.2f}")
print(f"Network Cost: ${network_cost:.2f}")
print(f"Total Cost: ${total_cost:.2f}")


