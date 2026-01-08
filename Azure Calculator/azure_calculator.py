import requests

def get_vm_rate(sku):
    """Fetch the real hourly price from Azure Retail Prices API."""
    # We filter by 'eastus' and 'Consumption' (Pay-As-You-Go) prices
    url = f"https://prices.azure.com/api/retail/prices?api-version=2023-01-01-preview&$filter=armRegionName eq 'eastus' and skuName eq '{sku}' and serviceName eq 'Virtual Machines' and priceType eq 'Consumption'"
    try:
        data = requests.get(url).json()
        for item in data.get('Items', []):
            # We skip 'Reservation' (prepaid) prices to get the standard rate
            if 'Reservation' not in item['meterName']:
                return item['retailPrice']
        return None
    except:
        return None

print("--- ☁️  Azure Calculator ---")
sku_name = input("Enter VM SKU (e.g., Standard_D2s_v3): ")

# API Lookup
auto_rate = get_vm_rate(sku_name)
if auto_rate:
    print(f"✅ Found Azure rate: ${auto_rate:.4f}/hr")
    vm_rate = auto_rate
else:
    print("⚠️  SKU not found. Enter rate manually.")
    vm_rate = float(input("Enter VM rate: "))

# Manual Inputs
vm_count = float(input("Enter VM count: "))
vm_hours = float(input("Enter VM hours (730 = 1 month): "))
storage_gb = float(input("Enter Storage GB: "))
storage_rate = float(input("Enter Storage rate (per GB): "))
egress_gb = float(input("Enter Outbound Data (GB): "))
egress_rate = float(input("Enter Outbound rate: "))

# Math
compute_cost = vm_hours * vm_rate * vm_count
storage_cost = storage_gb * storage_rate
network_cost = egress_gb * egress_rate
total_cost = compute_cost + storage_cost + network_cost

# Results
print("\n" + "="*35)
print(f"RESULTS FOR: {sku_name}")
print("-" * 35)
print(f"Compute Cost:   ${compute_cost:,.2f}")
print(f"Storage Cost:   ${storage_cost:,.2f}")
print(f"Network Cost:   ${network_cost:,.2f}")
print("-" * 35)
print(f"TOTAL MONTHLY:  ${total_cost:,.2f}")
print("="*35)