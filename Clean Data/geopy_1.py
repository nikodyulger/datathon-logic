from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from functools import partial
from tqdm import tqdm
import pandas as pd


tqdm.pandas()

# Función para parsear los datos que llegan
def get_address(location,prop):
    if location:
        try:
            return location.raw['address'][prop]
        except KeyError:
            return None

# Inicializar objetos para interactuar con API
geolocator =  Nominatim(user_agent="datathon_logic")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

# Leemos fichero con codigos postales
df_zipcodes = pd.read_csv('./zipcodes.csv')
total_zip = df_zipcodes.shape[0]

a = 0
for i in range(0,total_zip,1000):

    df_cities = pd.DataFrame({
        'zipcode': df_zipcodes['zipcode'][i:i+1000] # Por tandas para no perder datos
    })

    #Peticiones a la API -> restringimos la búsqueda dentro de los paises donde MiFarma opera
    df_cities['location'] = df_cities['zipcode'].progress_apply(partial(geocode,country_codes=['es','pt','fr','it','de','ne','gb'],addressdetails=True, exactly_one=True))

    #Parseamos el resultado obtenido en nuevas columnas
    df_cities["coords"] = df_cities['location'].apply(lambda loc: tuple(loc.point) if loc else None)
    df_cities['city'] = df_cities['location'].apply(lambda x: get_address(x,'city'))
    df_cities['state'] = df_cities['location'].apply(lambda x: get_address(x,'state'))
    df_cities['country'] = df_cities['location'].apply(lambda x: get_address(x,'country'))

    #Guardamos los ficheros de cada tanda
    df_cities.to_csv(f'city_info_{a}.csv',index=False)
    a += 1

