import streamlit as st
import re
import webbrowser

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
    exponent = NOTATION_CONVERSION.get(alpha_part, 'e0')
    try:
        number = float(num_part + exponent)
    except ValueError:
        return 0.0
    return number

def get_area_specific_advice(area):
    """Provide tailored advice based on the selected area."""
    advice = ""
    if area == "Early Game (A1-A3)":
        advice = """
        🟩 Early Game Tips:
        - Focus on unlocking perks like Instant Reload.
        - Prioritize pet hatching and mutations.
        - Farm shards at the Christmas event for quick progress.
        - Prestige only when necessary (after tutorial).
        """
    elif area == "Mid Game (A4)":
        advice = """
        🟨 Mid Game Tips:
        - Farm the A4 meteor for shards and eggs.
        - Maximize your Prestige upgrades before advancing.
        - Hatch and mutate pets before entering A5.
        - Balance stone collection with pet upgrades.
        """
    elif area == "Late Game (A5+)":
        advice = """
        🔴 Late Game Tips:
        - Focus on maxing shard sinks and Prestige Multiplier.
        - Join boss or meteor lobbies for maximum rewards.
        - Aim for 1b+ Prestige Multiplier before breaking A5 meteor solo.
        - Mutate all pets and invest in FS bonuses.
        """
    return advice

def calc_efficiency(upgrades, total_resources=None):
    results = []
    level_comparisons = []
    for i, upgrade in enumerate(upgrades, 1):
        bonus = convert_game_notation_to_number(upgrade['bonus'])
        cost = convert_game_notation_to_number(upgrade['cost'])
        eff_cost = convert_game_notation_to_number(upgrade['eff_cost']) if upgrade['eff_upgrade'] else 0
        
        if cost == 0:
            continue
        
        normal_efficiency = bonus / cost * 100  # Convert to percentage
        time_to_buy = "N/A"
        if total_resources is not None:
            current_resources = convert_game_notation_to_number(total_resources)
            if current_resources < cost:
                time_to_buy = f"{(cost - current_resources):.2e}"
        results.append((f"Upgrade {i} (Normal)", normal_efficiency, bonus, cost, time_to_buy))
        
        # Compare with efficiency upgrade if available
        if upgrade['eff_upgrade'] and eff_cost != 0:
            doubled_bonus = bonus * 2
            eff_efficiency = doubled_bonus / eff_cost * 100  # Convert to percentage
            results.append((f"Upgrade {i} (Efficiency)", eff_efficiency, doubled_bonus, eff_cost, "N/A"))
            
            # Level comparison
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
        return "No valid upgrades found!"
    
    # Sort by efficiency
    results.sort(key=lambda x: -x[1])
    
    # Prepare results text
    result_text = "🔹 UPGRADE COMPARISONS BY LEVEL 🔹\n"
    result_text += "\n".join(level_comparisons) + "\n"
    result_text += "🏆 ALL UPGRADES RANKED BY EFFICIENCY 🏆\n"
    
    for i, (name, eff, bonus, cost, time_to_buy) in enumerate(results, 1):
        medal = ""
        if i == 1: medal = "🥇 "
        elif i == 2: medal = "🥈 "
        elif i == 3: medal = "🥉 "
        result_text += f"{medal}{name}: {eff:.1f}% efficiency\n"
        result_text += f"   Bonus: {bonus:.2e} | Cost: {cost:.2e}\n"
        result_text += f"   Time to Buy: {time_to_buy}\n"
    
    result_text += f"\n✨ OVERALL BEST OPTION ✨\n{results[0][0]} with efficiency {results[0][1]:.1f}%"
    return result_text

# Streamlit App Layout
st.set_page_config(page_title="🎮 Upgrade Efficiency Checker", layout="wide")
st.title("🎮 Upgrade Efficiency Checker")
st.write("Optimize your upgrade path for maximum efficiency!")

