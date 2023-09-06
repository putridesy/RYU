import pyrebase
import board
import adafruit_dht
import RPi.GPIO as GPIO
import time
from mfrc522 import SimpleMFRC522
from signal import signal, SIGTERM, SIGHUP, pause
from rpi_lcd import LCD

#setting API firebase
config = {
  "apiKey": "AIzaSyBIxLGjEx5RJyiYgcCsWrj2leXziEUJEHQ",
  "authDomain": "cobarelay-b71bf.firebaseapp.com",
  "databaseURL": "https://cobarelay-b71bf-default-rtdb.firebaseio.com",
  "projectId": "cobarelay-b71bf",
  "storageBucket": "cobarelay-b71bf.appspot.com",
  "messagingSenderId": "318516627224",
  "appId": "1:318516627224:web:4e92bb0d831c8e25cac06d",
  "measurementId": "G-0WMLKJSNSH"
};

firebase = pyrebase.initialize_app(config)
storage = firebase.storage()
database = firebase.database()

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

reader=SimpleMFRC522()
dhtDevice = adafruit_dht.DHT11(board.D18, use_pulseio=False)
lcd = LCD()
def safe_exit(signum, frame):
    exit(1)
    
GPIO_L1=24
GPIO_L2=12
GPIO_L3=16
GPIO_SC1=20
GPIO_SC2=21
GPIO_drlock=27
GPIO_drsw=17
GPIO_flame=22
GPIO_motion=23
GPIO_alarm=26
GPIO_BTN1=5
GPIO_BTN2=6
GPIO_BTN3=13
  

