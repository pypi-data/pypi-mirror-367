
from astroquery.ipac.nexsci.nasa_exoplanet_archive import NasaExoplanetArchive
from astropy import units as u
from astropy.units import Quantity, UnitTypeError
from astropy.constants import R_earth, M_earth, R_sun, M_sun, G

import pandas as pd
import matplotlib.pyplot as plt


def get_current_parameters(planet_name=['Kepler-22 b']):
  '''
  Returns:
  Pandas Dataframe of stellar and planet parameters

  Args:
  name_planet: list of names of planets in nasa exoplanet archive (string)
  '''
  data=[]
  for i in range(len(planet_name)):
    tab = NasaExoplanetArchive.query_criteria(table="pscomppars", where=f"pl_name='{planet_name[i]}'").to_pandas()
    if len(tab)==0:
      data.append({'pl_name':planet_name[i],           #planet name

      })
      continue
    else:
      planet_dict = tab.to_dict(orient='records')[0]
      data.append({'pl_name':planet_dict['pl_name'],           #planet name
          'hostname':planet_dict['hostname'],       #host star name
          'pl_rade': planet_dict['pl_rade'],          #planet radius [earth radius]
          'pl_masse': planet_dict['pl_masse'] ,        #planet mass [earth mass]
          'pl_ratror': planet_dict['pl_ratror'],        #Ratio of Planet to Stellar Radius
          'st_teff':planet_dict['st_teff'],          #stellar effective temperature [K]
          'st_rad':planet_dict['st_rad'],           #stellar radius [Rsun]
          'st_mass':planet_dict['st_mass'],          #stellar mass [Msun]
          'st_lum':planet_dict['st_lum'],           #Stellar Luminosity [log10(Solar)]
          'st_age' :planet_dict['st_age'],          #stellar age [Gyr]
          'pl_orbper':planet_dict['pl_orbper'],        #Orbital period [days]
          'pl_orbsmax':planet_dict['pl_orbsmax'],       #Orbit Semi-Major Axis [au]
          })
  df=pd.DataFrame(data)
      
  return df

# def evolve_stellar_parameters(stellar_parameters: dict, current_age, target_age) -> dict:

#   return aged_stellar_parameters


# def find_habitable_zone(st_teff, st_lum, pl_mass):

#   inner = 0
#   outer = 0
  
#   bounds = [inner, outer]
#   return bounds

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


def ensure_unit(x, unit: u.Unit):
    """Helper method to ensure input units are correct
    :param x: Variable to check
    :param unit: Desired unit (astropy.unit)
    :returns x: Parameter x with proper unit attached. 
    :raises UnitTypeError: UnitTypeError raised when quantity requires conversion, but conversion cannot be completed
    """

    if x is None:
        return x
    if not isinstance(x, Quantity):
        x = x * unit
    elif x.unit != unit:
        try:
            x = x.to(unit)
        except u.UnitConversionError as uce:
            raise u.UnitTypeError(f"{x} cannot be converted to {unit}")
    return x

def dist_from_Seff(Seff, L):
    """Helper method to convert Seff to distance (AU)"""
    #L must be in solar units
    d = (L / Seff) ** 0.5
    return d


def find_hz(st_teff, st_lum):
    """
    Todo: write documentation
    note that rg0.1, rg1, and rg5 correspond to the 0.1, 1, and 5 Earth mass runaway greenhouse values. 
    """

    def KopparapuEqnFour(SeffSUN, a, b, c, d, tS):
        Seff = SeffSUN + a * tS + b * ((tS) ** 2) + c * ((tS) ** 3) + d * ((tS) ** 4)
        return Seff
    
    L = ensure_unit(st_lum, u.Lsun)
    T_s = ensure_unit(st_teff, u.K) - 5780 * u.K
    
    recent_venus = {'label': 'rv', 'Seff': 1.776000 , 'a': 2.136000e-04 , 'b': 2.533000e-08, 'c': -1.33200e-11, 'd': -3.09700e-15}
    runaway_greenhouse_1Mearth = {'label': 'rg1', 'Seff': 1.107, 'a': 1.332000e-04 , 'b': 1.580000e-08, 'c': -8.30800e-12, 'd': -1.93100e-15}
    maximum_greenhouse = {'label': 'mxg', 'Seff': 3.560000e-01, 'a': 6.171000e-05 , 'b': 1.698000e-09, 'c': -3.19800e-12, 'd': -5.57500e-16}
    early_mars = {'label': 'em', 'Seff': 3.200000e-01, 'a': 5.547000e-05 , 'b': 1.526000e-09, 'c': -2.87400e-12, 'd': -5.01100e-16}
    runaway_greenhouse_5Mearth = {'label': 'rg5', 'Seff': 1.188000, 'a': 1.433000e-04 , 'b': 1.707000e-08, 'c': -8.96800e-12, 'd': -2.08400e-15}
    runaway_greenhouse_01Mearth = {'label': 'rg0.1', 'Seff': 9.900000e-01, 'a': 1.209000e-04 , 'b': 1.404000e-08, 'c': -7.41800e-12, 'd': -1.71300e-15}
    
    coeff_matrix = pd.DataFrame([recent_venus, runaway_greenhouse_01Mearth, runaway_greenhouse_1Mearth, 
                                 runaway_greenhouse_5Mearth, maximum_greenhouse, early_mars])
    coeff_matrix.set_index('label', inplace=True)

    #Add column with the result of eqn. 4 in Kopparapu 2014
    for index, row in coeff_matrix.iterrows():
        #todo carry units through
        SeffBound = KopparapuEqnFour(row['Seff'], row['a'], row['b'], row['c'], row['d'], T_s.value)
        coeff_matrix.at[index,'SeffBound'] = SeffBound
        coeff_matrix.at[index,'distBound(AU)'] = dist_from_Seff(SeffBound, L.value)
        
    
    return coeff_matrix