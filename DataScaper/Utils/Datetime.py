def date_assembler(year, month, day):
    """Assemble the date to the format: YYYY-MM-DD"""
    if month < 10:
        month = f'0{month}'
    if day < 10:
        day = f'0{day}'
    return f'{year}-{month}-{day}'