from datetime import datetime
import matplotlib.pyplot as plt

# -----------------------------
ledger = []

roles = {
    "Tutoring": 10,
    "Repair": 12,
    "Crafting": 8,
    "Delivery": 9,
    "Cleaning": 6,
    "Guiding": 15
}

role_lower_map = {r.lower(): r for r in roles}

role_total_credits = {r: 0 for r in roles}
role_users_count = {r: 0 for r in roles}
user_credits_total = {}
user_redeemed = {}

# Show upfront credits
print("=== Role Credits per Hour ===")
for role, credit in roles.items():
    print(f"{role}: {credit} credits/hour")
print("-" * 70)

# -----------------------------
def calculate_credits(role, hours):
    base = roles[role] * hours
    # Dynamic AI bonus: fewer users → higher bonus
    multiplier = 1 + min(0.3, 0.1 * max(0, 3 - role_users_count[role]))
    total = round(base * multiplier)
    bonus = total - base
    role_total_credits[role] += total
    return base, bonus, total

def add_transaction(user, role, hours):
    base, bonus, total = calculate_credits(role, hours)
    ledger.append({
        "User": user,
        "Role": role,
        "Hours": hours,
        "Base": base,
        "Bonus": bonus,
        "Total": total,
        "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    user_credits_total[user] = user_credits_total.get(user, 0) + total
    role_users_count[role] += 1
    return base, bonus, total

def recommend_roles(current_role):
    # Exclude current role
    available_roles = {role: role_users_count[role] for role in roles if role != current_role}
    # Score: fewer users → higher score
    scored_roles = sorted(available_roles.items(), key=lambda x: (3 - x[1]), reverse=True)
    top2 = scored_roles[:2]
    recs = []
    for role, users_count in top2:
        if users_count == 0:
            reason = f"No users yet, high potential reward ~{roles[role]}"
        elif users_count == 1:
            reason = f"Only 1 user, high demand, expected reward ~{roles[role]}"
        elif users_count == 2:
            reason = f"Few users, moderate demand, expected reward ~{roles[role]}"
        else:
            reason = f"Many users, lower demand, expected reward ~{roles[role]}"
        recs.append((role, reason))
    return recs

def redeem_credits(user):
    total = user_credits_total.get(user, 0)
    if total <= 0:
        print(f"{user} has no credits to redeem.\n")
        return
    print(f"{user} has {total} credits available to redeem.")
    try:
        amount = int(input("Enter number of credits you want to redeem: "))
        if amount <= 0:
            print("Redeem amount must be positive.\n")
            return
        if amount > total:
            print("Cannot redeem more than total credits.\n")
            return
    except:
        print("Invalid input.\n")
        return
    purpose = input("Enter purpose of redemption (e.g., groceries, transport, mobile recharge): ")
    user_credits_total[user] -= amount
    user_redeemed[user] = user_redeemed.get(user, []) + [(amount, purpose)]
    print(f"{user} redeemed {amount} credits for {purpose}. Remaining: {user_credits_total[user]}\n")

# -----------------------------
print("\n=== Enter user transactions ===\n")
while True:
    user = input("Enter your name (or 'exit'): ").strip()
    if user.lower() == "exit":
        break

    # Role selection
    while True:
        print("Available roles:", list(roles.keys()))
        role_input = input("Enter role: ").strip().lower()
        if role_input in role_lower_map:
            role = role_lower_map[role_input]
            break
        else:
            print("Invalid role. Try again.\n")

    while True:
        try:
            hours = float(input("Enter hours worked: "))
            if hours <= 0:
                print("Hours must be >0.\n")
                continue
            break
        except:
            print("Invalid input.\n")

    base, bonus, total = add_transaction(user, role, hours)
    print(f"\nBase Credits : {base}")
    print(f"AI Bonus     : {bonus} (based on demand)")
    print(f"Total Earned : {total}\n")

    # Recommendation
    recs = recommend_roles(role)
    print("AI Recommended roles to try next:")
    for r, reason in recs:
        print(f"- {r} → {reason}")

    try_next = input("Do you want to try a recommended role? (yes/no): ").strip().lower()
    if try_next == "yes":
        recommended_roles = [r for r, _ in recs]
        while True:
            next_role_input = input(f"Enter role from recommended options {recommended_roles}: ").strip().lower()
            if next_role_input in role_lower_map and role_lower_map[next_role_input] in recommended_roles:
                next_role = role_lower_map[next_role_input]
                while True:
                    try:
                        next_hours = float(input("Enter hours for this role (e.g., 1, 2, 1.5): "))
                        if next_hours <= 0:
                            print("Hours must be positive.\n")
                            continue
                        base2, bonus2, total2 = add_transaction(user, next_role, next_hours)
                        print(f"\nBase Credits : {base2}")
                        print(f"AI Bonus     : {bonus2} (based on demand)")
                        print(f"Total Earned : {total2}\n")
                        break
                    except:
                        print("Invalid input for hours.\n")
                break
            else:
                print("Invalid role from recommendations.\n")

    redeem_choice = input("Do you want to redeem credits now? (yes/no): ").strip().lower()
    if redeem_choice == "yes":
        print("Purpose examples: groceries, transport, mobile recharge")
        redeem_credits(user)

    print("Current total credits per user:")
    for u, c in user_credits_total.items():
        print(f"{u}: {c} credits")
    print("-" * 70 + "\n")

# -----------------------------
# Final Ledger Table
print("\n=== FINAL LEDGER TABLE ===")
header = "{:<10} {:<12} {:<6} {:<12} {:<12} {:<12} {:<25}".format(
    "User","Role","Hours","Base","Bonus","Total","Redeemed")
print(header)
print("-"*len(header))
for entry in ledger:
    user = entry["User"]
    redeemed_info = ""
    if user in user_redeemed:
        redeemed_info = ", ".join([f"{amt}->{purpose}" for amt, purpose in user_redeemed[user]])
    row = "{:<10} {:<12} {:<6} {:<12} {:<12} {:<12} {:<25}".format(
        user, entry["Role"], entry["Hours"], entry["Base"], entry["Bonus"], entry["Total"], redeemed_info
    )
    print(row)

# -----------------------------
# Plot
colors = ['#FF5733','#33FF57','#3357FF','#FF33A8','#FF8F33','#8D33FF']
plt.figure(figsize=(10,6))
bars = plt.bar(role_total_credits.keys(), role_total_credits.values(), color=colors)
plt.title("Total Credits Earned per Skill/Role")
plt.xlabel("Skill / Role")
plt.ylabel("Total Credits")
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x()+bar.get_width()/2, height+0.5, str(height), ha='center', va='bottom')
plt.show()