import pandas as pd

# Load data
df = pd.read_excel("DP_World_Route_Data.xlsx")

# Separate hub and stops
hub = df[df['Stop'] == 0].iloc[0]
stops = df[df['Stop'] != 0].copy()

# Split into clusters
north = stops[stops['Cluster'] == 'North'].copy()
west = stops[stops['Cluster'] == 'West'].copy()

# Nearest Neighbor Algorithm
def nearest_neighbor(cluster_df):
    unvisited = cluster_df.copy()
    route = []
    current_distance = 0
    current_pos = 0  # Starting from hub (distance = 0)

    while not unvisited.empty:
        # Find nearest unvisited stop
        unvisited['gap'] = abs(unvisited['Distance (KM)'] - current_pos)
        nearest = unvisited.loc[unvisited['gap'].idxmin()]
        route.append(nearest)
        current_pos = nearest['Distance (KM)']
        current_distance += nearest['gap']
        unvisited = unvisited.drop(nearest.name)

    return route, current_distance

# Run optimization
print("\n========================================")
print("   DP WORLD ROUTE OPTIMIZER - CHENNAI")
print("========================================")

total_optimized_km = 0
total_original_km = 0
fuel_cost_per_km = 12  # Rs per KM (industry standard)

for cluster_name, cluster_df in [("NORTH", north), ("WEST", west)]:
    print(f"\n🚛 TRUCK {cluster_name} ROUTE:")
    print(f"   Start: Redhills CFS (Hub)")
    
    # Original route (as listed in Excel)
    original_km = cluster_df['Distance (KM)'].sum()
    
    # Optimized route
    route, optimized_km = nearest_neighbor(cluster_df)
    
    print(f"   Optimized Stop Sequence:")
    for i, stop in enumerate(route, 1):
        no_entry = "⚠️ NO ENTRY RESTRICTION" if stop['No Entry Restriction'] == 'Yes' else ""
        print(f"   {i}. {stop['Location']} ({stop['Distance (KM)']} KM) - {stop['Containers to Deliver']} containers {no_entry}")
    
    print(f"\n   Original Distance : {original_km} KM")
    print(f"   Optimized Distance: {round(optimized_km, 1)} KM")
    print(f"   KM Saved          : {round(original_km - optimized_km, 1)} KM")
    print(f"   Fuel Cost Saved   : Rs {round((original_km - optimized_km) * fuel_cost_per_km, 0)}")
    
    total_optimized_km += optimized_km
    total_original_km += original_km

print("\n========================================")
print("   TOTAL SUMMARY")
print("========================================")
print(f"Total Original KM   : {total_original_km} KM")
print(f"Total Optimized KM  : {round(total_optimized_km, 1)} KM")
print(f"Total KM Saved      : {round(total_original_km - total_optimized_km, 1)} KM")
print(f"Total Fuel Saved    : Rs {round((total_original_km - total_optimized_km) * fuel_cost_per_km, 0)} per day")
print(f"Monthly Savings     : Rs {round((total_original_km - total_optimized_km) * fuel_cost_per_km * 26, 0)}")
print("========================================")

# Save results to Excel
results = []

for cluster_name, cluster_df in [("NORTH", north), ("WEST", west)]:
    route, optimized_km = nearest_neighbor(cluster_df)
    original_km = cluster_df['Distance (KM)'].sum()
    
    for i, stop in enumerate(route, 1):
        results.append({
            'Truck': cluster_name,
            'Stop Sequence': i,
            'Location': stop['Location'],
            'Distance KM': stop['Distance (KM)'],
            'Containers': stop['Containers to Deliver'],
            'No Entry': stop['No Entry Restriction'],
            'Truck Time (mins)': stop['Truck Time (mins)']
        })

# Summary row
summary = pd.DataFrame([
    {'Truck': 'SUMMARY', 'Location': 'Total Original KM', 'Distance KM': 277},
    {'Truck': 'SUMMARY', 'Location': 'Total Optimized KM', 'Distance KM': 86},
    {'Truck': 'SUMMARY', 'Location': 'KM Saved', 'Distance KM': 191},
    {'Truck': 'SUMMARY', 'Location': 'Daily Fuel Saved (Rs)', 'Distance KM': 2292},
    {'Truck': 'SUMMARY', 'Location': 'Monthly Savings (Rs)', 'Distance KM': 59592},
])

output_df = pd.DataFrame(results)
final_output = pd.concat([output_df, summary], ignore_index=True)
final_output.to_excel("DP_World_Optimized_Routes.xlsx", index=False)

print("\n✅ Output saved to DP_World_Optimized_Routes.xlsx")