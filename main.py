import customtkinter as tk
from database import connect_portfolio, Error, sql, PORTFOLIO_NOTE, PORTFOLIO_USER
import threading
from CTkMenuBar import *
from CTkMessagebox import CTkMessagebox
from PIL import Image
from pathlib import Path
from datetime import datetime
from operator import itemgetter
import CTkTable
import CTkXYFrame

tk.set_appearance_mode("dark")
tk.set_default_color_theme("dark-blue")
objects = []
ASSET_DIR = Path(__file__).resolve().parent
PHARMACY_NAMES = {"fikretacar": "Fikret Acar Pharmacy", "dogakent": "Doğakent", "simkent": "Simkent"}

class Message():
    def __init__(self,element,window):
        self.MessageIsSent = element[0]
        self.MessageText = tk.CTkLabel(master = window,text=element[2],fg_color="#0a3b17",corner_radius=17)
        if self.MessageIsSent:
            self.MessageText.pack(anchor='e',pady=3)
        else:
            self.MessageText.pack(anchor='w',pady=3)

class MessageBoxWindow():
    def __init__(self,client):
        
        self.wopened = 1
        self.client_connection = connect_portfolio(schema=client)
        self.Window = tk.CTkToplevel(window)
        self.Window.transient(window)
        self.Window.title("Messages — " + PHARMACY_NAMES.get(client, client))
        self.Window.protocol("WM_DELETE_WINDOW",self.closed)
        self.TitleFrame = tk.CTkFrame(master=self.Window)
        self.TitleFrame.pack()
        self.MessageTopLabel = tk.CTkLabel(master=self.TitleFrame,text=PHARMACY_NAMES.get(client, client),font=('Helvetica Neue',25))
        self.MessageTopLabel.pack(side='left')
        self.MessageRightLabel = tk.CTkLabel(master=self.TitleFrame,text ="  — conversation",font=('Helvetica Neue',19))
        self.MessageRightLabel.pack(side='left')
        self.Frame = tk.CTkScrollableFrame(master=self.Window,height=700)
        self.Frame.pack(fill = 'x')
        cursor = connection.cursor()
        cursor.execute(sql.SQL("SELECT * FROM {} WHERE ToFrom = %s ORDER BY messageDateTime, messageId").format(sql.Identifier(PORTFOLIO_USER, "messages")), (client,))
        self.Messages = cursor.fetchall()
        cursor.close()
        self.OldMessages = self.Messages
        for element in self.Messages:
            element = list(element)
            element[3] = int(element[3].strftime('%Y%m%d%H%M%S'))
        self.OldMessages = self.Messages        
        self.Messages = sorted(self.Messages,key = itemgetter(3))
        self.packIndex = 0
        self.MessageLabels = []
        for element in self.Messages:
            exec("self.Message" + str(self.packIndex) + " = Message(element,self.Frame)")
            self.MessageLabels.append("self.Message" + str(self.packIndex))
            self.packIndex += 1
        self.UpdateMessages(client,0)
        self.MessageFrame = tk.CTkFrame(master=self.Window)
        self.MessageFrame.pack(fill='x')
        self.MessageBox = tk.CTkEntry(master=self.MessageFrame)
        self.MessageBox.pack(side = 'left',fill = 'x')
        self.MessageSendButton = tk.CTkButton(master=self.MessageFrame,text="Send",command=lambda: self.SendMessage(client),width=28)
        self.MessageSendButton.pack(side='right')
        self.cursor = connection.cursor()
        self.clientCursor = self.client_connection.cursor()
        self.Window.after(150, self.BringToFront)

    def BringToFront(self):
        if self.wopened:
            self.Window.deiconify()
            self.Window.lift(window)
            self.MessageBox.focus_set()
         
    def SendMessage(self,client):
        if self.MessageBox.get() != "":
            # Pharmacy accounts use schemas in the same PostgreSQL database.
            # Store the two copies atomically; PostgreSQL allocates message IDs.
            with connection.transaction():
                self.cursor.execute(
                    sql.SQL("INSERT INTO {} (Sent, ToFrom, messageContent, messageDateTime) VALUES (%s, %s, %s, %s)").format(sql.Identifier(PORTFOLIO_USER, "messages")),
                    (True, client, self.MessageBox.get(), datetime.now()),
                )
                self.cursor.execute(
                    sql.SQL("INSERT INTO {} (Sent, ToFrom, messageContent, messageDateTime) VALUES (%s, %s, %s, %s)").format(sql.Identifier(client, "messages")),
                    (False, PORTFOLIO_USER, self.MessageBox.get(), datetime.now()),
                )
            self.MessageBox.delete(0,tk.END)
            print("Message sent")
            self.UpdateMessages(client,1)
        # Both message copies use the active portfolio account.


    def UpdateMessages(self,client,sent):
        if self.wopened:
            cursor = connection.cursor()
            cursor.execute(sql.SQL("SELECT * FROM {} WHERE ToFrom = %s ORDER BY messageDateTime, messageId").format(sql.Identifier(PORTFOLIO_USER, "messages")), (client,))
            self.NewMessages = cursor.fetchall()
            cursor.close()
            if not len(self.NewMessages) == len(self.OldMessages): 
                for element in self.NewMessages:
                    element = list(element)
                    element[3] = int(element[3].strftime('%Y%m%d%H%M%S'))
                self.Diffrence = len(self.NewMessages) - len(self.OldMessages)
                print(str(self.Diffrence))
                for i in range(self.Diffrence,0,-1):
                    self.NewMessages[-i]
                    exec("self.Message" + str(self.packIndex) + " = Message(self.NewMessages[-i],self.Frame)")
                    self.MessageLabels.append("self.Message" + str(self.packIndex))
                    self.packIndex += 1
                self.OldMessages = self.NewMessages
            print(self.NewMessages)
            if not sent:
                self.Window.after(10000,lambda: self.UpdateMessages(client,0))



    def closed(self):
        self.cursor.close()
        self.clientCursor.close()
        self.client_connection.close()
        self.wopened = 0
        self.Window.destroy()



