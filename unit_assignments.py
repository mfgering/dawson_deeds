

def find_gaps(arr):
    gaps = []
    # First, sort the array to ensure it's in ascending order
    sorted_arr = sorted(arr)

    # Iterate through the sorted array
    for i in range(len(sorted_arr) - 1):
        current = sorted_arr[i]
        next = sorted_arr[i + 1]

        # Check if there's a gap
        if next - current > 1:
            # Print all numbers in the gap
            for gap in range(current + 1, next):
                gaps.append(gap)
    return gaps

# Columns: [<unit>, <parking>, <stg>, <lockbox>]
markdown_table = [
    ["200", "77, 96", "61", "36"],
    ["200-1", "105", "54", "67"],
    ["201", "4, 5", "11", "26"],
    ["202", "40", "52", "41"],
    ["203", "46", "47", "38"],
    ["204", "32, 51", "35", "9"],
    ["205", "76", "23", "8"],
    ["206", "70, 72", "28", "47"],
    ["207", "95", "33", "52"],
    ["208", "6, 8", "30", "32"],
    ["209", "100", "26", "12"],
    ["210", "63, 64", "57", "49"],
    ["211", "41", "48", "33"],
    ["213", "103", "24", "28"],
    ["215", "47", "32", "4"],
    ["217", "49, 50", "58", "24"],
    ["220", "78", "49", "31"],
    ["224", "43, 44", "56", "35"],
    ["226", "42", "44", "29"],
    ["300", "61, 69", "19", "30"],
    ["300-1", "87", "65", "50"],
    ["301", "37, 48", "41", "40"],
    ["302", "89", "50", "20"],
    ["303", "38", "46", "48"],
    ["304", "59, 60", "38", "22"],
    ["305", "80", "16", "17"],
    ["306", "11, 12", "66", "27"],
    ["307", "91", "14", "37"],
    ["308", "33, 75", "17", "42"],
    ["309", "99", "27", "54"],
    ["310", "57, 58", "36", "19"],
    ["311", "55, 90", "34", "10"],
    ["313", "86", "21", "18"],
    ["315", "39", "22", "13"],
    ["317", "26, 104", "45", "6"],
    ["320", "45", "64", "23"],
    ["324", "35, 36", "53", "43"],
    ["326", "93, 106", "63", "15"],
    ["400", "1, 2", "62", "34"],
    ["401", "29, 94", "55", "1"],
    ["403", "30", "43", "14"],
    ["404", "34, 56", "3", "7"],
    ["405", "101", "8", "46"],
    ["406", "71, 102", "12", "25"],
    ["407", "81", "9", "2"],
    ["408", "73, 92", "25", "5"],
    ["409", "98", "10", "3"],
    ["410", "53, 54", "31", "51"],
    ["411", "3", "51", "11"],
    ["412", "22, 23", "60", "21"],
    ["413", "85", "4", "16"],
    ["415", "31", "42", "44"],
    ["417", "25, 32", "59", "45"],
    ["500", "18, 19", "37", "39"],
    ["501", "20, 21", "15", "53"],
    ["504", "24, 62", "2", "60"],
    ["505", "84", "13", "65"],
    ["506", "67, 68", "20", "55"],
    ["507", "83", "5", "56"],
    ["508", "65, 66", "1", "62"],
    ["509", "97", "18", "61"],
    ["510", "14, 15", "29", "58"],
    ["511", "79, 82", "7", "59"],
    ["512", "27, 28", "39", "57"],
    ["513", "88", "6", "63"],
    ["515", "16, 17", "40", "64"]
]

unit_map = {r[0]: r[1:] for r in markdown_table}
unit2parking = {x: y[0] for x, y in unit_map.items()}
unit2stg = {x: y[1] for x, y in unit_map.items()}
unit2box = {x: y[2] for x, y in unit_map.items()}

units = {u[0] for u in markdown_table}

# parking_map: space->unit
parking2unit = {}
for r in markdown_table:
    unit = r[0]
    spaces = r[1]
    x = spaces.split(',')
    for y in x:
        try:
            int(y)
        except ValueError:
            print(f"Parking space {y} is not an integer")
            continue
        if y in parking2unit:
            print(f"Parking space {y} already assigned to {parking2unit[y]} instead of to {unit}")
        else:
            parking2unit[y] = unit
print(f"parking2unit has {len(parking2unit.items())} items")
# check for gaps
all_spaces = sorted([ int(u) for u in parking2unit.keys()])
gaps = [str(g) for g in find_gaps(all_spaces)]
print(f"Parking space gaps: {', '.join(gaps)}")

stg2unit = {}
for r in markdown_table:
    unit = r[0]
    stg = r[2]
    if stg in stg2unit:
        print(f"Storage {stg} already assigned to {stg2unit[stg]} instead of to {unit}")
    else:
        stg2unit[stg] = unit
print(f"stg2unit has {len(stg2unit.items())} items")
# check for gaps
all_stg = sorted([ int(u) for u in stg2unit.keys()])
gaps = [str(g) for g in find_gaps(all_stg)]
print(f"Storage gaps: {', '.join(gaps)}")

box2unit = {}
for r in markdown_table:
    unit = r[0]
    box = r[3]
    if box in box2unit:
        print(f"Lockbox {box} already assigned to {box2unit[box]} instead of to {unit}")
    else:
        box2unit[box] = unit
print(f"box2unit has {len(box2unit.items())} items")
# check for gaps
all_box = sorted([ int(u) for u in box2unit.keys()])
gaps = [str(g) for g in find_gaps(all_box)]
print(f"Box gaps: {', '.join(gaps)}")


print("Done")