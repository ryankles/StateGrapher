import pandas as pd
import matplotlib.pyplot as plt 
from shapely.geometry import Polygon, MultiPolygon
import geopy.distance
from tkinter import messagebox
import tkinter as tk



df = pd.read_csv('state_points.csv')

df = df[['STATE_NAME', 'POINT_X', 'POINT_Y']]

#funtion to get state center
def get_state_center(state_name):
    state_points = df[df['STATE_NAME'] == state_name]
    
    # Compute the center of the state
    center_longitude = state_points['POINT_X'].mean()
    center_latitude = state_points['POINT_Y'].mean()
    
    return center_longitude, center_latitude

#function to get perimeter
def get_state_perimeter(state_name):
    state_points = df[df['STATE_NAME'] == state_name]
    
    if state_points.empty:
        print("Invalid state name.")
        return None
    
    points = [(row['POINT_Y'], row['POINT_X']) for index, row in state_points.iterrows()]
    
    polygon = Polygon(points)
    
    perimeter_degrees = polygon.length
    
    center_latitude = state_points['POINT_Y'].mean()
    degrees_per_km = geopy.distance.distance((center_latitude, points[0][1]), (center_latitude, points[0][1] + 1)).km
    
    perimeter_km = perimeter_degrees * degrees_per_km
    
    return perimeter_km

#function to calculate state area
def get_state_area(state_name):
    state_points = df[df['STATE_NAME'] == state_name]
    
    if state_points.empty:
        print("Invalid state name.")
        return None
    
    points = [(row['POINT_Y'], row['POINT_X']) for index, row in state_points.iterrows()]
    
    polygon = Polygon(points)

    xs, ys = polygon.exterior.coords.xy
    area = 0.5 * abs(sum(xs[i] * ys[i+1] - xs[i+1] * ys[i] for i in range(-1, len(xs)-1)))
    
    center_latitude = state_points['POINT_Y'].mean()
    degrees_per_km = geopy.distance.distance((center_latitude, points[0][1]), (center_latitude, points[0][1] + 1)).km ** 2
    
    area_km2 = area * degrees_per_km
    
    return area_km2

#function to plot state
def plot_state(state_name):
    state_points = df[df['STATE_NAME'] == state_name]

    points = [(row['POINT_X'], row['POINT_Y']) for _, row in state_points.iterrows()]

    polygons = []
    #Logic to keep land separated when over water
    current_polygon_points = []
    all_polygon_points = []
    while all_polygon_points != points:
        for point in points:
            if point in current_polygon_points:
                current_polygon_points.append(point)
                polygons.append(Polygon(current_polygon_points))
                current_polygon_points = []
            else:
                current_polygon_points.append(point)
            all_polygon_points.append(point)
    current_polygon_points.append(point)
    if len(current_polygon_points) > 2:
        polygons.append(Polygon(current_polygon_points))

    multi_polygon = MultiPolygon(polygons)

    center_longitude, center_latitude = get_state_center(state_name)

    perimeter_km = get_state_perimeter(state_name)
    area_km2 = get_state_area(state_name)

    #Plotting the state
    fig, ax = plt.subplots(figsize=(10, 10))
    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
    ax.set_aspect('equal')
    ax.set_title(state_name)

    if len(polygons) == 1:
        polygon = polygons[0]
        ax.plot(*polygon.exterior.xy, color='black')
    else:
        for polygon in multi_polygon.geoms:
            ax.plot(*polygon.exterior.xy, color='black')

    ax.plot(center_longitude, center_latitude, marker='o', color='red')
    ax.annotate(f'({center_latitude:.2f}, {center_longitude:.2f})', (center_longitude, center_latitude))

    bounds = multi_polygon.bounds if len(polygons) > 1 else polygon.bounds
    min_longitude, max_longitude = bounds[0], bounds[2]
    min_latitude, max_latitude = bounds[1], bounds[3]
    delta_longitude = (max_longitude - min_longitude) * 0.2
    delta_latitude = (max_latitude - min_latitude) * 0.2
    ax.set_xlim(min_longitude - delta_longitude, max_longitude + delta_longitude)
    ax.set_ylim(min_latitude - delta_latitude, max_latitude + delta_latitude)

    ax.text(0.05, 0.95, f'Perimeter: {perimeter_km:.2f} km', transform=ax.transAxes)
    ax.text(0.05, 0.9, f'Area: {area_km2:.2f} km²', transform=ax.transAxes)

    plt.show()


#function for button press
def get_results():
    state = state_entry.get().title()

    if state in state_list:
        print(plot_state(state))
    else:
        messagebox.showerror("Error", "Invalid state. Please enter a valid state.")

#Using tkinter for input
window = tk.Tk()
#window.geometry("300x100")
window.title("USA State Grapher")

state_label = tk.Label(window, text="Enter a state:")
state_label.pack()

state_entry = tk.Entry(window)
state_entry.pack()

results_button = tk.Button(window, text="Veiw Map", command=get_results)
results_button.pack()

state_list = ["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"]

window.mainloop()