import csv,os,json
import tkinter as tk
import tkinter.filedialog
from tkinter import ttk
from tkinter import messagebox

import astropy.units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, get_sun, get_moon
from astropy.visualization import astropy_mpl_style
import libobs.telescopePoint

from libindi.telescope import TelescopeClient as Telescope
from libindi.camera import CameraClient as Camera
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
        self.path_target_files = "/home/tlemoult/Documents/cibles/ohp2023/"

    def sort_treeview(self,tree, col, reverse):
        # Récupérer les éléments du Treeview et les trier en utilisant la colonne spécifiée
        data = [(tree.set(child, col), child) for child in tree.get_children('')]
        data.sort(reverse=reverse)

        # Re-insérer les éléments triés dans le Treeview
        for index, (val, child) in enumerate(data):
            tree.move(child, '', index)

        # Changer la commande associée au clic sur l'en-tête pour le tri inverse
        tree.heading(col, command=lambda: self.sort_treeview(tree, col, not reverse))

    def create_widgets(self):

        self.data_table = ttk.Treeview(self, columns=("col1", "col2", "col3", "col4","col5","col6"))
        self.data_table.heading("#0", text="Row")
        self.data_table.heading("col1", text="name", command=lambda: self.sort_treeview(self.data_table, "col1", False))
        self.data_table.heading("col2", text="RA", command=lambda: self.sort_treeview(self.data_table, "col2", False))
        self.data_table.heading("col3", text="DEC", command=lambda: self.sort_treeview(self.data_table, "col3", False))
        self.data_table.heading("col4", text="mag", command=lambda: self.sort_treeview(self.data_table, "col4", False))
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

        self.button_3 = tk.Button(self.action_frame, text="edit data", command=self.edit_one_popup)
        self.button_3.grid(row=1, column=0, padx=10, pady=10, sticky="E")

        self.button4 = tk.Button(self.action_frame, text="Point Tel Astro", command=self.button_precise_point)
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
        file_path = tk.filedialog.askopenfilename(initialdir = self.path_target_files , filetypes=[("PRISM files", "*.lst")])
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
                restOfData = line[len(name)+4:].strip()
                #print(f" restOfData=[{restOfData}]")
                row = row + restOfData.split('  ')
                self.data_table.insert("", "end", text=str(i), values=row[:5]+[row[6].replace('"','')])

        self.process_button["state"] = "normal"

    def clear_csv(self):
        for item in self.data_table.get_children():
            self.data_table.delete(item)

    def clear_one(self):
        selected_index = self.data_table.selection()
        self.data_table.delete(selected_index)

    def edit_one_popup(self):
        # Fonction pour enregistrer les modifications et fermer la fenêtre
        def save_changes():
            variable1.set(entry_var1.get())
            variable2.set(entry_var2.get())
            variable3.set(entry_var3.get())
            variable4.set(entry_var4.get())
            variable5.set(entry_var5.get())
            variable6.set(entry_var6.get())
            top.destroy()

        # Création de la fenêtre pop-up
        top = tk.Toplevel()
        top.title("Target edit")

        # recupere les valeur actuelles
        selected_index = self.data_table.selection()
        selected_row = self.data_table.item(selected_index)["values"]
        print(f"Select row is {selected_row}")
        [targetName,targetRA,targetDEC,targetMag,targetStatus,targetComment] = selected_row[0:6]

        # Variables
        variable1 = tk.StringVar()
        variable2 = tk.StringVar()
        variable3 = tk.StringVar()
        variable4 = tk.StringVar()
        variable5 = tk.StringVar()
        variable6 = tk.StringVar()

        # Valeurs initiales des variables
        variable1.set(targetName)
        variable2.set(targetRA)
        variable3.set(targetDEC)
        variable4.set(targetMag)
        variable5.set(targetStatus)
        variable6.set(targetComment)

        # Labels et champs d'édition pour chaque variable
        myWidth = 200
        label_var1 = tk.Label(top, text="Name")
        entry_var1 = tk.Entry(top, textvariable=variable1, width=myWidth)
        label_var2 = tk.Label(top, text="RA J2000")
        entry_var2 = tk.Entry(top, textvariable=variable2, width=myWidth)
        label_var3 = tk.Label(top, text="DEC J2000")
        entry_var3 = tk.Entry(top, textvariable=variable3, width=myWidth)
        label_var4 = tk.Label(top, text="mag")
        entry_var4 = tk.Entry(top, textvariable=variable4, width=myWidth)
        label_var5 = tk.Label(top, text="status")
        entry_var5 = tk.Entry(top, textvariable=variable5, width=myWidth)
        label_var6 = tk.Label(top, text="comment")
        entry_var6 = tk.Entry(top, textvariable=variable6, width=myWidth)

        # Bouton de validation
        button_save = tk.Button(top, text="Valider", command=save_changes)

        # Placement des widgets dans la fenêtre
        label_var1.pack()
        entry_var1.pack()
        label_var2.pack()
        entry_var2.pack()
        label_var3.pack()
        entry_var3.pack()
        label_var4.pack()
        entry_var4.pack()
        label_var5.pack()
        entry_var5.pack()
        label_var6.pack()
        entry_var6.pack()
        button_save.pack()

        # Attend que la fenêtre soit fermée
        top.wait_window(top)

        # Affiche les contenus des variables après la fermeture de la fenêtre
        print("Contenu des variables après modification :")
        print("Variable 1:", variable1.get())
        print("Variable 2:", variable2.get())
        print("Variable 3:", variable3.get())
        print("Variable 4:", variable4.get())
        print("Variable 5:", variable5.get())
        print("Variable 6:", variable6.get())
   
        self.data_table.item(selected_index,text="",values= (variable1.get(),variable2.get(),variable3.get(),variable4.get(),variable5.get(),variable6.get()))

    def save_csv(self):
        f_save = tkinter.filedialog.asksaveasfile(initialdir = self.path_target_files , mode="w",defaultextension=".lst")
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

    def button_precise_point(self):
        selected_index = self.data_table.selection()
        selected_row = self.data_table.item(selected_index)["values"]
        print(f"Select row is {selected_row}")
        [targetName,targetRA,targetDEC] = selected_row[0:3]
        strCoordJ2000 = (targetRA+' '+targetDEC).replace("°",'d').replace("''",'s').replace("'",'m')
        J2000Target = SkyCoord(strCoordJ2000, frame='icrs')
        print(f"We point the object name = {targetName}  coord J2000 = {J2000Target}")

        obsSite=myUtil.getEarthLocation(config)

        # connect camera
        if False:
            print("We use the guiding field of spectro")
            configCamera = config["ccdGuide"]
        else:
            print("We use the electronic finder")
            configCamera = config["ccdFinder"]

        print(f"camera is {configCamera['name']}")
        camera = Camera(configCamera)

        for loopIndex in range(2):
            libobs.telescopePoint.astrometry(loopIndex,camera,configCamera,self.telescope,J2000Target,obsSite,self.config)

    def button5_action(self):
        pass


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
