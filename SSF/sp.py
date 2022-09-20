import geopy.distance 

coords_1 = (-1.304967,36.8261)
coords_2 = (-1.30485,36.826217)

print(geopy.distance.geodesic(coords_1, coords_2).m)