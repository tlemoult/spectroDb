import csv,os,json
import tkinter as tk
import tkinter.filedialog
from tkinter import ttk
from tkinter import messagebox

import astropy.units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, get_sun, get_moon
from astropy.visualization import astropy_mpl_style

from libindi.telescope import TelescopeClient as Telescope
import libcalc.util as myUtil
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.dates import HourLocator, DateFormatter

class App(tk.Frame):
    def __init__(self, config,master=None):
        super().__init__(master)
        self.master = master
        self.grid()
        self.create_widgets()
        self.config = config
        self.telescope = None

    def create_widgets(self):

        self.data_table = ttk.Treeview(self, columns=("col1", "col2", "col3", "col4","col5","col6"))
        self.data_table.heading("#0", text="Row")
        self.data_table.heading("col1", text="name")
        self.data_table.heading("col2", text="RA")
        self.data_table.heading("col3", text="DEC")
        self.data_table.heading("col4", text="mag")
        self.data_table.heading("col5", text="Status")
        self.data_table.heading("col6", text="comment")

        self.data_table.column("#0", width=50, stretch=False)
        self.data_table.column("col1", width=120)
        self.data_table.column("col2", width=120)
        self.data_table.column("col3", width=120)
        self.data_table.column("col4", width=50)
        self.data_table.column("col5", width=50)
        self.data_table.column("col6", width=700)
        self.data_table.grid(row=0, column=0, padx=10, pady=10)

        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.data_table.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.data_table.configure(yscrollcommand=self.scrollbar.set)

## in a frame#
        self.button_frame = tk.Frame(self)
        self.button_frame.grid(row=1, column=0)

        self.load_button = tk.Button(self.button_frame, text="Load LST", command=self.load_csv)
        self.load_button.grid(row=0, column=0)

        self.clean_button = tk.Button(self.button_frame, text="clear all data", command=self.clear_csv)
        self.clean_button.grid(row=0, column=1)

        self.clean_1_button = tk.Button(self.button_frame, text="clear one", command=self.clear_one)
        self.clean_1_button.grid(row=0, column=2)

        self.save_button = tk.Button(self.button_frame, text="Save LST", command=self.save_csv)
        self.save_button.grid(row=0, column=3)


## in a second frame  ##
        self.action_frame = tk.Frame(self)
        self.action_frame.grid(row=2,column=0)

        self.button1 = tk.Button(self.action_frame, text="Connect Telescope", command=self.button_connect_telescope)
        self.button1.grid(row=0, column=0, padx=10, pady=10, sticky="E")

        self.process_button = tk.Button(self.action_frame, text="Point Telescope", state="disabled", command=self.point_telescope)
        self.process_button.grid(row=0, column=1, padx=10, pady=10)

        self.button2 = tk.Button(self.action_frame, text="Plot altitude", command=self.button2_action)
        self.button2.grid(row=0, column=2, padx=10, pady=10, sticky="E")

        self.button_3 = tk.Button(self.action_frame, text="Button 3")
        self.button_3.grid(row=1, column=0, padx=10, pady=10, sticky="E")

        self.button4 = tk.Button(self.action_frame, text="Button 4", command=self.button4_action)
        self.button4.grid(row=1, column=1, padx=10, pady=10, sticky="E")

        self.button5 = tk.Button(self.action_frame, text="Button 5", command=self.button5_action)
        self.button5.grid(row=1, column=2, padx=10, pady=10, sticky="E")

# a frame for SIMBAD
        self.simbad_frame = tk.Frame(self)
        self.simbad_frame.grid(row=3,column=0)

        self.simbad_entry_label = tk.Label(self.simbad_frame,text='star Name')
        self.simbad_entry_label.grid(row=0,column=0)

        self.simbad_entry = tk.Entry(self.simbad_frame)
        self.simbad_entry.grid(row=0,column=1)

        self.button_SIMBAD = tk.Button(self.simbad_frame, text="Get SIMBAD coords", command=self.button_SIMBAD_action)
        self.button_SIMBAD.grid(row=0, column=2, padx=10, pady=10, sticky="E")



    def load_csv(self):
        file_path = tk.filedialog.askopenfilename(initialdir = "/mnt/gdrive/astro/cibles/" , filetypes=[("PRISM files", "*.lst")])
        with open(file_path, "r",encoding="latin-1", errors='ignore') as lst_file:
            print(f"Load target list in file_path = {file_path}")
            for i, line in enumerate(lst_file):
                # isolate the  "name" begin of the line
                a = line.split('"')
                if a[0] == '' and (len(a)>3):
                    name = a[1]
                else:
                    print(f"Cannot find target name in line = {line}")
                    continue
                #print(f"name = {name}")
                row = [name]
                restOfData = line.lstrip('"'+name+'"').strip()
                #print(f" restOfData=[{restOfData}]")
                row = row + restOfData.split('  ')
                self.data_table.insert("", "end", text=str(i), values=row[:5]+row[6:])

        self.process_button["state"] = "normal"

    def clear_csv(self):
        for item in self.data_table.get_children():
            self.data_table.delete(item)

    def clear_one(self):
        selected_index = self.data_table.selection()
        self.data_table.delete(selected_index)

    def save_csv(self):
        f_save = tkinter.filedialog.asksaveasfile(initialdir = "/mnt/gdrive/astro/cibles/" , mode="w",defaultextension=".lst")
        if f_save is None:
            return
        for line in self.data_table.get_children():
            data_fields = self.data_table.item(line)['values']
            lineText = '"'+data_fields[0]+'"  '
            for value in data_fields[1:-1]:
                lineText = lineText + str(value) + '  '
            lineText += '1  "'+data_fields[-1]+'"'
            print(f"write line {lineText}")
            f_save.write(lineText.strip()+'\n')
        f_save.close()

    def point_telescope(self):
        selected_index = self.data_table.selection()
        selected_row = self.data_table.item(selected_index)["values"]
        # Call your data processing function with the selected row here
