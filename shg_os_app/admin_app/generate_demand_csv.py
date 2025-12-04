import pandas as pd
import numpy as np

# 40 districts (India-wide)
district_data = [
    ("Gujarat", "Ahmedabad", 23.0225, 72.5714),
    ("Gujarat", "Surat", 21.1702, 72.8311),
    ("Gujarat", "Vadodara", 22.3072, 73.1812),
    ("Rajasthan", "Jaipur", 26.9124, 75.7873),
    ("Rajasthan", "Udaipur", 24.5854, 73.7125),
    ("Rajasthan", "Jodhpur", 26.2389, 73.0243),
    ("Maharashtra", "Mumbai", 19.0760, 72.8777),
    ("Maharashtra", "Pune", 18.5204, 73.8567),
    ("Maharashtra", "Nagpur", 21.1458, 79.0882),
    ("Madhya Pradesh", "Indore", 22.7196, 75.8577),
    ("Madhya Pradesh", "Bhopal", 23.2599, 77.4126),
    ("Madhya Pradesh", "Gwalior", 26.2183, 78.1828),
    ("Uttar Pradesh", "Lucknow", 26.8467, 80.9462),
    ("Uttar Pradesh", "Kanpur", 26.4499, 80.3319),
    ("Uttar Pradesh", "Varanasi", 25.3176, 82.9739),
    ("Bihar", "Patna", 25.5941, 85.1376),
    ("Bihar", "Gaya", 24.7914, 85.0002),
    ("Bihar", "Bhagalpur", 25.2417, 86.9842),
    ("Tamil Nadu", "Chennai", 13.0827, 80.2707),
    ("Tamil Nadu", "Coimbatore", 11.0168, 76.9558),
    ("Tamil Nadu", "Madurai", 9.9252, 78.1198),
    ("Karnataka", "Bengaluru", 12.9716, 77.5946),
    ("Karnataka", "Mysuru", 12.2958, 76.6394),
    ("Karnataka", "Hubli", 15.3647, 75.1240),
    ("Telangana", "Hyderabad", 17.3850, 78.4867),
    ("Telangana", "Warangal", 17.9784, 79.5941),
    ("Andhra Pradesh", "Vijayawada", 16.5062, 80.6480),
    ("Andhra Pradesh", "Visakhapatnam", 17.6868, 83.2185),
    ("Odisha", "Bhubaneswar", 20.2961, 85.8245),
    ("Odisha", "Cuttack", 20.4625, 85.8830),
    ("West Bengal", "Kolkata", 22.5726, 88.3639),
    ("West Bengal", "Asansol", 23.6739, 86.9524),
    ("Jharkhand", "Ranchi", 23.3441, 85.3096),
    ("Jharkhand", "Jamshedpur", 22.8046, 86.2029),
    ("Kerala", "Kochi", 9.9312, 76.2673),
    ("Kerala", "Thiruvananthapuram", 8.5241, 76.9366),
    ("Punjab", "Amritsar", 31.6340, 74.8723),
    ("Punjab", "Ludhiana", 30.9010, 75.8573),
    ("Assam", "Guwahati", 26.1445, 91.7362),
    ("Assam", "Dibrugarh", 27.4728, 94.9120),
]

skill_categories = [
    "Tailoring","Papad Making","Pickle Making","Pottery","Bag Stitching",
    "Goat Rearing","Dairy Farming","Spice Grinding","Handicraft","Beautician",
    "Embroidery","Textile Weaving","Snacks Making","Candle Making","Incense Stick Making"
]

rows = []
rng = np.random.default_rng(42)

for state, district, lat, lon in district_data:
    for skill in skill_categories:
        demand = int(rng.integers(2000, 50000))
        priority = int(rng.integers(1, 6))
        rows.append({
            "state": state,
            "district": district,
            "latitude": lat,
            "longitude": lon,
            "skill_category": skill,
            "monthly_demand": demand,
            "priority_level": priority,
        })

df = pd.DataFrame(rows)
df.to_csv("india_district_demand_large.csv", index=False)

print("CSV created:", len(df), "rows")