#VARIABLES
numOfUndefinedCust = "0"
numOfCust = "0"
global firstTime
firstTime = True
def ForgetAll():
    for element in objects:
        try:
            element.pack_forget()
        except:
            pass
    '''try:
        exec("StockButton.pack_forget()")
        LoginToAccountLabel.pack_forget()
        LoginMasterUsername.pack_forget()
        LoginMasterPassword.pack_forget()
        LoginLowerUsername.pack_forget()
        LoginLowerPassword.pack_forget()
        LoginButton.pack_forget()
        exec("infoFrame.pack_forget()")
    except:
        pass'''

#START
window = tk.CTk()
window.geometry("480x350")
window.title("PharmAssist")
window.resizable(width=False,height=False)

x= 5
LoginToAccountLabel = tk.CTkLabel(master=window,text="Sign In",font=('TkDefaultFont',27))
LoginToAccountLabel.pack(pady = x+5)
objects.append(LoginToAccountLabel)
LoginMasterUsername = tk.CTkEntry(master=window,placeholder_text="Administrator Username",width=220)
LoginMasterUsername.pack(pady = x)
objects.append(LoginMasterUsername)
LoginMasterPassword = tk.CTkEntry(master=window,placeholder_text="Password",show="*",width=220)
LoginMasterPassword.pack(pady = x)
objects.append(LoginMasterPassword)
PortfolioNote = tk.CTkLabel(master=window, text=PORTFOLIO_NOTE, font=("TkDefaultFont", 11))
PortfolioNote.pack(padx=8, pady=(0, 5))
objects.append(PortfolioNote)
LoginLowerUsername = tk.CTkEntry(master=window,placeholder_text="Personal Username",width=220)
LoginLowerUsername.pack(pady = x)
objects.append(LoginLowerUsername)
LoginLowerPassword = tk.CTkEntry(master=window,placeholder_text="Password",show="*",width=220)
LoginLowerPassword.pack(pady = x)
objects.append(LoginLowerPassword)
def Login(*args):
    def StockScreen():
        ForgetAll()  
        StockTopFrame = tk.CTkFrame(master=window)
        StockTopFrame.pack()
        objects.append(StockTopFrame)
        MainScreenButton = tk.CTkButton(master=StockTopFrame,command=MainScreen,text="Back to Home")
        MainScreenButton.pack()
        objects.append(MainScreenButton)
        cursor.execute('SELECT * FROM fikretacar.MedList;')
        Stock = cursor.fetchall()
        for item in Stock:
            item = list(item)
            for value in item:
                value = str(value)
        StockFrame = CTkXYFrame.CTkXYFrame(master=window,height=500)
        StockFrame.pack(pady = 20,fill='both')
        objects.append(StockFrame)
        StockList = CTkTable.CTkTable(master=StockFrame,column=9,row=len(Stock),values=Stock,colors=["#272729","#14112b"],color_phase="vertical")
        StockList.pack()
        objects.append(StockList)

    def MainScreen(*args):
        if args:
            StockScreen()
            ForgetAll()
            window.geometry("1400x1000")
            window.resizable(width=True,height=True)
            infoFrame = tk.CTkFrame(master=window,bg_color="gray")
            infoFrame.pack(side="right",fill="y")
            allignerLabel = tk.CTkLabel(master=infoFrame,text="                                  ",font=('TkDefaultFont',27),text_color="gray")
            allignerLabel.pack()
            storePhoto = Image.open(ASSET_DIR / "fikret_acar.jpeg")
            storeImage = tk.CTkImage(light_image=storePhoto, dark_image=storePhoto, size=(200,200))
            storeImageLabel = tk.CTkLabel(master=infoFrame, image=storeImage, text="")
            storeImageLabel.image = storeImage
            storeImageLabel.pack(pady=20)
            pharmacyNameLabel = tk.CTkLabel(master=infoFrame, text=PHARMACY_NAMES[PORTFOLIO_USER], font=('TkDefaultFont',20))
            pharmacyNameLabel.pack(pady=5)
            lineLabel = tk.CTkLabel(master=infoFrame,text="______________________",font=('TkDefaultFont',20),bg_color="transparent")
            lineLabel.pack(pady=15)
            #Account information
            customerInfoLabel1 = tk.CTkLabel(master=infoFrame,text= "Signed in as " + loggedInInformation[0],font=('TkDefaultFont',20),bg_color="transparent")
            customerInfoLabel1.pack(pady=5)
            customerInfoLabel2 = tk.CTkLabel(master=infoFrame,text= "Username: " + PORTFOLIO_USER + "\n" + "Work Score: " + str(loggedInInformation[2]),font=('TkDefaultFont',18),bg_color="transparent")
            customerInfoLabel2.pack(pady=5,padx=5)
            customerCountFrame = tk.CTkFrame(master=infoFrame,bg_color="black")
            customerCountFrame.pack(fill="x",pady=5)
            '''customerImage = tk.CTkImage(light_image=Image.open(ASSET_DIR / "hasta.png"),dark_image=Image.open(ASSET_DIR / "hasta.png"),size=(70,70))
            customerImage = tk.CTkLabel(master=customerCountFrame,image=customerImage,text="")
            customerImage.pack(side="left")'''
            customerLabel = tk.CTkLabel(master=customerCountFrame,text="Patients currently in the pharmacy: " + numOfCust + "\n" + "Unidentified patients: " + numOfUndefinedCust)
            customerLabel.pack(padx=10,pady=20)
            #Messages
            MessageFrame = tk.CTkScrollableFrame(master=infoFrame,bg_color="black",height=220)
            MessageFrame.pack(fill="x",pady=5)
            cursor.execute("SELECT username FROM pharmacy.Stores WHERE username <> %s ORDER BY username", (PORTFOLIO_USER,))
            for (client,) in cursor.fetchall():
                MessageTestButton = tk.CTkButton(
                    master=MessageFrame,
                    command=lambda client=client: MessageBoxWindow(client),
                    text=PHARMACY_NAMES.get(client, client),
                )
                MessageTestButton.pack(pady=4)
        else:
            ForgetAll()
        StockButton = tk.CTkButton(master=window,text="Stock",command=StockScreen)
        StockButton.pack()
        objects.append(StockButton)
    try:
        global connection
        connection = connect_portfolio()
        temp = connection.info.server_version
        print("Connected to PostgreSQL Server version ", temp)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Personel WHERE personelUsername = %s", ("evrenacar",))
        loggedInInformation = cursor.fetchone()
        if loggedInInformation is None:
            raise Error("The portfolio staff record is missing from the configured database.")
        print("Connection established")
        MainScreen(args)
    except Error as e:
        CTkMessagebox(message="Unable to open the portfolio database. Check postgres-connection.json and that PostgreSQL is reachable.",icon="cancel", option_1="OK",title="Database Error")
        print("Error while connecting to PostgreSQL", e)
LoginButton = tk.CTkButton(master=window,text="Sign In",width=100,command=lambda: Login(True))
LoginButton.pack(pady = x + 3)
objects.append(LoginButton)
#END
window.mainloop()
try:
    try:
        exec("cursor.close()")
    except NameError:
        print("Cursor Was Already Closed/Didnt Open")
    exec("connection.close()")
    print("PostgreSQL connection is closed")
except NameError:
    print("Closed Without Making A Connection")