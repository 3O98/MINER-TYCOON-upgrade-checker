import streamlit as st
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
    if not alpha_part:
        try:
            return float(value)
        except ValueError:
            return 0.0
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

def calc_efficiency():
    """Calculate and compare upgrade efficiencies."""
    try:
        upgrades = []
        level_comparisons = []
        selected_area = st.session_state.area_var

        # Collect all regular upgrade data and compare with efficiency upgrades
        for i in range(1, 6):  # 5 upgrades
            bonus = st.session_state[f'bonus_{i}']
            cost = st.session_state[f'cost_{i}']
            unlocked = st.session_state[f'unlocked_{i}']
            if not unlocked:
                continue
            bonus_num = convert_game_notation_to_number(bonus)
            cost_num = convert_game_notation_to_number(cost)
            if cost_num == 0:
                continue
            normal_efficiency = bonus_num / cost_num
            upgrades.append((f"Upgrade {i}", normal_efficiency, bonus_num, cost_num, "Normal"))
            
            # Check efficiency upgrade if available
            if st.session_state[f'eff_upgrade_{i}']:
                eff_cost = convert_game_notation_to_number(st.session_state[f'eff_cost_{i}'])
                if eff_cost == 0:
                    continue
                doubled_bonus = bonus_num * 2
                eff_efficiency = doubled_bonus / eff_cost
                upgrades.append((f"Upgrade {i}", eff_efficiency, doubled_bonus, eff_cost, "Efficiency"))
                
                # Compare normal vs efficiency for this level
                if eff_efficiency > normal_efficiency:
                    diff_percent = ((eff_efficiency - normal_efficiency) / normal_efficiency) * 100
                    comparison = f"Level {i}: 🟢 Efficiency upgrade is {diff_percent:.1f}% better"
                elif eff_efficiency < normal_efficiency:
                    diff_percent = ((normal_efficiency - eff_efficiency) / eff_efficiency) * 100
                    comparison = f"Level {i}: 🔴 Normal upgrade is {diff_percent:.1f}% better"
                else:
                    comparison = f"Level {i}: ⚪ Both upgrades are equally efficient"
                level_comparisons.append(comparison)

        # Check if we have any upgrades to compare
        if not upgrades:
            st.error("No upgrades selected or all have zero cost!")
            return

        # Sort all upgrades by efficiency (highest first)
        upgrades.sort(key=lambda x: -x[1])

        # Prepare results text
        result_text = f"🔹 UPGRADE COMPARISONS BY LEVEL ({selected_area}) 🔹\n"
        result_text += "\n".join(level_comparisons) + "\n\n"
        result_text += "🏆 ALL UPGRADES RANKED BY EFFICIENCY 🏆\n"
        for i, (name, eff, bonus, cost, upgrade_type) in enumerate(upgrades, 1):
            medal = ""
            if i == 1: medal = "🥇 "
            elif i == 2: medal = "🥈 "
            elif i == 3: medal = "🥉 "
            result_text += f"{medal}{name} ({upgrade_type}): {eff:.2e} efficiency\n"
            result_text += f"   Bonus: {bonus:.2e} | Cost: {cost:.2e}\n"
        result_text += f"\n✨ OVERALL BEST OPTION ✨\n{upgrades[0][0]} ({upgrades[0][4]}) with efficiency {upgrades[0][1]:.2e}"
        
        # Add area-specific advice
        result_text += "\n\n🎯 AREA-SPECIFIC TIPS:\n" + get_area_specific_advice(selected_area)

        # Display results
        st.subheader("Results")
        st.text_area("Upgrade Comparison Results", result_text, height=400)
        
        # Add copy button (Streamlit doesn't have direct clipboard access, so we show a message)
        if st.button("📋 Copy Results (Manually select and copy)"):
            st.success("Please manually select the text above and copy it (Ctrl+C or Cmd+C)")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

