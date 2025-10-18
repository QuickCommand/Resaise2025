# QuickCommand MAVLink translator (minimal stub)
# Returns a dict describing the intended MAVLink call.

def intent_to_mavlink(intent: str, params: dict) -> dict:
    intent = (intent or "").lower()
    if intent in ("move", "altitude"):
        return {"msg": "SET_POSITION_TARGET_LOCAL_NED",
                "vx_vy_vz": params.get("meters"),
                "dir": params.get("direction")}
    if intent == "rotate":
        return {"msg": "SET_ATTITUDE_TARGET",
                "yaw_deg": params.get("degrees")}
    if intent == "takeoff":
        return {"msg": "COMMAND_LONG", "cmd": "MAV_CMD_NAV_TAKEOFF"}
    if intent == "land":
        return {"msg": "COMMAND_LONG", "cmd": "MAV_CMD_NAV_LAND"}
    if intent == "hover" or params.get("low_confidence"):
        return {"msg": "SET_POSITION_TARGET_LOCAL_NED", "hold": True}
    if intent in ("emergency_stop", "e-stop", "estop"):
        return {"msg": "MODE_HOLD", "vel": 0}
    return {"msg": "UNKNOWN"}
