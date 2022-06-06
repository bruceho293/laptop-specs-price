# Count the component based on the size and unit in the components and memos.
unit_table = {
    "MB": 1,
    "GB": 1000,
    "TB": 1000000,
}
def unit_conversion(unit):
    if not unit in unit_table.keys():
        raise ValueError("Inappropriate or Unsupported Unit Type")
    return unit_table[unit]

def unit_count(from_size, from_unit, to_size, to_unit):
    # Table for unit conversion in decimal (base 10).
    # The smallest unit in the table will be Megabyte (MB),
    # whose value equals to 1.
    # Example: 
    #     1) 1 TB Component A to 256 GB Component B
    #     Count = (1 * 10^6) / (256 * 10^3) ~ 3.90
    #     --> 1 Comp A = 4 Comp B (using ceiling function) 
    #     
    #     2) 256 Component A to 1 TB Component B
    #     Count = (256 * 10^3) / (1 * 10^6) = 0.256
    #     --> Cant convert 

    print("From: {} {} - To: {} {}".format(from_size, from_unit, to_size, to_unit))

    # Convert string to float
    f_size = float(from_size)
    t_size = float(to_size)
    
    # Get the convertsion
    f_unit = unit_table[from_unit]
    t_unit = unit_table[to_unit]

    # Calculate the count
    return (f_size * f_unit) / (t_size * t_unit)