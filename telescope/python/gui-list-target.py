import csv,os,json
import tkinter as tk
import tkinter.filedialog
from tkinter import ttk

from astropy.coordinates import SkyCoord
import libcalc.util as myUtil

class App(tk.Frame):
    def __init__(self, config,master=None):
        super().__init__(master)
        self.master = master
        self.grid()
        self.create_widgets()
        self.config = config

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

        self.process_button = tk.Button(self.action_frame, text="Point Telescope", state="disabled", command=self.point_telescope)
        self.process_button.grid(row=0, column=0, pady=10)

        self.button1 = tk.Button(self.action_frame, text="Button 1", command=self.button1_action)
        self.button1.grid(row=0, column=1, padx=10, pady=10, sticky="E")

        self.button2 = tk.Button(self.action_frame, text="Button 2", command=self.button2_action)
        self.button2.grid(row=0, column=2, padx=10, pady=10, sticky="E")

        self.button3 = tk.Button(self.action_frame, text="Button 3", command=self.button3_action)
        self.button3.grid(row=1, column=0, padx=10, pady=10, sticky="E")

        self.button4 = tk.Button(self.action_frame, text="Button 4", command=self.button4_action)
        self.button4.grid(row=1, column=1, padx=10, pady=10, sticky="E")

        self.button5 = tk.Button(self.action_frame, text="Button 5", command=self.button5_action)
        self.button5.grid(row=1, column=2, padx=10, pady=10, sticky="E")

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
                self.data_table.insert("", "end", text=str(i), values=row)

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
            lineText = ""
            for value in self.data_table.item(line)['values']:
                lineText = lineText + str(value) + '  '
            print(f"write line {lineText}")
            f_save.write(lineText.strip()+'\n')
        f_save.close()

    def point_telescope(self):
        selected_index = self.data_table.selection()
        selected_row = self.data_table.item(selected_index)["values"]
        # Call your data processing function with the selected row here
        print(f"Select index is {selected_index}")
        print(f"Select row is {selected_row}")
        [targetName,targetRA,targetDEC] = selected_row[0:3]
        print(f"targetName = {targetName} targetRA={targetRA}  targetDEC = {targetDEC}")

        strCoordJ2000 = (targetRA+' '+targetDEC).replace("°",'d').replace("''",'s').replace("'",'m')
        print(f"strCoordJ2000 = {strCoordJ2000}")

        J2000Target = SkyCoord(strCoordJ2000, frame='icrs')
        obsSite=myUtil.getEarthLocation(self.config)
        CoordTelescopeTarget= myUtil.convJ2000toJNowRefracted(J2000Target,obsSite)

        print(f"JNow refracted coordinates = {CoordTelescopeTarget}")




    def button1_action(self):
        print("Button1 action")

    def button2_action(self):
        print("Button2 action")

    def button3_action(self):
        print("Button3 action")

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
