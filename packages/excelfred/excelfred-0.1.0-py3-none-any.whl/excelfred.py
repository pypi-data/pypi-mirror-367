"""
excelfred - A beginner-friendly open-source Python package recreating Excel 514 functions
`Author: Samuel Raj P (FRED)`
https://www.linkedin.com/in/samuel-raj23
"""

def ABS(*args: int | float | str) -> float:
    """**=ABS(number)** Returns an Absolute value of a number by taking Modulus. A number without its sign
    
    `Parameters: Only one -> Number (but accepts arithmetics too) int | float | str`

    *Example inputs*:

     ABS(-5)                 -> 5.0
     ABS(5+2)                -> 7.0
     ABS(11,7)               -> 18.0
     ABS("3+2-7")            -> 2.0
     ABS(-5,"54",-(3.2+6.8)) -> 69.00
    """
    try:
        total = 0
        for arg in args:
            if isinstance(arg, str) and not arg.replace('.', '', 1).replace('-', '', 1).isdigit():
                try:
                    arg = eval(arg)
                except:
                    raise ValueError(f"🚫 String Error: Invalid Formula `{arg}` is not evaluatable.")
            try:
                number = float(arg)
            except:
                raise TypeError(f"🚫 ABS() only works on numbers or math-like strings. Got `{arg}`.")

            total += abs(number)
        assert args, "Value Error: 🚫 ABS() requires at least one numeric input."
        return total
    except AssertionError as ae:
        raise ValueError(str(ae))
print("ABS")

def ACCRINT(issue: str, first_interest: str, settlement: str, rate: float, par: float = 15000.00, frequency: int = 1, basis: int = 0, calc_method: bool = True) -> float:
    """
    `=ACCRINT(issue, first_interest, settlement, rate, par, frequency, [basis], [calc_method])`

    Calculates accrued interest for a security that pays periodic interest.

    Parameters:
        issue (str): Issue date (format: 'DD-MM-YYYY')
        first_interest (str): First interest date (format: 'DD-MM-YYYY')
        settlement (str): Settlement date (format: 'DD-MM-YYYY')
        rate (float): Annual interest rate (e.g. 0.1 for 10%)
        par (float): Par value of the security
        frequency (int): Payments per year (1=Annual, 2=Semiannual, 4=Quarterly)
        basis (int, optional): Day count basis (default is 0):
            0 = US (NASD) 30/360
            1 = Actual/actual
            2 = Actual/360
            3 = Actual/365
            4 = European 30/360
        calc_method (bool, optional): 
            If TRUE (default), calculates from issue to settlement date. 
            If FALSE, from first interest to settlement date.

    Returns:
        float: The accrued interest
    """
    import pandas as pd
    try:
        issue_date = pd.to_datetime(issue, dayfirst=True)
        first_date = pd.to_datetime(first_interest, dayfirst=True)
        settle_date = pd.to_datetime(settlement, dayfirst=True)
    except Exception:
        raise ValueError("🚫 Could not parse one or more dates. Try using common formats like 'DD-MM-YYYY'")

    if settle_date <= issue_date:
        raise ValueError("🚫 Settlement date must be after issue date.")
    if frequency not in [1, 2, 4]:
        raise ValueError("🚫 Frequency must be 1 (Annual), 2 (Semi-annual), or 4 (Quarterly).")
    if basis not in range(5):
        raise ValueError("🚫 Basis must be between 0 and 4.")

    start_date = issue_date if calc_method else first_date
    if settle_date <= start_date:
        raise ValueError("🚫 Settlement date must be after the start date based on calc_method.")

    delta_days = (settle_date - start_date).days
    if basis == 0 or basis == 4:
        d1 = start_date
        d2 = settle_date
        days = ((d2.year - d1.year) * 360 +
                (d2.month - d1.month) * 30 +
                (d2.day - d1.day))
        year_basis = 360
    elif basis == 1:
        days = delta_days
        leap_start = int(pd.Timestamp(start_date).is_leap_year)
        leap_end = int(pd.Timestamp(settle_date).is_leap_year)
        year_basis = 366 if leap_start or leap_end else 365
    elif basis == 2:
        days = delta_days
        year_basis = 360
    elif basis == 3:
        days = delta_days
        year_basis = 365
    accrued = par * rate * days / year_basis
    return accrued
print("ACCRINT")

