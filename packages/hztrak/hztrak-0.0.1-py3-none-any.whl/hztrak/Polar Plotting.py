import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

d_TEST = {
    'time': pd.Series([0, 1, 2, 3, 4, 5, 6]),
    'distance_planet_star': pd.Series([0.6, 1.0, 1.3, 1.8, 2.0, 2.2, 2.6]),
    'distance_hz_in': pd.Series([0.5]*7),
    'distance_hz_out': pd.Series([2.5]*7),
}

df_TEST = pd.DataFrame(d_TEST)

def visualize(df, time_bc, distance_bc, habitable_zone):
    
    # Filter based on time and distance
    df = df[(df.time > time_bc[0]) & (df.time < time_bc[1])]
    df = df[(df.distance_planet_star > distance_bc[0]) & (df.distance_planet_star < distance_bc[1])]

    theta = np.linspace(0, 2*np.pi, len(df), endpoint=False)
    r = df['distance_planet_star']
    colors = r
    area = 200

    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(projection='polar')

    theta_fill = np.linspace(0, 2*np.pi, 500)
    r_inner, r_outer = habitable_zone
    ax.fill(theta_fill, [r_outer]*len(theta_fill), color='lightgreen', alpha=0.3, zorder=0)
    ax.fill(theta_fill, [r_inner]*len(theta_fill), color='white', alpha=1.0, zorder=1)

    ax.scatter(0, 0, marker='*', color='gold', s=500, label='The star', zorder=5)

    scatter = ax.scatter(theta, r, c=colors, s=area, cmap='plasma', alpha=0.75, zorder=3)

    plt.colorbar(scatter, ax=ax, label='Distance from the star (AU)')
    ax.set_title('Polar plot of the planets in the habitable zone')

    plt.show()

habitable_zone = (1.0, 2.0)

visualize(df_TEST, [0, 7], [0.4, 3.0], habitable_zone)
