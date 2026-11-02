import customtkinter as tk
from database import connect_portfolio, Error, PORTFOLIO_NOTE, PORTFOLIO_USER
import threading
from CTkMenuBar import *
from CTkMessagebox import CTkMessagebox
from PIL import Image
from pathlib import Path
from datetime import datetime

tk.set_appearance_mode("dark")
tk.set_default_color_theme("dark-blue")

ASSET_DIR = Path(__file__).resolve().parent
hasta_sayisi = "0"
taninmamis_sayi = "0"


def clock():
    tarih.configure(text=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    tarih.pack()
    tarih.after(1000,clock)

def login():
    global connection, cursor
    connection = None
    try:
        connection = connect_portfolio(schema='pharmacy')
        if connection is not None and not connection.closed:
            db_Info = connection.info.server_version
            print("Connected to PostgreSQL Server version ", db_Info)
            cursor = connection.cursor()
            cursor.execute("SELECT current_database();")
            record = cursor.fetchone()
            print("You're connected to database: ", record)

    except Error as e:
        CTkMessagebox(message="Unable to open the portfolio database. Check postgres-connection.json and that PostgreSQL is reachable.",
                  icon="cancel", option_1="OK",title="Database Error")
        print("Error while connecting to PostgreSQL", e)
    finally:
        if connection is not None and not connection.closed:
            window.geometry("1200x1200")
            kulladi.place_forget()
            sifre.place_forget()
            giris.place_forget()
            yazi1.place_forget()
            portfolio_note.place_forget()
            menu = CTkMenuBar(window)
            button_1 = menu.add_cascade("File")
            dropdown1 = CustomDropdownMenu(widget=button_1)
            dropdown1.add_option(option="Open", command=lambda: print("Open"))
            dropdown1.add_option(option="Save")
            stok = tk.CTkButton(master=window,text="Stock",height=140).place(relwidth=0.18,relx=0.2,rely=0.5,anchor="center")
            satis = tk.CTkButton(master= window,text="Retail Sales",height=140).place(relwidth=0.18,relx=0.4,rely=0.5,anchor="center")
            havuz = tk.CTkButton(master= window,text="Queue",height=140).place(relwidth=0.18,relx=0.6,rely=0.5,anchor="center")
            mesajlar = tk.CTkButton(master= window,text="Messages",height=140).place(relwidth=0.18,relx=0.8,rely=0.5,anchor="center")
            frame = tk.CTkFrame(master=window,bg_color="gray",width=1000)#.place(relwidth=0.2,relheight=2,relx=1,rely=0,anchor="e")
            frame.pack(side="right",fill="y")
            sql = "SELECT * FROM Stores WHERE username = %s"
            cursor.execute(sql, (PORTFOLIO_USER,))
            result = cursor.fetchone()
            
            kullanicibilgileri0 = tk.CTkLabel(master=frame,text="                                  ",font=('TkDefaultFont',27),text_color="gray")
            kullanicibilgileri0.pack()
            my_image = tk.CTkImage(light_image=Image.open(ASSET_DIR / "fikret_acar.jpeg"),
                                  dark_image=Image.open(ASSET_DIR / "fikret_acar.jpeg"),
                                  size=(200,200))

            image_label = tk.CTkLabel(master=frame, image=my_image, text="")
            image_label.pack(pady=20)
            kullanicibilgileri3 = tk.CTkLabel(master=frame,text="______________________",font=('TkDefaultFont',20),bg_color="transparent")
            kullanicibilgileri3.pack(pady=25)
            kullanicibilgileri3 = tk.CTkLabel(master=frame,text= result[2] + " — signed in",font=('TkDefaultFont',20),bg_color="transparent")
            kullanicibilgileri3.pack(pady=5)
            kullanicibilgileri1 = tk.CTkLabel(master=frame,text= "Username: " + result[0] + "\n" + "Head Pharmacist: " + result[1],font=('TkDefaultFont',18),bg_color="transparent")
            kullanicibilgileri1.pack(pady=5,padx=5)
            frame2 = tk.CTkFrame(master=frame,bg_color="black")
            frame2.pack(fill="x",pady=20)
            hasta_image = tk.CTkImage(light_image=Image.open(ASSET_DIR / "hasta.png"),
                                      dark_image=Image.open(ASSET_DIR / "hasta.png"),
                                      size=(70,70)
                                      )
            hasta_foto = tk.CTkLabel(master=frame2,image=hasta_image,text="")
            hasta_foto.pack(side="left")
            yazi2 = tk.CTkLabel(master=frame2,text="Patients currently in the pharmacy: " + hasta_sayisi + "\n" + "Unidentified patients: " + taninmamis_sayi)
            yazi2.pack(padx=10,pady=20)
            frame3 = tk.CTkScrollableFrame(master=frame,bg_color="black",height=400)
            frame3.pack(fill="x",pady=5)
            button1 = tk.CTkButton(master=frame3,text="Test1").pack(pady=50)
            button2 = tk.CTkButton(master=frame3,text="Test2").pack(pady=50)
            button3 = tk.CTkButton(master=frame3,text="Test3").pack(pady=50)
            button4 = tk.CTkButton(master=frame3,text="Test4").pack(pady=50)
            button5 = tk.CTkButton(master=frame3,text="Test5").pack(pady=50)
            button6 = tk.CTkButton(master=frame3,text="Test6").pack(pady=50)

            sql = "SELECT * FROM Messages WHERE messageSender = %s"
            cursor.execute(sql, (PORTFOLIO_USER,))
            sentMessages = cursor.fetchall()
            sql = "SELECT * FROM Messages WHERE messageReciever = %s"
            cursor.execute(sql, (PORTFOLIO_USER,))
            recievedMessages = cursor.fetchall()
            print(recievedMessages)
            print(sentMessages)
            Messaging = []
            MessagerTime = []
            for item in recievedMessages:
                if Messaging.count(item[0]) == 0:
                    Messaging.append(item[0])# + "@" + item[1].strftime("%m/%d/%Y, %H:%M:%S") + "@"+ item[2])
                    MessagerTime.append(item[1].strftime("%Y%m%d%H%M%S"))
                    print(item[0])
                if Messaging.count(item[4]) == 0:
                    Messaging.append(item[4])# + "@" + item[1].strftime("%m/%d/%Y, %H:%M:%S") + "@"+item[2])  
                    MessagerTime.append(item[1].strftime("%Y%m%d%H%M%S"))
                    print(item[4])
            for item in sentMessages:
                if Messaging.count(item[0]) == 0:
                    Messaging.append(item[0])# + "@" + item[1].strftime("%m/%d/%Y, %H:%M:%S") + "@"+ item[2])
                    MessagerTime.append(item[1].strftime("%Y%m%d%H%M%S"))
                    print(item[0])
                if Messaging.count(item[4]) == 0:
                    Messaging.append(item[4])# + "@" + item[1].strftime("%m/%d/%Y, %H:%M:%S") + "@"+ item[2])        
                    MessagerTime.append(item[1].strftime("%Y%m%d%H%M%S"))
                    print(item[4])
            print(Messaging) 
            print(MessagerTime)   
            MessageList = dict(zip(Messaging,MessagerTime))
            print(MessageList)
            MessageList = dict(sorted(MessageList.items(), key=lambda item: item[1]))
            print(MessageList)
            MessageList.pop(PORTFOLIO_USER, None)
            print(MessageList)
            print("------------")
            for item in MessageList:
                conversation = [
                    (message[2], message[1])
                    for message in recievedMessages
                    if message[0] == item
                ]
                print(item, conversation)
                for i in range(len(conversation)):
                    # Placeholder for displaying the remaining conversations.
                    pass


            global tarih
            tarih = tk.CTkLabel(master=frame,text="")
            tarih.pack(pady=0)
            clock()

window = tk.CTk()
window.geometry("480x280")
window.title("PharmAssist")
window.resizable(width=True,height=False)

#Sign-in screen
yazi1 = tk.CTkLabel(master=window,text="Sign In",font=('TkDefaultFont',27))
yazi1.place(relx=0.5,rely=0.12,anchor="center")
kulladi = tk.CTkEntry(master=window,placeholder_text="Username")
kulladi.place(relx=0.5,rely=0.32,anchor="center")
sifre = tk.CTkEntry(master=window,placeholder_text="Password",show="*")
sifre.place(relx=0.5,rely=0.48,anchor="center")
portfolio_note = tk.CTkLabel(master=window, text=PORTFOLIO_NOTE, font=("TkDefaultFont", 11))
portfolio_note.place(relx=0.5,rely=0.66,anchor="center")

giris = tk.CTkButton(master=window,command=login,text="Sign In")
giris.place(relx=0.5,rely=0.84,anchor="center")

window.mainloop()
window.after

if "connection" in globals() and connection is not None and not connection.closed:
    cursor.close()
    connection.close()
print("PostgreSQL connection is closed")