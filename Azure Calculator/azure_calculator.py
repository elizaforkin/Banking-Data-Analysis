import requests

# --- CONFIGURATION & API HELPERS ---

def get_live_exchange_rates():
    """
    Fetches live currency rates from a public API.
    Returns a dictionary of rates relative to 1 USD.
    """
    try:
        # Using a free, no-key-required API for live rates
        url = "https://open.er-api.com/v6/latest/USD"
        response = requests.get(url)
        data = response.json()
        return data.get("rates", {})
    except Exception as e:
        print(f"⚠️ Warning: Could not fetch live rates ({e}). Using defaults.")
        # Fallback rates if the internet is down
        return {"USD": 1.0, "AUD": 1.52, "EUR": 0.92}

def get_azure_price(sku, region_tech_name):
    """
    Connects to Microsoft Azure Retail Prices API to get real-time hourly costs.
    """
    sku = sku.strip()
    # Official Azure Prices API URL with filters
    url = (
        f"https://prices.azure.com/api/retail/prices?api-version=2023-01-01-preview"
        f"&$filter=serviceName eq 'Virtual Machines' and "
        f"armRegionName eq '{region_tech_name}' and "
        f"armSkuName eq '{sku}' and "
        f"priceType eq 'Consumption'"
    )
    
    try:
        response = requests.get(url)
        data = response.json()
        items = data.get('Items', [])
        for item in items:
            # We filter for 'Consumption' (Pay-As-You-Go) and avoid Windows/Spot/Reservations
            if 'Reservation' not in item['meterName'] and 'Spot' not in item['meterName'] and 'Windows' not in item['productName']:
                return item['retailPrice']
        return None
    except Exception:
        return None

def get_number(prompt):
    """Helper function to prevent the program from crashing if a user enters text."""
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("❌ Invalid input. Please enter a number.")

# --- MAIN CALCULATOR ENGINE ---

def run_calculator():
    # 1. Initialize live data
    live_rates = get_live_exchange_rates()
    
    print("\n" + "="*60)
    print("      🌍 GLOBAL AZURE COST ESTIMATOR (LIVE FX VERSION)")
    print("="*60)

    # 2. Define Region Mapping (Technical Name vs Display Name)
    region_options = {
        "1": ("australiaeast", "Australia East (Sydney)"),
        "2": ("australiasoutheast", "Australia South East (Melbourne)"),
        "3": ("eastus", "East US (Virginia)"),
        "4": ("northeurope", "North Europe (Ireland)"),
        "5": ("westeurope", "West Europe (Netherlands)"),
        "6": ("southeastasia", "South East Asia (Singapore)")
    }

    print("Select a Global Region:")
    for key, (tech, display) in region_options.items():
        print(f"{key}. {display}")
    
    reg_choice = input("\nEnter choice (1-6): ")
    selected_tech, selected_display = region_options.get(reg_choice, region_options["1"])

    # 3. Currency Selection with Live API Data
    print("\nSelect Output Currency:")
    print(f"1. USD ($) [Rate: 1.00]")
    print(f"2. AUD ($) [Live Rate: {live_rates.get('AUD'):.2f}]")
    print(f"3. EUR (€) [Live Rate: {live_rates.get('EUR'):.2f}]")
    
    curr_choice = input("Enter 1, 2, or 3: ")
    
    # Map selection to the live rate dictionary
    currency_map = {"1": "USD", "2": "AUD", "3": "EUR"}
    currency_label = currency_map.get(curr_choice, "USD")
    fx_multiplier = live_rates.get(currency_label, 1.0)

    # 4. Azure SKU Lookup
    print(f"\n--- Project Configuration [{selected_display}] ---")
    sku_name = input(f"Enter VM SKU (e.g., Standard_D2s_v3): ").strip()
    
    base_usd_rate = get_azure_price(sku_name, selected_tech)

    if base_usd_rate:
        # Convert the base USD price from Azure into the selected currency
        vm_rate = base_usd_rate * fx_multiplier
        print(f"✅ Live Rate Found: {vm_rate:.4f} {currency_label}/hr")
    else:
        print(f"⚠️  SKU '{sku_name}' not found. Enter {currency_label} rate manually.")
        vm_rate = get_number(f"Enter hourly rate in {currency_label}: ")

    # 5. Usage Calculation
    vm_count = get_number("\nNumber of VMs: ")
    vm_hours = get_number("Monthly Hours (730 = 24/7): ")
    
    compute_total = vm_rate * vm_hours * vm_count
    
    # 6. Final Financial Reporting
    print("\n" + "="*60)
    print(f"{'GLOBAL COST ESTIMATE (' + currency_label + ')':^60}")
    print("-" * 60)
    print(f"{'Data Center':<25} | {selected_display}")
    print(f"{'VM Hardware':<25} | {sku_name}")
    print(f"{'Exchange Rate (1 USD)':<25} | {fx_multiplier:.4f} {currency_label}")
    print(f"{'Monthly Compute':<25} | {currency_label} ${compute_total:>15,.2f}")
    
    # Apply Australian GST if applicable
    if currency_label == "AUD" and "Australia" in selected_display:
        gst = compute_total * 0.10
        print(f"{'GST (10%)':<25} | {currency_label} ${gst:>15,.2f}")
        print(f"{'TOTAL INC. GST':<25} | {currency_label} ${compute_total + gst:>15,.2f}")
    
    print("="*60 + "\n")

if __name__ == "__main__":
    run_calculator()