def get_percent_change(current:float, bought:float):
    return (current-bought)/bought*100

def get_current_value(price:float, amount:float):
    return price*amount