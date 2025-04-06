import streamlit as st

# Conversion dictionary for game notations to scientific notation
NOTATION_CONVERSION = {
    'K': 'e3', 'M': 'e6', 'B': 'e9', 'T': 'e12', 'Qa': 'e15', 'Qt': 'e18',
    'Sx': 'e21', 'Sp': 'e24', 'Oc': 'e27', 'No': 'e30', 'Dc': 'e33', 
    'UDc': 'e36', 'DDc': 'e39', 'TDc': 'e42', 'QaDc': 'e45', 'QtDc': 'e48',
    'SxDc': 'e51', 'SpDc': 'e54', 'ODc': 'e57', 'NDc': 'e60', 'Vg': 'e63',
    'UVg': 'e66', 'DVg': 'e69', 'TVg': 'e72', 'QaVg': 'e75', 'QtVg': 'e78',
    'SxVg': 'e81', 'SpVg': 'e84', 'OVg': 'e87', 'NVg': 'e90', 'Tg': 'e93',
    'UTg': 'e96', 'DTg': 'e99', 'TTg': 'e102', 'QaTg': 'e105', 'QtTg': 'e108',
    'SxTg': 'e111', 'SpTg': 'e114', 'OTg': 'e117', 'NTg': 'e120', 'Qd': 'e123',
    'UQd': 'e126', 'DQd': 'e129', 'TQd': 'e132', 'QaQd': 'e135', 'QtQd': 'e138',
    'SxQd': 'e141', 'SpQd': 'e144', 'OQd': 'e147', 'NQd': 'e150', 'Qi': 'e153',
    'UQi': 'e156', 'DQi': 'e159', 'TQi': 'e162', 'QaQi': 'e165', 'QtQi': 'e168',
    'SxQi': 'e171', 'SpQi': 'e174', 'OQi': 'e177', 'NQi': 'e180', 'Se': 'e183',
    'USe': 'e186', 'DSe': 'e189', 'TSe': 'e192', 'QaSe': 'e195', 'QtSe': 'e198',
    'SxSe': 'e201', 'SpSe': 'e204'
}

def convert_game_notation_to_number(value):
    """Convert game notation (like 10NQd) to a float number"""
    if not value:
        return 0.0
    # Check if the value is already in scientific notation
    if 'e' in value:
        try:
            return float(value)
        except ValueError:
            return 0.0
    # Find the alphabetical part
    alpha_part = ''
    num_part = ''
    for char in value:
        if char.isalpha():
            alpha_part += char
        else:
            num_part += char
    if not alpha_part:  # No notation, just a regular number
        try:
            return float(value)
        except ValueError:
            return 0.0
    # Handle cases where decimal is omitted (like "10NQd" instead of "10.0NQd")
    if '.' not in num_part and num_part:
        num_part += '.0'
    # Get the exponent from the notation
    exponent = NOTATION_CONVERSION.get(alpha_part, 'e0')
    try:
        number = float(num_part + exponent)
    except ValueError:
        return 0.0
    return number

def calc_efficiency(upgrades):
    results = []
    level_comparisons = []
    for i, upgrade in enumerate(upgrades, 1):
        bonus = upgrade['bonus']
        cost = upgrade['cost']
        eff_cost = upgrade['eff_cost'] if upgrade['eff_upgrade'] else None
        unlocked = upgrade['unlocked']
        
        if not unlocked:
            continue
        
        bonus_num = convert_game_notation_to_number(bonus)
        cost_num = convert_game_notation_to_number(cost)
        
        if cost_num == 0:
            continue
        
        normal_efficiency = bonus_num / cost_num
        results.append((f"Upgrade {i} (Normal)", normal_efficiency, bonus_num, cost_num))
        
        if eff_cost:
            eff_cost_num = convert_game_notation_to_number(eff_cost)
            doubled_bonus = bonus_num * 2
            eff_efficiency = doubled_bonus / eff_cost_num
            results.append((f"Upgrade {i} (Efficiency)", eff_efficiency, doubled_bonus, eff_cost_num))
            
            # Compare normal vs efficiency
            if eff_efficiency > normal_efficiency:
                diff_percent = ((eff_efficiency - normal_efficiency) / normal_efficiency) * 100
                comparison = f"Level {i}: 🟢 Efficiency upgrade is {diff_percent:.1f}% better"
            elif eff_efficiency < normal_efficiency:
                diff_percent = ((normal_efficiency - eff_efficiency) / eff_efficiency) * 100
                comparison = f"Level {i}: 🔴 Normal upgrade is {diff_percent:.1f}% better"
            else:
                comparison = f"Level {i}: ⚪ Both upgrades are equally efficient"
            level_comparisons.append(comparison)
    
    if not results:
        return "No upgrades selected or all have zero cost!"
    
    # Sort by efficiency
    results.sort(key=lambda x: -x[1])
    
    # Prepare results text
    result_text = "🔹 UPGRADE COMPARISONS BY LEVEL 🔹\n"
    result_text += "\n".join(level_comparisons) + "\n"
    result_text += "🏆 ALL UPGRADES RANKED BY EFFICIENCY 🏆\n"
    
    for i, (name, eff, bonus, cost) in enumerate(results, 1):
        medal = ""
        if i == 1: medal = "🥇 "
        elif i == 2: medal = "🥈 "
        elif i == 3: medal = "🥉 "
        result_text += f"{medal}{name}: {eff:.2e} efficiency\n"
        result_text += f"   Bonus: {bonus:.2e} | Cost: {cost:.2e}\n"
    
    result_text += f"\n✨ OVERALL BEST OPTION ✨\n{results[0][0]} with efficiency {results[0][1]:.2e}"
    return result_text

# Streamlit App Layout
st.title("🎮 Upgrade Efficiency Checker")
st.write("Optimize your upgrade path for maximum efficiency!")

# Input fields for 5 upgrades
upgrades = []
for i in range(1, 6):
    st.subheader(f"⚙️ Upgrade Level {i}")
    unlocked = st.checkbox(f"Unlocked", key=f"unlock_{i}", value=True)
    bonus = st.text_input(f"Bonus Value:", key=f"bonus_{i}", help="Example: 10NQd or 1.23e150")
    cost = st.text_input(f"Cost:", key=f"cost_{i}", help="Example: 10NQd or 1.23e150")
    eff_upgrade = st.checkbox(f"Efficiency Upgrade Available", key=f"eff_unlock_{i}")
    eff_cost = st.text_input(f"Eff. Cost:", key=f"eff_cost_{i}") if eff_upgrade else ""
    upgrades.append({
        "unlocked": unlocked,
        "bonus": bonus,
        "cost": cost,
        "eff_upgrade": eff_upgrade,
        "eff_cost": eff_cost
    })

# Calculate Button
if st.button("🔍 Compare Upgrades"):
    result_text = calc_efficiency(upgrades)
    st.markdown(result_text)

# Footer
st.write("💬 Join our Discord for more help!")
st.write("[Discord Link](https://discord.gg/tcgvB36KDQ)")