# Sidebar for Help and Settings
with st.sidebar:
    st.header("⚙️ Settings & Help")
    st.markdown("""
    ### How to Use
    1. For each upgrade level (1-5):
       - Enter the **Bonus** and **Cost** values (e.g., `10NQd` or `1.23e150`).
       - Check the box if an **Efficiency Upgrade** is available and enter its cost.
    2. Enter your total resources (optional) to calculate time-to-buy estimates.
    3. Click **Compare Upgrades** to see:
       - Level-by-level comparisons (which is better).
       - All upgrades ranked by efficiency.
       - The absolute best option.
    4. Copy the results and paste them into Discord.
    
    ### Example Input
    - **Bonus:** `10NQd`
    - **Cost:** `70.4Qi`
    - **Efficiency Cost:** `140.8Qi`
    - **Total Resources:** `61.3Qi`
    
    ### Tips
    - You can use shorthand (e.g., `10NQd`) or precise (e.g., `10.03NQd`) values.
    - Decimal points are optional.
    """)
    discord_link = st.text_input("Discord Link", value="https://discord.com", help="Join our Discord for support!")
    if st.button("💬 Join Discord"):
        webbrowser.open(discord_link)

# Main Content
col1, col2 = st.columns([2, 1])

with col1:
    # Inputs for 5 upgrades
    upgrades = []
    for i in range(1, 6):
        st.subheader(f"⚙️ Upgrade Level {i}")
        unlocked = st.checkbox(f"Unlocked", key=f"unlocked_{i}", value=True)
        if unlocked:
            col1, col2, col3 = st.columns([2, 2, 1])
            bonus = col1.text_input(f"Bonus Value:", key=f"bonus_{i}", value="10NQd")
            cost = col2.text_input(f"Cost:", key=f"cost_{i}", value="1Qi")
            eff_upgrade = col3.checkbox(f"Efficiency Upgrade Available", key=f"eff_upgrade_{i}")
            eff_cost = ""
            if eff_upgrade:
                eff_cost = col2.text_input(f"Efficiency Cost:", key=f"eff_cost_{i}", value="2Qi")
            upgrades.append({
                "bonus": bonus,
                "cost": cost,
                "eff_upgrade": eff_upgrade,
                "eff_cost": eff_cost
            })

    # Total Resources Input
    total_resources = st.text_input("Enter your total resources (e.g., 61.3Qi)", help="Optional: Enter your saved resources to calculate time-to-buy.")

    # Calculate Button
    if st.button("🔍 Compare Upgrades"):
        result_text = calc_efficiency(upgrades, total_resources)
        st.markdown(result_text)

with col2:
    st.header("📋 Results Summary")
    st.info("Results will appear here after processing.")
    st.markdown("""
    ### Share Your Results
    - Copy the results and paste them into Discord.
    - Use the **💬 Join Discord** button to share feedback or ask questions.
    """)

# Area Selection Dropdown
area_var = st.selectbox("Select Your Current Area:", ["Early Game (A1-A3)", "Mid Game (A4)", "Late Game (A5+)"])
area_advice = get_area_specific_advice(area_var)
st.markdown("🎯 AREA-SPECIFIC TIPS:")
st.markdown(area_advice)

# Footer
st.write("💬 Join Discord for more help!")
st.write("[Discord Link](https://discord.gg/tcgvB36KDQ)")

# Additional Features
st.markdown("""
---
### Additional Features
- **Time-to-Buy Estimates**: Calculates how long it will take to afford upgrades based on your current resources.
- **Area-Specific Advice**: Provides tailored tips for Early, Mid, and Late Game.
- **Copy Results**: Easily copy results to share with your Discord community.
- **Scientific Notation Support**: Handles shorthand (e.g., `10NQd`) and precise (e.g., `10.03NQd`) inputs.
""")

# FAQ Section
with st.expander("❓ Frequently Asked Questions"):
    st.markdown("""
    #### Q: What is an Efficiency Upgrade?
    A: An Efficiency Upgrade doubles the bonus but costs significantly more. This tool helps you decide whether to buy the normal upgrade or the Efficiency Upgrade.
    
    #### Q: How do I use shorthand notations like `10NQd`?
    A: Simply type the number followed by the shorthand (e.g., `10NQd`). The tool automatically converts it into scientific notation.
    
    #### Q: Can I use this tool for any game?
    A: While it’s optimized for games with similar mechanics, you can adapt it for other games by modifying the conversion dictionary.
    """)

# Credits
st.markdown("""
---
### Credits
Developed by ka.i_  
Special thanks to the Discord community for feedback and support!
""")
