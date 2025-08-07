import matplotlib.pyplot as plt
import pandas as pd


d_TEST = {'time': pd.Series([0, 1, 2, 3]),
     'distance_hz_in': pd.Series([0.8, 0.8, 0.9, 1.2]),
     'distance_hz_out': pd.Series([1, 1, 1.1, 1.5]),
                      }

df_TEST = pd.DataFrame(d_TEST)

def visualize(df, time_bc, distance_bc, planet_AU):
    """
    Inputs
    ------

    df : dataframe
        Columns are time, distance_hz_in, distance_hz_out
    
    time_bc : list
        The lower and upper time boundary conditions for your plot. Units in Gyr
    
    distance_bc : list
        The lower and upper distance-from-star boundary conditions for your plot. Units in AU
    
    planet_AU : list
        List of planet distances from star in AU
    
    Returns
    -------
    plots how habitable zone changes over time
    """

    df = df[(df.time > time_bc[0]) | (df.time < time_bc[1])] # trim x axis

    plt.fill_between(df["time"], df["distance_hz_in"], y2= df["distance_hz_out"], color = 'green', alpha = 0.4)
    
    for i in planet_AU:
        plt.axhline(y=i, color='k', linestyle='--')

    plt.ylim(distance_bc)

    plt.title("Habitable Zone over Time")
    plt.xlabel("Time (Gyr)")
    plt.ylabel("Distance from Star (AU)")

    plt.show()


TEST_plot = visualize(df_TEST, [0,4], [0.5,1.7], [0.7, 1.1, 1.5])