def ACCRINTM(issue: str, maturity: str, rate: float, par: float = 15000.00, basis: int = 0) -> float:
    """
    `=ACCRINTM(issue, settlement maturity, rate, par, [basis])`

    Returns the accrued interest for a security that pays interest at maturity (no periodic coupons).

    Parameters:
        issue (str): Issue date in 'DD-MM-YYYY' format
        maturity (str): Maturity date in 'DD-MM-YYYY' format
        rate (float): Annual interest rate (e.g., 0.1 for 10%)
        par (float): Par value of the security (default = 15000.00)
        basis (int): Day count basis (0–4). Default is 0:
            0 = US (NASD) 30/360
            1 = Actual/actual
            2 = Actual/360
            3 = Actual/365
            4 = European 30/360

    Returns:
        float: Accrued interest at maturity
    """
    import pandas as pd
    try:
        issue_date = pd.to_datetime(issue, dayfirst=True)
        maturity_date = pd.to_datetime(maturity, dayfirst=True)
    except:
        raise ValueError("🚫 Invalid date format. Use 'DD-MM-YYYY'.")

    if maturity_date <= issue_date:
        raise ValueError("Logic Error: 🚫 Maturity date must be after the issue date.")

    delta_days = (maturity_date - issue_date).days
    if basis == 0 or basis == 4:
        d1 = issue_date
        d2 = maturity_date
        days = ((d2.year - d1.year) * 360 +
                (d2.month - d1.month) * 30 +
                (d2.day - d1.day))
        year_basis = 360
    elif basis == 1:
        days = delta_days
        leap_start = int(issue_date.is_leap_year)
        leap_end = int(maturity_date.is_leap_year)
        year_basis = 366 if leap_start or leap_end else 365
    elif basis == 2:
        days = delta_days
        year_basis = 360
    elif basis == 3:
        days = delta_days
        year_basis = 365
    else:
        raise ValueError("String Error: 🚫 Basis must be an integer between 0 and 4.")
    interest = par * rate * days / year_basis
    return interest
print("ACCRINTM")

def ACOS(*args: int | float | str) -> float:
    """
    **=ACOS(number)** Returns the arccosine (inverse cosine) of a number, in a radians in the range of 0 to pi. Returns angle
    `Parameters: Only one -> Number (but accepts arithmetics too) int | float | str`

    *Example inputs*:

     print(ACOS(1))           # ➜ 0.0
     print(ACOS(0))           # ➜ 1.5707963268
     print(ACOS(-1))          # ➜ 3.1415926536
     print(ACOS("0.5")) # ➜ 1.0471975512
     print(ACOS(0.5+0.3))     # ➜ 0.927295218

    """
    import numpy as np
    try:
        assert args, "Value Error: 🚫 ACOS() requires one numeric input."
        if len(args) != 1:
            raise ValueError("Parameters Error: 🚫 ACOS() only takes one input.")
        for arg in args:
            if isinstance(arg, str) and not arg.replace('.', '', 1).replace('-', '', 1).isdigit():
                try:  arg = eval(arg)
                except:  raise ValueError(f"Value Error: 🚫 Cannot evaluate the expression `{arg}`.")
            try:
                number = float(arg)
            except:
                raise TypeError(f"Number Error: 🚫 ACOS expects a numeric value or a math-like string. Got `{arg}`")
            if number < -1 or number > 1:
                raise ValueError("Range Error: 🚫 Input must be between -1 to 1 (inclusive).")
            return np.arccos(number)
    except AssertionError as ae:
        raise ValueError(str(ae))
print("ACOS")

def ACOSH(*args: int | float | str) -> float:
    """
    **=ACOSH(number)** Returns the inverse hyperbolic cosine of a number. The number must be greater than or equal to 1. 

    `Parameters: Only one -> Number (but accepts arithmetics too) int | float | str`

    *Example inputs*:

     ACOSH(1)            -> 0.0
     ACOSH("2 + 3")      -> 2.2924316696
     ACOSH(2 + 3)        -> 2.2924316696
     ACOSH("5")          -> 2.2924316696
    """
    import numpy as np
    try:
        assert args, "Value Error: 🚫 ACOSH() requires one numeric input."
        if len(args) != 1:
            raise ValueError("Parameters Error: 🚫 ACOSH() only takes one input.")
        for arg in args:
            if isinstance(arg, str) and not arg.replace('.', '', 1).replace('-', '', 1).isdigit():
                try: arg = eval(arg)
                except: raise ValueError(f"Evaluate Error: 🚫 Cannot evaluate the expression `{arg}`.")
            try:
                number = float(arg)
            except:
                raise TypeError(f"Type Error: 🚫 ACOSH expects a numeric value or a math-like string. Got `{arg}`")
            if number < 1:
                raise ValueError("Number Error: 🚫 Input must be greater than or equal to 1.")
            return np.arccosh(number)
    except AssertionError as ae: raise ValueError(str(ae))
print("ACOSH")

def ACOT(*args: int | float | str) -> float:
    """
    **=ACOT(number)** Returns the arccotangent (inverse cotangent) of a number, if radians ranges 0 to Pi. It returns 1/number.

    `Parameters: Only one -> Number (but accepts arithmetics too) int | float | str`

    *Example inputs*:

     ACOT(1)           -> 0.7853981634
     ACOT(0.5)         -> 1.1071487178
     ACOT("1 / 3")     -> 1.2490457724
     ACOT(0)           -> 1.5707963268
     ACOT(-5 + 2)    -> 1.8925468812
    """
    import numpy as np
    try:
        assert args, "Value Error: 🚫 ACOT() requires one numeric input."
        if len(args) != 1: raise ValueError("Value Error: 🚫 ACOT() only takes one input.")
        for arg in args:
            if isinstance(arg, str) and not arg.replace('.', '', 1).replace('-', '', 1).isdigit():
                try: arg = eval(arg)
                except: raise ValueError(f"Value Error: 🚫 Cannot evaluate the expression `{arg}`.")
            try: number = float(arg)
            except: raise TypeError(f"Value Error: 🚫 ACOT expects a numeric value or a math-like string. Got `{arg}`")
            if number == 0: return np.pi / 2  # ACOT(0) = π/2

            return np.arctan(1 / number)

    except AssertionError as ae: raise ValueError(str(ae))