GPIO.setup(GPIO_L1, GPIO.OUT)
GPIO.setup(GPIO_L2, GPIO.OUT)
GPIO.setup(GPIO_L3, GPIO.OUT)
GPIO.setup(GPIO_SC1, GPIO.OUT)
GPIO.setup(GPIO_SC2, GPIO.OUT)
GPIO.setup(GPIO_alarm, GPIO.OUT)
GPIO.setup(GPIO_drlock, GPIO.OUT)
GPIO.setup(GPIO_drsw, GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(GPIO_flame, GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(GPIO_motion, GPIO.IN)
GPIO.setup(GPIO_BTN1, GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(GPIO_BTN2, GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(GPIO_BTN3, GPIO.IN,pull_up_down=GPIO.PUD_UP)


GPIO.output(GPIO_L1, 1)
GPIO.output(GPIO_L2, 1)
GPIO.output(GPIO_L3, 1)
GPIO.output(GPIO_SC1, 1)
GPIO.output(GPIO_SC2, 1)
GPIO.output(GPIO_alarm, 1)
GPIO.output(GPIO_drlock, 0)

lamp1=0
lamp2=0
lamp3=0
tb_lamp=0
kipas=0
tb_kipas=0
alarm=0
doorsw=0
nama=""
senflame=0
masuk=0
suhu=0

sw1=0
sw2=0
sw3=0

ln1="Tempelkan Kartu"
ln2="   Disini !"

#fungsi baca_tombol
def baca_tombol():
    global sw1,sw2,tb_kipas,alarm,tb_lamp
    #-----------Tombol 1-------------------
    if GPIO.input(GPIO_BTN1)==0 and sw1==0:
        sw1=1
    if GPIO.input(GPIO_BTN1)!=0 and sw1==1:
        if tb_lamp==0:
            tb_lamp=1
            lampu(1)
            database.child("SMC").update({"lamp1": 1})
            database.child("SMC").update({"lamp2": 1})
            database.child("SMC").update({"lamp3": 1})
                     
        elif tb_lamp==1:
            tb_lamp=0
            lampu(0)
            database.child("SMC").update({"lamp1": 0})
            database.child("SMC").update({"lamp2": 0})
            database.child("SMC").update({"lamp3": 0})
        sw1=0
    #-----------Tombol 2--------------
    if GPIO.input(GPIO_BTN2)==0 and sw2==0:
        sw2=1
    if GPIO.input(GPIO_BTN2)!=0 and sw2==1:
        if tb_kipas==0:
            tb_kipas=1
            kipase(1)
            database.child("SMC").update({"kipas": 1})
           
        elif tb_kipas==1:
            tb_kipas=0
            kipase(0)
            database.child("SMC").update({"kipas": 0})
           
        sw2=0
    #--------------tombol 3---------------
    if GPIO.input(GPIO_BTN3)==0 and alarm==1:
        GPIO.output(GPIO_SC2, 1)
        alarm=0
        database.child("SMC").update({"alarm": alarm})
 
#fungsi nyalakan lampu
def lampu(x):
    if x==1:
        GPIO.output(GPIO_L1, 0)
        GPIO.output(GPIO_L2, 0)
        GPIO.output(GPIO_L3, 0)
    else:
        GPIO.output(GPIO_L1, 1)
        GPIO.output(GPIO_L2, 1)
        GPIO.output(GPIO_L3, 1)
        
#fungsi nyala kipas
def kipase(x):
    if x==1:
        GPIO.output(GPIO_SC1, 0)
    else:
        GPIO.output(GPIO_SC1, 1)
        
#fungsi baca RFID 
def baca_rfid():
    global nama,ln1,ln2,masuk,id
    id=reader.read_id()
    if (id==289103918677 and masuk==0):
        nama="Pak_Danu"
        lcd.clear()
        ln1="Selamat Datang"
        ln2="   "+nama
        database.child("SMC").update({"nama": nama})
        masuk=1
    elif (id==289103918677 and masuk==1):
        masuk=0
        nama=""
        lcd.clear()
        ln1="Tempelkan Kartu"
        ln2="   Disini !"
        GPIO.output(GPIO_drlock, 1)
        database.child("SMC").update({"nama": ""})
        #time.sleep(3)
        
    elif (id==621510271202 and masuk==0):
        nama="Pak_Arif"
        lcd.clear()
        ln1="Selamat Datang"
        ln2="   "+nama
        database.child("SMC").update({"nama": nama})
        masuk=1
    elif (id==621510271202 and masuk==1):
        masuk=0
        nama=""
        lcd.clear()
        ln1="Tempelkan Kartu"
        ln2="   Disini !"
        database.child("SMC").update({"nama": ""})
        GPIO.output(GPIO_drlock, 1)
        #time.sleep(3)
        
# fungsi baca sensor
def baca_sensor():
    global doorsw,senflame,alarm
    if GPIO.input(GPIO_drsw) !=0:
        doorsw=1
        database.child("SMC").update({"doorsw": 1})
    else:
        doorsw=0
        database.child("SMC").update({"doorsw": 0})
        
    if GPIO.input(GPIO_flame)==0:
        alarm=1
        senflame=1
        GPIO.output(GPIO_SC2, 0)
        database.child("SMC").update({"senflame": senflame})
        database.child("SMC").update({"alarm": alarm})
    else:
        senflame=0
        database.child("SMC").update({"senflame": senflame})

def aksi():
    global lamp1,lamp2,lamp3,kipas,tb_lamp
    if lamp1|lamp2|lamp3:
        tb_lamp=1
    else:
        tb_lamp=0
        
    if  lamp1==1:
        GPIO.output(GPIO_L1, 0)
    else :
        GPIO.output(GPIO_L1, 1)
    
    if  lamp2==1:
        GPIO.output(GPIO_L2, 0)
    else :
        GPIO.output(GPIO_L2, 1)
    
    if  lamp3==1:
        GPIO.output(GPIO_L3, 0)
    else :
        GPIO.output(GPIO_L3, 1)
    
    
    if kipas==1:
        tb_kipas=1
        kipase(1)
    else :
        tb_kipas=0
        kipase(0)
            
  
database.child("SMC")
data = {"Temp":suhu,
            "lamp1":lamp1 ,
            "lamp2":lamp2 ,
            "lamp3":lamp3 ,
            "kipas":kipas ,
            "alarm":alarm ,
            "doorsw":doorsw ,
            "nama": nama,
            "senflame":senflame }
database.set(data)

while True:
    
    signal(SIGTERM, safe_exit)
    signal(SIGHUP, safe_exit)
    lcd.text(ln1, 1)
    lcd.text(ln2, 2)
    
    
    baca_tombol()
    
    #-------baca data dari firebase------------------
    dtlamp1=database.child("SMC").child("lamp1").get()
    dtlamp2=database.child("SMC").child("lamp2").get()
    dtlamp3=database.child("SMC").child("lamp3").get()
    dtkipas=database.child("SMC").child("kipas").get()
    dtalarm=database.child("SMC").child("alarm").get()
    
    lamp1=int (dtlamp1.val())
    lamp2=int (dtlamp2.val())
    lamp3=int (dtlamp3.val())
    kipas=int (dtkipas.val())
   
    baca_rfid()
    baca_sensor()
    aksi()
    
    try:
        suhu=dhtDevice.temperature
        #print(suhu)
        time.sleep(0.2)
        database.child("SMC").update({"Temp": suhu})
    except RuntimeError as error:
        # Errors happen fairly often, DHT's are hard to read, just keep going
        #print(error.args[0])
        #time.sleep(2.0)
        continue
