import numpy as np
import matplotlib.pyplot as plt
import matplotlib


def generate_order_grid(current_price, density, multiplier, drop_percentage, num_orders):
    orders = []
    volumes = []

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

        if i == 0:
            volumes.append(1)  # Начальный объем
        else:
            volumes.append(volumes[-1] * multiplier)

    return np.array(orders), np.array(volumes)


def plot_order_grid(current_price, density=0.7, multiplier=1.5, drop_percentage=8.1, num_orders=10):
    orders, volumes = generate_order_grid(current_price, density, multiplier, drop_percentage, num_orders)
    plt.figure(figsize=(10, 6))
    for i, order in enumerate(orders):
        plt.axhline(order, color='blue', linestyle='--', linewidth=1)
        print(order)
        plt.annotate(f'{order:.2f}', xy=(0, order), xytext=(5, 5), textcoords='offset points', color='blue')

    plt.axhline(current_price, color='red', linestyle='-', linewidth=2, label='Current Price')
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.title('Order Grid')
    plt.legend()
    plt.grid(True)
    plt.show()
    plt.savefig('order_grid.png')  # Сохранить график в файл


# Пример использования
current_price = 64864
plot_order_grid(current_price, density=0.7, multiplier=1.5, num_orders=10, drop_percentage=8.1)