print("ACOT")

def ACOTH(*args: int | float | str) -> float:
    """
    **=ACOTH(number)** Returns the inverse hyperbolic cotangent of a number.
    ACOTH is only defined for values **greater than 1 or less than -1**.

    `Parameters: Only one -> Number (but accepts arithmetics too) int | float | str`

    *Example inputs*:

     ACOTH(2)           -> 0.5493061443
     ACOTH(-2)          -> -0.5493061443
     ACOTH(3+2)       -> 0.5493061443
     ACOTH(-1.5)        -> -0.8047189562
     ACOTH("5 - 0.5")   -> 0.2027325541
    """
    import numpy as np
    try:
        assert args, "Value Error: 🚫 ACOTH() requires one numeric input."
        if len(args) != 1: raise ValueError("Argument Error: 🚫 ACOTH() only takes one input.")
        for arg in args:
            if isinstance(arg, str) and not arg.replace('.', '', 1).replace('-', '', 1).isdigit():
                try: arg = eval(arg)
                except: raise ValueError(f"Evaluate Error: 🚫 Cannot evaluate the expression `{arg}`.")
            try: number = float(arg)
            except: raise TypeError(f"Type Error: 🚫 ACOTH expects a numeric value or a math-like string. Got `{arg}`")
            if -1 < number < 1: raise ValueError("Number Error: 🚫 Input must be less than or equal to -1 or greater than or equal to 1.")
            
            return 0.5 * np.log((number + 1) / (number - 1))
    except AssertionError as ae: raise ValueError(str(ae))
print("ACOTH")

def AMORLINC(cost: float, date_purchased: str, first_period: str, salvage: float, period: int, rate: float, basis: int = 1):
    """
    **=AMORLINC(cost, date_purchased, first_period, salvage, period, rate, [basis])** Returns the **linear depreciation** for each accounting period using the French accounting system.
    This method calculates depreciation linearly, prorated if needed for the first period.

    Parameters:
        cost (float): Initial cost of the asset
        date_purchased (str): Date of purchase (format: 'DD-MM-YYYY')
        first_period (str): End of first accounting period (format: 'DD-MM-YYYY')
        salvage (float): Salvage value at the end of asset life
        period (int): The depreciation period number (0 for first, 1 for second...)
        rate (float): Depreciation rate (e.g., 0.15 for 15%)
        basis (int, optional): Day count basis (default = 1):
            0 = 30/360 US
            1 = Actual/actual
            2 = Actual/360
            3 = Actual/365
            4 = 30/360 European

    Returns:
        float: Depreciation amount for the specified period
    """
    import pandas as pd

    try:
        purchase_date = pd.to_datetime(date_purchased, dayfirst=True)
        period_end = pd.to_datetime(first_period, dayfirst=True)
    except: raise ValueError("🚫 Invalid date format. Use 'DD-MM-YYYY'.")

    if salvage >= cost: raise ValueError("🚫 Salvage value must be less than cost.")
    if rate <= 0: raise ValueError("🚫 Rate must be a positive value.")

    if basis == 0 or basis == 4:
        d1 = purchase_date; d2 = period_end
        days_in_first = ((d2.year - d1.year) * 360 + (d2.month - d1.month) * 30 + (d2.day - d1.day))
        year_basis = 360
    elif basis == 1: days_in_first = (period_end - purchase_date).days; year_basis = 366 if purchase_date.is_leap_year or period_end.is_leap_year else 365
    elif basis == 2: days_in_first = (period_end - purchase_date).days; year_basis = 360
    elif basis == 3: days_in_first = (period_end - purchase_date).days; year_basis = 365
    else: raise ValueError("🚫 Basis must be an integer between 0 and 4.")

    depreciation = 0.0
    for i in range(period + 1):
        if i == 0: depreciation = cost * rate * (days_in_first / year_basis)
        else:
            remaining = cost - (cost * rate * (days_in_first / year_basis)) - ((i - 1) * cost * rate)
            if remaining <= salvage: return 0.0
            depreciation = cost * rate
    return depreciation

if __name__ == "__main__":
    print("EXCELFRED MODULE")

    print(AMORLINC(
    cost=10000,
    date_purchased='01-01-2020',
    first_period='31-12-2020',
    salvage=1000,
    period=2,
    rate=0.2,
    basis=1
))

