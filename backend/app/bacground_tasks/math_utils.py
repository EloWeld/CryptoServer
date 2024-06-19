import numpy as np


def generate_order_grid(current_price, density, drop_percentage, num_orders):
    orders = []

    drop_price = current_price * (1 - drop_percentage / 100)
    total_range = current_price - drop_price
    if density < 1:
        distances = np.array([(density ** i) for i in range(num_orders)][::-1])
    else:
        distances = np.array([((1 / density) ** i) for i in range(num_orders)])

    # Normalize distances so they sum up to the total range
    distances = distances / distances.sum() * total_range

    # Generate prices based on the normalized distances
    for i in range(num_orders):
        if i == 0:
            price = current_price
        else:
            price = orders[-1] - distances[i]
        orders.append(price)

    return np.array(orders)