#        print(f"Select index is {selected_index}")
        print(f"Select row is {selected_row}")
        [targetName,targetRA,targetDEC] = selected_row[0:3]
#        print(f"targetName = {targetName} targetRA={targetRA}  targetDEC = {targetDEC}")

        strCoordJ2000 = (targetRA+' '+targetDEC).replace("°",'d').replace("''",'s').replace("'",'m')
#        print(f"strCoordJ2000 = {strCoordJ2000}")

        J2000Target = SkyCoord(strCoordJ2000, frame='icrs')
        obsSite=myUtil.getEarthLocation(self.config)
        CoordTelescopeTarget= myUtil.convJ2000toJNowRefracted(J2000Target,obsSite)

        time = Time.now()
        altAzJ2000 = J2000Target.transform_to(AltAz(obstime=time,location=obsSite))
#        print(f"Target {targetName} = {altAzJ2000.alt} deg")

#        print(f"JNow refracted coordinates = {CoordTelescopeTarget}")

        confirmed = messagebox.askyesno(
            "Confirmation",
            f"Are you sure you want to point telescope at [{targetName}]\n {J2000Target.to_string(style='hmsdms')}\n Alt = {altAzJ2000.alt.dms[0]} deg ?"
            )
        if not confirmed:
            return

        if not self.telescope == None:
            self.telescope.slewTelescope(CoordTelescopeTarget)
        else:
            print(f"Connect first telescope")




    def button_connect_telescope(self):
        self.telescope=Telescope(self.config['telescope'])
        if not self.telescope.connect():
            print(f"Failed to connect to telescope {self.config['telescope']}")
            self.telescope = None
        else:
            print("Telescope connected")
            self.button1["state"] = "disabled"

    def button2_action(self):
        print("Button2 action")
        # Define the location and time
        obs_location=myUtil.getEarthLocation(self.config)

        # Define the star coordinates
        selected_index = self.data_table.selection()
        selected_row = self.data_table.item(selected_index)["values"]
        [targetName,targetRA,targetDEC] = selected_row[0:3]
        strCoordJ2000 = (targetRA+' '+targetDEC).replace("°",'d').replace("''",'s').replace("'",'m')
        star_coord = SkyCoord(strCoordJ2000, frame='icrs')

        # Create an array of times at 1-minute intervals for the entire night
        times = Time.now() + np.linspace(0, 16, 100)*u.hour

        # Calculate the star's altitude at each time
        altaz = star_coord.transform_to(AltAz(obstime=times, location=obs_location))
        altitudes = altaz.alt.deg

        # Calculer les positions actuelles du soleil et de la lune par rapport à l'observateur
        sun_altaz = get_sun(times).transform_to(AltAz(obstime=times, location=obs_location))
        moon_altaz = get_moon(times).transform_to(AltAz(obstime=times, location=obs_location))

        # Plot the altitude vs. time
        fig, ax = plt.subplots(figsize=(14,6))
        ax.plot(times.datetime, altitudes, label=targetName)

        # Set the x-axis locator and formatter for hourly ticks
        ax.xaxis.set_major_locator(HourLocator())
        ax.xaxis.set_major_formatter(DateFormatter('%H:%M'))

        # Remplir la zone de jour et de nuit
        ax.fill_between(times.datetime, 0, 90,
                        where=sun_altaz.alt.deg > -18,
                        color='orange', alpha=0.2, transform=ax.get_xaxis_transform())
        ax.fill_between(times.datetime, 0, 90,
                        where= sun_altaz.alt.deg < -12,
                        color='yellow', alpha=0.2, transform=ax.get_xaxis_transform())
        ax.fill_between(times.datetime, 0, 90,
                        where=sun_altaz.alt.deg < -18,
                        color='blue', alpha=0.2, transform=ax.get_xaxis_transform())

        # Ajouter les positions actuelles du soleil et de la lune
        ax.plot(times.datetime, sun_altaz.alt.deg, color='yellow', label='Soleil')
        ax.plot(times.datetime, moon_altaz.alt.deg, color='gray', label='Lune')


        ax.set_xlabel('Time (UTC)')
        ax.set_ylabel('Altitude (degrees)')
        title =  f'Altitude of {targetName} Over Night start at {Time.now()}\n'
        title += f'Observatory {obs_location}'
        ax.set_title(title)

        plt.grid(True)
        plt.legend(loc='upper right')
        plt.show()



    def button_SIMBAD_action(self):
        targetName = self.simbad_entry.get()

        #J2000Target = myUtil.getCoordFromName(targetName)
        J2000Target, v_mag, sp_type, object_type = myUtil.get_star_info(targetName)

        raStr = str(J2000Target.ra.to_string(u.hour,precision=2))
        decStr = str(J2000Target.dec.to_string(u.degree, alwayssign=True,precision=2))
        print(f"Target Name = {targetName} SIMBAD coord {raStr} {decStr}")

        row = [targetName,raStr,decStr,str(v_mag),"FALSE","object_type="+str(object_type)+", sp_type="+str(sp_type)]
        self.data_table.insert("", "end", values=row)
        self.process_button["state"] = "normal"

    def button4_action(self):
        print("Button4 action")

    def button5_action(self):
        print("Button5 action")


#load configuration
spectro_config = os.environ['SPECTROCONFIG']
configFilePath = os.path.join(spectro_config,'acquire.json')
print(f"Configuration file is {configFilePath}")
json_text=open(configFilePath).read()
config = json.loads(json_text)

root = tk.Tk()
root.title("Target list")
app = App(config,master=root)
app.mainloop()
