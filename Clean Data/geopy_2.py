from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from functools import partial
from tqdm import tqdm
import pandas as pd

tqdm.pandas()

# Se concatenan todos los fichero resultantes del primer script
df_cities = pd.concat([pd.read_csv(f'./city_info_{i}.csv', index_col=None, header=0) for i in range(0,12) ], axis=0,ignore_index=True)
df_cities.to_csv('./city_info.csv',index=False)
# Vimos que hay bastantes codigos postales con los que no encuentra información
print(df_cities.isna().sum())

# df_cities = pd.read_csv('./city_info.csv')
df_items = pd.read_csv('./items_ordered_2years.txt',sep='|',on_bad_lines='skip')

#El procedimeinto es el mismo que antes, tan solo cambia la manera en la que se crea la query
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

#Nos quedamos con aquellos zipcodes que no se encontró información
zipcodes = df_cities[df_cities['state'].isna()]['zipcode'].to_list()

#De la tabla de items nos quedamos con la ciudad y el codigo postal -> quitando duplicados para no hacer peticiones repetidas a la API
df_query = df_items[df_items['zipcode'].isin(zipcodes)][['city','zipcode']].drop_duplicates()
# print(df_query.shape) -> alreadedor de 2500 filas

#Concatenamos las dos columnas y las guardamos en una nueva
df_query['query'] = df_query.apply(lambda row: ' '.join(row.values.astype(str)), axis=1)

#Peticiones a la API, pero esta vez con una query diferente
df_query['location'] = df_query['query'].progress_apply(partial(geocode,country_codes=['es','pt','fr','it','de','ne','gb'],addressdetails=True, exactly_one=True))

#Parseamos al igual que antes el resultado obtenido en nuevas columnas
df_query["coords"] = df_query['location'].apply(lambda loc: tuple(loc.point) if loc else None)
df_query['city_y'] = df_query['location'].apply(lambda x: get_address(x,'city'))
df_query['state'] = df_query['location'].apply(lambda x: get_address(x,'state'))
df_query['country'] = df_query['location'].apply(lambda x: get_address(x,'country'))

# Guardamos el resultado
df_query.to_csv('./query.csv',index=False)

