# app/utils/regions.py

REGIONS = ["All", "North", "South", "East", "West"]

REGION_TO_STATES = {
    "North": ["CT","ME","MA","NH","NJ","NY","PA","RI","VT","MI","MN","WI","IA","ND","SD","NE","OH","IL","IN"],
    "South": ["AL","AR","FL","GA","KY","LA","MS","NC","OK","SC","TN","TX","VA","WV","MD","DE","DC"],
    "East":  ["CT","DE","DC","FL","GA","MA","MD","ME","NC","NH","NJ","NY","PA","RI","SC","VA","VT"],
    "West":  ["AK","AZ","CA","CO","HI","ID","MT","NM","NV","OR","UT","WA","WY"],
}

def states_for_regions(selected: list[str]) -> list[str]:
    # Return [] when "All" (or nothing) is chosen → no filter
    if not selected or "All" in selected:
        return []
    out = []
    for r in selected:
        out.extend(REGION_TO_STATES.get(r, []))
    # dedupe + sort
    return sorted(set(out))