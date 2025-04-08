import streamlit as st
import pandas as pd
from math import log10

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

# Game progression milestones
MILESTONES = {
    "Early Game (A1-A3)": [
        "Get Instant Reload perk ASAP",
        "Farm Christmas event for eggs",
        "Prestige once with 63+ shards (45 for pet slots)",
        "Don't prestige again after initial tutorial prestige",
        "Focus on pet hatching and mutations"
    ],
    "Mid Game (A4)": [
        "Get help with A4 meteor gun trick (use Discord)",
        "Farm A4 meteor for shards (40k per break)",
        "Unlock rooms up to 18 (171k shards)",
        "Max prestige upgrades (1.04m shards)",
        "Don't enter A5 until ready (mutates pets)"
    ],
    "Late Game (A5+)": [
        "Stand in optimal position for OTg rocks",
        "Mutate all pets before heavy investing",
        "Join A5 meteor/boss lobbies at A5-5",
        "Aim for 1b+ Prestige Multiplier",
        "Focus on shard sinks after mutating pets"
    ]
}

# Boss vs Meteor comparison data
BOSS_VS_METEOR = {
    "Rewards": ["Shards/hour", "Eggs/hour", "Bones/hour", "Activity Required"],
    "Meteor (1min)": ["28.75m", "97.5m", "Varies", "AFK possible"],
    "Boss (100oc)": ["43.75m", "N/A", "Higher", "Active play"],
    "Advantages": [
        "Consistent, can AFK", 
        "Higher rewards, scales infinitely",
        "Good for bones", 
        "Better for late game"
    ]
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

def format_large_number(num):
    """Format large numbers into game notation"""
    if num == 0:
        return "0"
    exponent = int(log10(num))
    for notation, exp in sorted(NOTATION_CONVERSION.items(), 
                              key=lambda x: -int(x[1][1:])):
        exp_val = int(exp[1:])
        if exponent >= exp_val:
            value = num / (10 ** exp_val)
            return f"{value:.2f}{notation}"
    return f"{num:.2e}"

def calculate_upgrade_efficiency():
    """Calculate and compare upgrade efficiencies."""
    try:
        upgrades = []
        level_comparisons = []
        selected_area = st.session_state.area_var
        # Collect upgrade data
        for i in range(1, 6):
            if not st.session_state[f'unlocked_{i}']:
                continue
            bonus = convert_game_notation_to_number(st.session_state[f'bonus_{i}'])
            cost = convert_game_notation_to_number(st.session_state[f'cost_{i}'])
            if cost == 0:
                continue
            normal_efficiency = bonus / cost
            upgrades.append({
                "Upgrade": f"Level {i}",
                "Type": "Normal",
                "Efficiency": normal_efficiency,
                "Bonus": bonus,
                "Cost": cost
            })
            # Check efficiency upgrade
            if st.session_state[f'eff_upgrade_{i}']:
                eff_cost = convert_game_notation_to_number(st.session_state[f'eff_cost_{i}'])
                if eff_cost == 0:
                    continue
                eff_efficiency = (bonus * 2) / eff_cost
                upgrades.append({
                    "Upgrade": f"Level {i}",
                    "Type": "Efficiency",
                    "Efficiency": eff_efficiency,
                    "Bonus": bonus * 2,
                    "Cost": eff_cost
                })
                # Compare normal vs efficiency
                if eff_efficiency > normal_efficiency:
                    diff = ((eff_efficiency - normal_efficiency) / normal_efficiency) * 100
                    level_comparisons.append(f"Level {i}: 🟢 Efficiency is {diff:.1f}% better")
                elif eff_efficiency < normal_efficiency:
                    diff = ((normal_efficiency - eff_efficiency) / eff_efficiency) * 100
                    level_comparisons.append(f"Level {i}: 🔴 Normal is {diff:.1f}% better")
                else:
                    level_comparisons.append(f"Level {i}: ⚪ Both are equal")
        if not upgrades:
            st.error("No valid upgrades to compare!")
            return None
        # Sort by efficiency
        upgrades_df = pd.DataFrame(upgrades)
        upgrades_df = upgrades_df.sort_values("Efficiency", ascending=False)
        return upgrades_df, level_comparisons, selected_area
    except Exception as e:
        st.error(f"Calculation error: {str(e)}")
        return None

def show_guide_section():
    """Show the game guide section"""
    st.header("🎮 Complete Game Progression Guide")
    tab1, tab2, tab3, tab4 = st.tabs(["Early Game", "Mid Game", "Late Game", "Advanced"])
    with tab1:
        st.subheader("A1-A3: Early Game Strategy")
        st.image("https://via.placeholder.com/600x300?text=Early+Game+Screenshot", use_container_width=True)
        st.write("""
        **Key Objectives:**
        - Complete tutorial and get basic gun
        - Unlock Instant Reload perk ASAP
        - Farm Christmas event for eggs
        - First prestige with 63+ shards (45 for pet slots)
        **Pro Tips:**
        - Don't prestige again after initial tutorial prestige
        - Focus on pet hatching and mutations
        - Best perks: Instant Reload, Attack, Crit Damage
        - Evolve gun to Mythic when possible
        """)
        st.write("\n".join(MILESTONES["Early Game (A1-A3)"]))
    with tab2:
        st.subheader("A4: Mid Game Strategy")
        st.image("https://via.placeholder.com/600x300?text=Mid+Game+Screenshot", use_container_width=True)
        st.write("""
        **Key Objectives:**
        - Get help with A4 meteor gun trick (use Discord)
        - Farm A4 meteor for shards (40k per break)
        - Unlock rooms up to 18 (171k shards)
        - Max prestige upgrades (1.04m shards)
        **Pro Tips:**
        - Join meteor lobbies for faster progress
        - Don't enter A5 until ready (mutates pets)
        - Farm 20min-31hr depending on goals
        - Clear A4-5 but don't fight Astralis boss
        """)
        st.write("\n".join(MILESTONES["Mid Game (A4)"]))
    with tab3:
        st.subheader("A5+: Late Game Strategy")
        st.image("https://via.placeholder.com/600x300?text=Late+Game+Screenshot", use_container_width=True)
        st.write("""
        **Key Objectives:**
        - Optimal positioning for OTg rocks
        - Mutate all pets before heavy investing
        - Join A5 meteor/boss lobbies at A5-5
        - Aim for 1b+ Prestige Multiplier
        **Pro Tips:**
        - Common pet FS ≈ 66% of level
        - Uncommon pet FS ≈ 100% of level
        - Focus on shard sinks after mutating
        - 300NQd/s to start meteor farming
        """)
        st.write("\n".join(MILESTONES["Late Game (A5+)"]))
    with tab4:
        st.subheader("Advanced Mechanics")
        st.write("""
        **Prestige Strategy:**
        - First 220 prestiges scale with stone
        - 221+ gives flat bonus based on shard sink
        - Wait until 4-5m+ FS and 1150% shard sink
        - Early prestiges should take <1min
        **Boss vs Meteor:**
        """)
        st.dataframe(pd.DataFrame(BOSS_VS_METEOR), hide_index=True)
        st.write("""
        **Efficiency Math:**
        - Pet Gather % = Prestige Multiplier
        - 1.5m FS ≈ 22.5m Gather %
        - 2m FS ≈ 30m Gather %
        - Need 100-200m PM for comfortable meteor
        - 500m PM feels good, 1b+ is ideal
        """)

def show_calculator_section():
    """Show the calculator section"""
    st.header("⚖️ Upgrade Efficiency Calculator")
    # Area selection
    st.session_state.area_var = st.selectbox(
        "Select Your Game Stage:",
        list(MILESTONES.keys()),
        key="area_select"
    )
    # Create input fields for each upgrade level
    for i in range(1, 6):
        with st.expander(f"⚙️ Upgrade Level {i}", expanded=(i==1)):
            cols = st.columns([1,2,2,3])
            with cols[0]:
                st.checkbox(
                    "Unlocked", 
                    value=st.session_state.get(f'unlocked_{i}', True), 
                    key=f"unlocked_{i}"
                )
            with cols[1]:
                st.text_input(
                    "Bonus Value", 
                    value=st.session_state.get(f'bonus_{i}', ""), 
                    key=f"bonus_{i}", 
                    help="Example: 10NQd or 1.23e150"
                )
            with cols[2]:
                st.text_input(
                    "Cost", 
                    value=st.session_state.get(f'cost_{i}', ""), 
                    key=f"cost_{i}"
                )
            st.checkbox(
                "Efficiency Upgrade Available", 
                value=st.session_state.get(f'eff_upgrade_{i}', False), 
                key=f"eff_upgrade_{i}"
            )
            if st.session_state.get(f'eff_upgrade_{i}', False):
                st.text_input(
                    "Efficiency Upgrade Cost", 
                    value=st.session_state.get(f'eff_cost_{i}', ""), 
                    key=f"eff_cost_{i}"
                )
    if st.button("🔍 Compare Upgrades", use_container_width=True):
        with st.spinner("Calculating efficiencies..."):
            result = calculate_upgrade_efficiency()
        if result:
            upgrades_df, comparisons, area = result
            st.subheader("🔹 Upgrade Comparisons by Level")
            for comp in comparisons:
                st.write(comp)
            st.subheader("🏆 All Upgrades Ranked by Efficiency")
            st.dataframe(
                upgrades_df.style.format({
                    "Efficiency": "{:.2e}",
                    "Bonus": "{:.2e}",
                    "Cost": "{:.2e}"
                }),
                column_config={
                    "Upgrade": "Upgrade",
                    "Type": "Type",
                    "Efficiency": st.column_config.NumberColumn(
                        "Efficiency",
                        help="Bonus per cost",
                        format="%.2e"
                    ),
                    "Bonus": st.column_config.NumberColumn(
                        "Bonus Value",
                        format="%.2e"
                    ),
                    "Cost": st.column_config.NumberColumn(
                        "Cost",
                        format="%.2e"
                    )
                },
                hide_index=True,
                use_container_width=True
            )
            best_upgrade = upgrades_df.iloc[0]
            st.success(
                f"✨ Best Option: {best_upgrade['Upgrade']} ({best_upgrade['Type']}) "
                f"with efficiency {best_upgrade['Efficiency']:.2e}"
            )
            st.subheader(f"🎯 {area} Tips")
            st.write("\n".join(MILESTONES[area]))

def show_optimizer_section():
    """Show the resource optimizer section"""
    st.header("📊 Resource Optimizer")
    cols = st.columns(3)
    with cols[0]:
        st.text_input(
            "Total Resources Available", 
            value=st.session_state.get('total_resources', ""), 
            key='total_resources', 
            help="Example: 1.5Qa or 1.5e15"
        )
    with cols[1]:
        st.text_input(
            "Current Final Strike Bonus", 
            value=st.session_state.get('fs_bonus', ""), 
            key='fs_bonus', 
            help="Your FS bonus value"
        )
    with cols[2]:
        st.text_input(
            "Current Gather %", 
            value=st.session_state.get('gather_percent', ""), 
            key='gather_percent', 
            help="Your total gather percentage"
        )
    if st.button("💡 Get Optimization Advice", use_container_width=True):
        try:
            resources = convert_game_notation_to_number(st.session_state.total_resources)
            fs = convert_game_notation_to_number(st.session_state.fs_bonus)
            gather = convert_game_notation_to_number(st.session_state.gather_percent)
            area = st.session_state.area_var
            advice = f"### 🎯 Optimization Advice for {area}\n"
            if area == "Early Game (A1-A3)":
                advice += f"""
                - Spend up to {format_large_number(resources*0.7)} on pet hatching
                - Allocate remaining to weapon upgrades
                - Target FS bonus of at least {format_large_number(1e6)} before A3
                """
            elif area == "Mid Game (A4)":
                advice += f"""
                - Invest {format_large_number(resources*0.5)} in prestige upgrades
                - Spend {format_large_number(resources*0.3)} on pet mutations
                - Keep {format_large_number(resources*0.2)} for emergency needs
                - Target FS bonus of {format_large_number(1e7)} before A5
                """
            else:  # Late Game
                advice += f"""
                - Invest {format_large_number(resources*0.7)} in shard sinks
                - Spend {format_large_number(resources*0.2)} on pet mutations
                - Allocate {format_large_number(resources*0.1)} to hut upgrades
                - Target PM of {format_large_number(1e9)} for optimal meteor
                """
            st.markdown(advice)
            # Show stats
            st.metric("Current Resources", format_large_number(resources))
            st.metric("Final Strike Bonus", format_large_number(fs))
            st.metric("Gather Percentage", format_large_number(gather))
        except Exception as e:
            st.error(f"Error in calculation: {str(e)}")

def main():
    """Main app function"""
    # Configure page
    st.set_page_config(
        page_title="🎮 Ultimate Miner Tycoon Tool",
        page_icon="⛏️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    # Custom CSS
    st.markdown("""
    <style>
    .st-emotion-cache-1v0mbdj img {
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .st-emotion-cache-1y4p8pa {
        padding: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px;
        border-radius: 4px 4px 0 0;
    }
    .st-emotion-cache-16txtl3 {
        padding: 2rem 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    # Initialize session state
    if 'initialized' not in st.session_state:
        for i in range(1, 6):
            st.session_state[f'unlocked_{i}'] = True
            st.session_state[f'bonus_{i}'] = ""
            st.session_state[f'cost_{i}'] = ""
            st.session_state[f'eff_upgrade_{i}'] = False
            st.session_state[f'eff_cost_{i}'] = ""
        st.session_state['area_var'] = "Early Game (A1-A3)"
        st.session_state['total_resources'] = ""
        st.session_state['fs_bonus'] = ""
        st.session_state['gather_percent'] = ""
        st.session_state['initialized'] = True
    # Sidebar
    with st.sidebar:
        st.title("⛏️ Miner Tycoon Tools")
        st.markdown("""
        **Navigate through the tabs to access:**
        - 📖 Complete game guide
        - ⚖️ Upgrade efficiency calculator
        - 📊 Resource optimization advisor
        """)
        st.divider()
        st.markdown("""
        **Quick Tips:**
        - Early game: Focus on pets
        - Mid game: Farm A4 meteor
        - Late game: Join A5 lobbies
        """)
        if st.button("Join Discord for Help"):
            webbrowser.open("https://discord.gg/tcgvB36KDQ")
    # Main content
    tab1, tab2, tab3 = st.tabs(["📖 Game Guide", "⚖️ Calculator", "📊 Optimizer"])
    with tab1:
        show_guide_section()
    with tab2:
        show_calculator_section()
    with tab3:
        show_optimizer_section()
    # Footer
    st.divider()
    st.caption("""
    Made with ❤️ for Miner Tycoon players | 
    Data based on community research by Elrina and others
    """)

if __name__ == "__main__":
    main()
