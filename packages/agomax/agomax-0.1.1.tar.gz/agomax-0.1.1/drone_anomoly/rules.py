def constant_rule_checker(dp):
    return sum([
        dp["GPS_status"] != 1,
        dp["Gyro_status"] != 1,
        dp["Accel_status"] != 1,
        dp["Baro_status"] != 1
    ])

def initialisation_rule_checker(dp):
    return sum([
        not (-0.0009 <= dp["roll"] <= -0.0003),
        not (0.0009 <= dp["pitch"] <= 0.001),
        not (0.0001 <= dp["pitchspeed"] <= 0.0005),
        not (0.00009 <= dp["rollspeed"] <= 0.0004),
        not (0.001 <= dp["yawspeed"] <= 0.002),
        dp["airspeed"] != 0.0,
        dp["throttle"] != 0.0,
        not (-0.02 <= dp["climb"] <= 0.04)
    ])

def takeoff_rule_checker(dp):
    return sum([
        not (-0.2 <= dp["climb"] <= 1.6),
        not (0 <= dp["airspeed"] <= 6),
        not (0 <= dp["throttle"] <= 80),
        not (-0.07 <= dp["roll"] <= 0.17),
        not (-0.19 <= dp["pitch"] <= 0.16),
        not (-0.15 <= dp["pitchspeed"] <= 0.1),
        not (-0.87 <= dp["rollspeed"] <= 0.89),
        not (-0.095 <= dp["yawspeed"] <= 0.85)
    ])

def on_mission_rule_checker(dp):
    return sum([
        not (-1.1 <= dp["climb"] <= 1.6),
        not (0.1 <= dp["airspeed"] <= 7.05),
        not (31 <= dp["throttle"] <= 100),
        not (-0.25 <= dp["roll"] <= 0.22),
        not (-0.3 <= dp["pitch"] <= 0.16),
        not (-0.22 <= dp["pitchspeed"] <= 0.2),
        not (-1.14 <= dp["rollspeed"] <= 1.07),
        not (-0.81 <= dp["yawspeed"] <= 0.79)
    ])

def return_to_origin_rule_checker(dp):
    return sum([
        not (-0.041 <= dp["climb"] <= 0.09),
        not (0.04 <= dp["airspeed"] <= 6.9),
        not (32 <= dp["throttle"] <= 50),
        not (-0.07 <= dp["roll"] <= 0.068),
        not (-0.062 <= dp["pitch"] <= 0.22),
        not (-0.087 <= dp["pitchspeed"] <= 0.088),
        not (-0.68 <= dp["rollspeed"] <= 0.68),
        not (-0.043 <= dp["yawspeed"] <= 0.039)
    ])

def landing_rule_checker(dp):
    return sum([
        not (-1.18 <= dp["climb"] <= 0.163),
        not (0 <= dp["airspeed"] <= 6.1),
        not (0 <= dp["throttle"] <= 38),
        not (-0.081 <= dp["roll"] <= 0.05),
        not (-0.07 <= dp["pitch"] <= 0.05),
        not (-0.05 <= dp["pitchspeed"] <= 0.04),
        not (-1.49 <= dp["rollspeed"] <= 1.61),
        not (-0.023 <= dp["yawspeed"] <= 0.071)
    ])

def rule_checker(dp):
    """
    Apply all relevant rule checkers for a single datapoint (row).
    """
    phase = dp["PHASE"]
    count = constant_rule_checker(dp)

    if phase == "INITIALISATION":
        count += initialisation_rule_checker(dp)
    elif phase == "TAKEOFF":
        count += takeoff_rule_checker(dp)
    elif phase == "ON MISSION":
        count += on_mission_rule_checker(dp)
    elif phase == "RETURN TO ORIGIN":
        count += return_to_origin_rule_checker(dp)
    elif phase == "LANDING":
        count += landing_rule_checker(dp)

    return count
