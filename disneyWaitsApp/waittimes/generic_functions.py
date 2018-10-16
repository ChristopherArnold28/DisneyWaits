def fix_time(time_string):
    if ("AM" in time_string) or ("PM" in time_string):
        time_string = time_string[1:] if time_string.startswith('0') else time_string
        return time_string

    first_half = time_string.split(":")[0]
    second_half = time_string.split(":")[1]
    if int(first_half) ==0:
        first_half = "12"
        time_string = str(first_half) + ":" + second_half + " AM"
    elif int(first_half)>12:
        first_half = int(first_half) - 12
        time_string = str(first_half) + ":" + second_half + " PM"
    elif int(first_half) == 12:
        time_string = first_half + ":" + second_half + " PM"
    else:
        time_string = str(int(first_half)) + ":" + second_half + " AM"

    return time_string