def show_optimization_advice():
    """Display optimization advice based on user inputs."""
    try:
        total_resources = convert_game_notation_to_number(st.session_state.resource_input)
        fs_bonus = convert_game_notation_to_number(st.session_state.fs_input)
        gather_percent = convert_game_notation_to_number(st.session_state.gather_input)
        selected_area = st.session_state.area_var

        advice = f"🎯 OPTIMIZATION ADVICE FOR {selected_area}:\n\n"

        if selected_area == "Early Game (A1-A3)":
            advice += "- Focus on unlocking perks like Instant Reload.\n"
            advice += "- Prioritize pet hatching and mutations.\n"
            advice += "- Farm shards at the Christmas event for quick progress.\n"
            advice += "- Prestige only when necessary (after tutorial).\n"
        elif selected_area == "Mid Game (A4)":
            advice += "- Farm the A4 meteor for shards and eggs.\n"
            advice += "- Maximize your Prestige upgrades before advancing.\n"
            advice += "- Hatch and mutate pets before entering A5.\n"
            advice += "- Balance stone collection with pet upgrades.\n"
        elif selected_area == "Late Game (A5+)":
            advice += "- Focus on maxing shard sinks and Prestige Multiplier.\n"
            advice += "- Join boss or meteor lobbies for maximum rewards.\n"
            advice += "- Aim for 1b+ Prestige Multiplier before breaking A5 meteor solo.\n"
            advice += "- Mutate all pets and invest in FS bonuses.\n"

        advice += f"\nYour Current Stats:\n"
        advice += f"- Total Resources: {total_resources:.2e}\n"
        advice += f"- Final Strike Bonus: {fs_bonus:.2e}\n"
        advice += f"- Gather %: {gather_percent:.2e}\n"

        st.subheader("Optimization Advice")
        st.text_area("Advice", advice, height=300)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

# Main Streamlit app
def main():
    st.set_page_config(page_title="🎮 Upgrade Efficiency Checker", layout="wide")
    
    # Initialize session state variables
    if 'area_var' not in st.session_state:
        st.session_state.area_var = "Early Game (A1-A3)"
    
    # Header
    st.title("🎮 Upgrade Efficiency Checker")
    st.markdown("Optimize your upgrade path for maximum efficiency!")
    
    # Area selection
    st.session_state.area_var = st.selectbox(
        "Select Your Current Area:",
        ["Early Game (A1-A3)", "Mid Game (A4)", "Late Game (A5+)"],
        index=0
    )
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["Calculator", "Tips & Tricks", "Optimization"])
    
    with tab1:
        st.header("Upgrade Efficiency Calculator")
        
        # Input fields for upgrades
        for i in range(1, 6):
            with st.expander(f"⚙️ Upgrade Level {i}", expanded=True):
                cols = st.columns([1, 4, 4, 4])
                with cols[0]:
                    st.session_state[f'unlocked_{i}'] = st.checkbox(
                        "Unlocked", value=True, key=f"unlocked_check_{i}"
                    )
                with cols[1]:
                    st.session_state[f'bonus_{i}'] = st.text_input(
                        "Bonus Value", key=f"bonus_entry_{i}"
                    )
                with cols[2]:
                    st.session_state[f'cost_{i}'] = st.text_input(
                        "Cost", key=f"cost_entry_{i}"
                    )
                
                st.caption("Example: 10NQd or 1.23e150")
                
                st.session_state[f'eff_upgrade_{i}'] = st.checkbox(
                    "Efficiency Upgrade Available", key=f"eff_upgrade_check_{i}"
                )
                if st.session_state[f'eff_upgrade_{i}']:
                    st.session_state[f'eff_cost_{i}'] = st.text_input(
                        "Efficiency Upgrade Cost", key=f"eff_cost_entry_{i}"
                    )
        
        if st.button("🔍 Compare Upgrades", key="calculate_button"):
            calc_efficiency()
    
    with tab2:
        st.header("Tips & Tricks")
        st.markdown(get_area_specific_advice(st.session_state.area_var))
    
    with tab3:
        st.header("Optimization Advice")
        st.session_state.resource_input = st.text_input("Total Resources:")
        st.session_state.fs_input = st.text_input("Final Strike Bonus:")
        st.session_state.gather_input = st.text_input("Gather %:")
        
        if st.button("Get Optimization Advice", key="optimization_button"):
            show_optimization_advice()
    
    # Footer
    st.markdown("---")
    st.markdown("Share your results in Discord!")

if __name__ == "__main__":
    main()
