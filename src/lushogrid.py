from collections import Counter

def loshu_grid_from_dob(dob_str):
    # dob_str format: "YYYY-MM-DD" or "YYYY/MM/DD"

    dob_str = dob_str.replace("/", "-")
    year, month, day = dob_str.split("-")

    day = int(day)
    month = int(month)
    year = int(year)

    # ---- Extract DOB digits ----
    dob_digits = list(str(day).zfill(2) + str(month).zfill(2) + str(year))
    dob_digits = [int(d) for d in dob_digits if d != '0']

    # ---- Driver (Day) ----
    driver = sum(int(d) for d in str(day))
    while driver > 9:
        driver = sum(int(d) for d in str(driver))

    # ---- Conductor (Full DOB) ----
    conductor = sum(int(d) for d in str(day) + str(month) + str(year))
    while conductor > 9:
        conductor = sum(int(d) for d in str(conductor))

    dob_digits += [driver, conductor]

    freq = Counter(dob_digits)

    grid = {i: str(i) * freq.get(i, 0) for i in range(1, 10)}

    return grid, driver, conductor
