def prime_number_finder(value):
    if value <= 1:
        return f"{value} asal değildir."

    for i in range(2, int(value**0.5) + 1):
        if value % i == 0:
            return f"{value} asal değildir."
    
    return f"{value} asaldır."

prime_number_finder(2)
