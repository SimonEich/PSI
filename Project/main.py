import customtkinter as customtkinter
from customtkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk
import numpy as np
import cv2
import pandas as pd
from datetime import datetime
import os
import vision
import coordinate_system
from fanuc_py_xyw_chunk_debug import Robot

vision_data=[]
detectSquareImg=0

def file_browser():
    print("Opening next UI")
    file = filedialog.askopenfile()
    if file:
        file_extension = os.path.splitext(file.name)[1]
        if file_extension == '.xlsx':
            df = pd.read_excel(file.name, header=None)
        elif file_extension == '.csv':
            df = pd.read_csv(file.name, header=None, delimiter=';')
        else:
            print(
                "Dateityp wird nicht unterstützt, .csv oder .xlsx verwenden. Siehe Dokumentation bezüglich Standard von Wafewr Map Datei ")
            return

        waver_typ = df.iloc[0, 1]
        wafer = df.iloc[1, 1]
        current_datetime = datetime.now()
        data_array = df.iloc[7:].to_numpy()

        # Information zu Qualität wird in VAR gespeichert
        quality_values = [str(row[1]) for row in data_array]
        # Anzahl von Chip wird herausgelesen
        chip_quantity = len(quality_values)
        chip_quantity_ = f"{chip_quantity:02}"

        # Calculate the number of good chips (quality != 0)
        good_chip_count = len([row for row in data_array if row[1] != '0' and row[1] != 0])
        good_chip_count_ = f"{good_chip_count:02}"

        # STRING für KAREL (Fanuc) wird erstellt
        # setregister --> Funktionsname in Karel
        cmd = f"setregister:{chip_quantity_}:{good_chip_count_}:{':'.join(quality_values)}"
        print(cmd)

        data_array = [row for row in data_array if row[1] != 0]

        ablagepunkt = [[0 for x in range(4)] for y in range(99)]
        for i in range(min(99, len(data_array))):
            for j in range(4):
                if i * 4 + j < len(data_array):
                    ablagepunkt[i][j] = data_array[i * 4 + j][0]

        ablagepunkt_indices = [(i, j) for i in range(99) for j in range(4) if ablagepunkt[i][j] != 0]
        ablagepunkt_index_1 = [index[0] + 1 for index in ablagepunkt_indices]
        ablagepunkt_index_2 = [index[1] + 1 for index in ablagepunkt_indices]

        waver_info_df = pd.DataFrame({
            'Waver Typ': [waver_typ] * len(data_array),
            'Wafer Nummer': [wafer] * len(data_array),
            'Chip Nummer': [row[0] for row in data_array],
            'Qualitaet': [row[1] for row in data_array],
            'Gel Pak Nummer': ablagepunkt_index_1,
            'Position auf Gel Pak': ablagepunkt_index_2
        })

        robot = Robot(
            robot_model="Fanuc",
            host="127.0.0.1",
            port=18735,
            ee_DO_type="RDO",
            ee_DO_num=7,
        )
        robot.connect()
        robot.setregister(cmd=cmd)
        robot.disconnect()

        output_file_xlsx = f"{waver_typ}_Wafer_{wafer}_Ablage_{current_datetime.strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
        waver_info_df.to_excel(output_file_xlsx, index=False)

        output_file_csv = f"{waver_typ}_Wafer_{wafer}_Ablage_{current_datetime.strftime('%Y-%m-%d_%H-%M-%S')}.csv"
        waver_info_df.to_csv(output_file_csv, index=False)
        print(f"Files saved as {output_file_xlsx} and {output_file_csv}")


def vision_data():
    vision_data = vision.get_vision_data()
        
    #[
        #(1.0, 2.0, -3.0), (1.1, 20.1, 3.1), (1.2, 29.2, 0.2), (10.3, 2.3, 3.3),
        #(10.4, 20.4, -0.4), (10.5, 29.5, 3.5), (21.6, 2.6, 0.6), (21.7, 20.7, -0.7),
        #(21.8, 29.8, 0.8), (31.9, 2.9, 0.9), (32.0, 13.0, 1.0), (32.1, 23.1, 1.1),
        #(32.2, 33.2, 1.2), (42.3, 3.3, 1.3), (42.4, 23.4, 1.4), (32.5, 43.5, 1.5),
        #(2.6, 3.6, 1.6), (2.7, 3.7, 1.7), (2.8, 3.8, 1.8), (2.9, 3.9, 1.9),
        #(3.0, 4.0, 3.0), (3.1, 4.1, 2.1), (3.2, 4.2, 2.2), (3.3, 4.3, 2.3),
        #(3.4, 4.4, 2.4), (3.5, 4.5, 2.5), (3.6, 4.6, 2.6), (3.7, 4.7, 2.7),
        #(3.8, 4.8, 3.8), (3.9, 4.9, 3.9), (4.0, 5.0, 3.0), (4.1, 5.1, 3.1),
        #(4.2, 5.2, 3.2), (4.3, 5.3, 3.3), (4.4, 5.4, 3.4), (4.5, 5.5, 3.5)
    #]  # 36 tuples of (x, y, w)
    robot = Robot(
        robot_model="Fanuc",
        host="127.0.0.1",
        port=18735,
        ee_DO_type="RDO",
        ee_DO_num=7,
    )
    robot.connect()
    robot.send_vision_data(vision_data)
    robot.disconnect()


def vision_data_test():
    
   
     # Transform the vision_data points
    vision_data, detectSquareImg = vision.get_vision_data()
    print(f'vision data is: {vision_data}')
    print(f'number of center: {len(vision_data)}')
    len_vision_data = len(vision_data)
    

    if len_vision_data == 36:
        label = customtkinter.CTkLabel(master=frame, text=f"Wafer data: {str(vision_data)}")
        label.pack(pady=12, padx=10)
    # Convert the image data to a format compatible with ImageTk
    # Convert to OpenCV image

    PIL_image = Image.fromarray(detectSquareImg, 'RGB')
    ctk_image = ImageTk.PhotoImage(PIL_image)   
    image_label = customtkinter.CTkLabel(root, image=ctk_image, text="")
    image_label.pack(padx=20, pady=20)

    return vision_data, detectSquareImg

def coordinate_system_func():
    matrix=coordinate_system.get_coordinateSystem()
    return matrix

customtkinter.set_appearance_mode("dark")

root = customtkinter.CTk()
root.geometry("700x800")

frame = customtkinter.CTkFrame(master=root)
frame.pack(pady=20, padx=60, fill="both", expand=True)

label = customtkinter.CTkLabel(master=frame, text="Importieren der Datei")
label.pack(pady=12, padx=10)

button = customtkinter.CTkButton(master=frame, text="Öffnen", command=file_browser)
button.pack(pady=12, padx=10)

# Add another button to execute vision_data
vision_button = customtkinter.CTkButton(master=frame, text="Vision Data", command=vision_data)
vision_button.pack(pady=12, padx=10)

# Add another button to execute vision_data test
visiontest_button = customtkinter.CTkButton(master=frame, text="Vision Data Test button", command=vision_data_test)
visiontest_button.pack(pady=12, padx=10)

# Add another button to execute coordinatesystem_data
coordinat_button = customtkinter.CTkButton(master=frame, text="Kalibration", command=coordinate_system_func)
coordinat_button.pack(pady=12, padx=10)


root.mainloop()
