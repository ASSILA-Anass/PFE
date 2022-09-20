import csv
import json
import smtplib
import sqlite3
import datetime
import ssl
import geopy.distance 
from django.db import models
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import urllib.request

validity_dic={"validity":"pas d'informations correspondantes dans la base de données"}
APIkey="mHcaHwUF3uxP9mtu8CP37qD7AYhodI0M"
GPSkey="zBivviezIVzbGIbiBIbi4uizIGBZyhAO"
# Create your models here.
'''***********************************$ les classes pour base de données $***********************************'''

class utilisateurs(models.Model):
    id_user=models.AutoField(primary_key=True)
    username=models.CharField(max_length=50)
    password=models.CharField(max_length=50)
    entreprise=models.CharField(max_length=50)

class vehicules(models.Model):
    id_vehicule=models.AutoField(primary_key=True)
    matricule=models.CharField(max_length=50)
    classe=models.CharField(max_length=50)

class chauffeurs(models.Model):
    id_chauffeur=models.AutoField(primary_key=True)
    nom=models.CharField(max_length=50)
    prenom=models.CharField(max_length=50)

class positions(models.Model):
    id_position=models.AutoField(primary_key=True)
    latitude=models.CharField(max_length=50)
    longitude=models.CharField(max_length=50)
    id_chauffeur=models.ForeignKey(chauffeurs, on_delete=models.CASCADE)
    id_vehicule=models.ForeignKey(vehicules, on_delete=models.CASCADE)
    date_heure=models.DateTimeField()

'''***********************************$ La classe pour dessiner la carte $***********************************'''

class GPSVis(object):
    """
        Class for GPS data visualization using pre-downloaded OSM map in image format.
    """
    def __init__(self, data_path, map_path, points):

        self.data_path = data_path    
        self.points = points
        self.map_path = map_path

        self.result_image = Image
        self.x_ticks = []
        self.y_ticks = []

    def plot_map(self, output='save', save_as='SSF/static/img/resultMap.png'):

        # Mise en forme finale de l'image aprés traitement et ajout du trajectoire

        self.get_ticks()
        fig, axis1 = plt.subplots(figsize=(10, 10))
        axis1.imshow(self.result_image)
        axis1.set_xlabel('Longitude')
        axis1.set_ylabel('Latitude')
        axis1.set_xticklabels(self.x_ticks)
        axis1.set_yticklabels(self.y_ticks)
        axis1.grid()
        if output == 'save':
            plt.savefig(save_as)
        else:
            plt.show()

    def create_image(self, color, width=2):
        
                 # lire les données sauvgardées des locations du gps_transmitter
                 # trouver les pixels correspondants du chaque cords
                 # dessiner le chemin
        
        data = pd.read_csv(self.data_path, names=['LATITUDE', 'LONGITUDE'], sep=',')

        self.result_image = Image.open(self.map_path, 'r')
        img_points = []
        gps_data = tuple(zip(data['LATITUDE'].values, data['LONGITUDE'].values))
        for d in gps_data:
            x1, y1 = self.scale_to_img(d, (self.result_image.size[0], self.result_image.size[1]))
            img_points.append((x1, y1))
        draw = ImageDraw.Draw(self.result_image)
        draw.line(img_points, fill=color, width=width)

    def scale_to_img(self, lat_lon, h_w):

                 #on utilise les cordonnées réels d'image en combinaison avec ces dimensions
                 #et les cordonnées réels d'un point pour trouver sa position dans l'image
                 #on retourne la position du point dans l'image

        # https://gamedev.stackexchange.com/questions/33441/how-to-convert-a-number-from-one-min-max-set-to-another-min-max-set/33445
        old = (self.points[2], self.points[0])
        new = (0, h_w[1])
        y = ((lat_lon[0] - old[0]) * (new[1] - new[0]) / (old[1] - old[0])) + new[0]
        old = (self.points[1], self.points[3])
        new = (0, h_w[0])
        x = ((lat_lon[1] - old[0]) * (new[1] - new[0]) / (old[1] - old[0])) + new[0]
        # y must be reversed because the orientation of the image in the matplotlib.
        # image - (0, 0) in upper left corner; coordinate system - (0, 0) in lower left corner
        return int(x), h_w[1] - int(y)

    def get_ticks(self):
                 #get 5 numbers between min and max X cords of the map evenly spaced and round it to the 4 digits
                 #get 6 numbers between min and max Y cords of the map evenly spaced and round it to the 4 digits
                 #store each in the corresponding list
        ima = Image.open(self.map_path, 'r')

        self.x_ticks = map(
            lambda x: round(x, 4),
            np.linspace(self.points[1], self.points[3], num=(ima.size[0]//10)+1))
        y_ticks = map(
            lambda x: round(x, 4),
            np.linspace(self.points[2], self.points[0], num=(ima.size[1]//10)+1))



        # Ticks must be reversed because the orientation of the image in the matplotlib.
        # image - (0, 0) in upper left corner; coordinate system - (0, 0) in lower left corner
        self.y_ticks = sorted(y_ticks, reverse=True)

'''***********************************$ les fonction pour enregistrer/supprimer du BD $***********************************'''

def saveposition(latitude,longitude,id_chauffeur,id_vehicule,Skey):
    id_ch=int(id_chauffeur)
    id_vic=int(id_vehicule)
    chauffeur=chauffeurs(id_ch)
    vehicule=vehicules(id_vic)
    if Skey==GPSkey:
        pos= positions()
        pos.latitude=latitude
        pos.longitude=longitude
        pos.id_chauffeur=chauffeur
        pos.id_vehicule=vehicule
        pos.date_heure=datetime.datetime.now()
        pos.save()

def databasefiller(latitude,longitude,id_chauffeur,id_vehicule,Skey,date_heure):
    id_ch=int(id_chauffeur)
    id_vic=int(id_vehicule)
    chauffeur=chauffeurs(id_ch)
    vehicule=vehicules(id_vic)
    print("blabla")
    if Skey==GPSkey:
        pos= positions()
        pos.latitude=latitude
        pos.longitude=longitude
        pos.id_chauffeur=chauffeur
        pos.id_vehicule=vehicule
        pos.date_heure=datetime.datetime.strptime(date_heure, '%Y-%m-%d %H:%M:%S.%f')
        pos.save()

def savechauffeur(nom,prenom):
    ch=chauffeurs()
    ch.nom=nom
    ch.prenom=prenom
    ch.save()

def saveuser(username,password,entreprise):
    user=utilisateurs()
    user.username=username
    user.password=password
    user.entreprise=entreprise
    user.save()

def savevehicule(matricule,classe):
    vehicule=vehicules()
    vehicule.matricule=matricule
    vehicule.classe=classe
    vehicule.save()

def cleartable(id_line1,id_line2):
    for i in range(id_line1,id_line2):
        pos=positions(i)
        pos.delete()
'''***********************************$ Autres fonctions $***********************************'''

# def fetch_nom_entreprise():
#     with open("TEMP/data_file.json", "r") as read_file:
#         data = json.load(read_file)
#     return data

def checklogin(username,password):                                      #Vérifier login
    con = sqlite3.connect('db.sqlite3')                                               #connection avec db
    cur= con.cursor()
    cur.execute(''' SELECT * FROM BE_utilisateurs
    WHERE username='''+"\'" +username+"\'" + ''' AND password='''+"\'"+password+"\'") #créer une requette pour selectionner l'utilisateur
    rows=cur.fetchall()                                                               #executer la requette
    if rows==[]:                                                                      #verifier si le login est faux
        return False
    else:
        entreprise=rows[0][3]                                                         #selectionner le nom de l'entreprise
        with open("TEMP/data_file.json", "w") as write_file:
            json.dump({"nom_entreprise":entreprise}, write_file)
        return                                                              #retourner le nom de l'entreprise si le login est un succes

def main_fetch(id_vehicule,date_heure_A,date_heure_B):                  #main fonction for the mainpage
    if id_vehicule=='':
        copymap('first_img.png')
    elif date_heure_A=='':
        return fetch_data_A(id_vehicule)
    elif date_heure_B=='':
        return fetch_data_B(id_vehicule,date_heure_A)
    else:
        return fetch_data_C(id_vehicule,date_heure_A,date_heure_B)

''' 
We have three functionalities:
1--fetch_data_A(id_vehicule)-upon entering only vehicule id return latest position on map
2--fetch_data_B(id_vehicule,date_heure_A,date_heure_B)-upon entering  id_vehicule and date_heure_A return position of vehicule at the time
3--fetch_data_C(id_vehicule,date_heure_A,date_heure_B)-upon entering all parameters return a map with a track that the vehicule took between the two dates
'''

def fetch_data_A(id_vehicule):
    con = sqlite3.connect('db.sqlite3')                                             
    cur= con.cursor()
    cur.execute('''select * from BE_positions
    where id_vehicule_id='''+"\'" +id_vehicule+"\'" + ''' order by date_heure desc limit 1''')
    rows=cur.fetchall()
    if rows==[]:
        return validity_dic
    row=rows[0]
    latitude=float(row[1])
    longitude=float(row[2])
    makemap_one_point(latitude,longitude)
    nom_chauffeur=getchauffeur(row[4])
    l_vic=getvehicule(id_vehicule)
    dic ={
        "ch":'Chauffeur(s):',
        "mat":'Matricule:',
        "cl":'Classe:',
        "vm":'',
        "name" : '',
        "matricule" :' ',
        "classe":' ',
        "vitesse_moyenne":''
    }
    dic["matricule"]=l_vic[0]
    dic["classe"]=l_vic[1]
    dic["name"]=nom_chauffeur
    copymap()
    return dic

def fetch_data_B(id_vehicule,date_heure_A):
    con = sqlite3.connect('db.sqlite3')
    cur=con.cursor()    
    date=convert_time(date_heure_A)
    cur.execute(''' select * from BE_positions
    where id_vehicule_id='''+"\'" +id_vehicule+"\'" +''' AND date_heure<'''+"\'"+date+"\'" + ''' order by date_heure desc limit 1 ''')
    rows=cur.fetchall()
    if rows==[]:
        return validity_dic
    row=rows[0]
    latitude=float(row[1])
    longitude=float(row[2])
    makemap_one_point(latitude,longitude)
    nom_chauffeur=getchauffeur(row[4])
    l_vic=getvehicule(id_vehicule)
    dic ={
        "ch":'Chauffeur(s):',
        "mat":'Matricule:',
        "cl":'Classe:',
        "vm":'',
        "name" : '',
        "matricule" :' ',
        "classe":' ',
        "vitesse_moyenne":''
    }
    dic["matricule"]=l_vic[0]
    dic["classe"]=l_vic[1]
    dic["name"]=nom_chauffeur
    copymap()
    return dic

def fetch_data_C(id_vehicule,date_heure_A,date_heure_B):                                
    con = sqlite3.connect('db.sqlite3')                                             
    cur= con.cursor()
    date_debut=convert_time(date_heure_A)
    date_fin=convert_time(date_heure_B)
    cur.execute(''' select * from BE_positions
    where id_vehicule_id='''+"\'" +id_vehicule+"\'" + ''' AND date_heure>'''+"\'"+date_debut+"\'" + ''' AND date_heure<'''+"\'"+date_fin+"\'")
    rows=cur.fetchall()
    if rows==[]:
        return validity_dic
    dictionnaire_donné=fill_csvs(rows)
    l_vic=getvehicule(id_vehicule)
    dictionnaire_donné["matricule"]=l_vic[0]
    dictionnaire_donné["classe"]=l_vic[1]
    dictionnaire_donné["vitesse_moyenne"]=str(makemap())+" Km/h"
    copymap()
    return dictionnaire_donné

def fill_csvs(rows):                                                    #input:positions table ***** output:create two csv files on containing cords and the other containing names et retourne un dictionnaires des noms
    liste_id_chauffeurs=[]
    list_chauffeurs=[]
    cords_collector=open('TEMP/cordscollector.csv','w',newline='')
    # names_collector=open('TEMP/namescollector.csv','w')
    cords_writer=csv.writer(cords_collector)
    for row in rows:
        lat=float(row[1])
        long=float(row[2])
        cords=[lat,long]
        cords_writer.writerow(cords)
        if row[4] not in liste_id_chauffeurs:
            liste_id_chauffeurs.append(row[4])
            # names_collector.write(getchauffeur(row[4]))
            list_chauffeurs.append(getchauffeur(row[4]))
    cords_collector.close()
    # names_collector.close()
    dic ={
        "ch":'Chauffeur(s):',
        "mat":'Matricule:',
        "cl":'Classe:',
        "vm":'Vitesse moyenne:',
        "name" : '',
        "matricule" :' ',
        "classe":' ',
        "vitesse_moyenne":''
    }
    for l in list_chauffeurs:
        dic["name"]= l +", "+dic["name"]
    return  dic

def getchauffeur(id):                                                   #input:id_chauffeur **** output: nom complet chauffeur
    id_chauffeur=int(id)
    chauffeur=chauffeurs.objects.get(id_chauffeur=id_chauffeur)
    nom_complet_chauffeur= chauffeur.nom +" "+ chauffeur.prenom
    return nom_complet_chauffeur

def getvehicule(id):
    id_vehicule=int(id)
    vehicule=vehicules.objects.get(id_vehicule=id_vehicule)
    return [vehicule.matricule,vehicule.classe]

def convert_time(date):                                                 #convertir date du datetime-local à datetime  $$--outsourced code--$$
    date_in = date
    date_processing = date_in.replace('T', '-').replace(':', '-').split('-')
    date_processing = [int(v) for v in date_processing]
    date_out = datetime.datetime(*date_processing)
    output=str(date_out)
    return output

def makemap():                                                          #input:csv file containing cords *** output:drawn image of trajectory
    index=0
    distance=0
    time=0
    cord1=(0,0)
    cord2=(0,0)
    map_borders=[-90.0,180.0,90.0,-180.0]
    zdata=[360, 180.0, 90.0, 45.0, 22.5, 11.25, 5.625, 2.813, 1.406, 0.703, 0.352, 0.176, 0.088, 0.044, 0.022, 0.011, 0.005, 0.003,  0.001, 0.001 , 0.0005 , 0.00025]
    with open('TEMP/cordscollector.csv', 'r') as input_file:
        reader = csv.reader(input_file)
        for row in reader:
            if  float(row[0])>map_borders[0]:
                map_borders[0]=float(row[0])
            if float(row[0])<map_borders[2]:
                map_borders[2]=float(row[0])
            if float(row[1])<map_borders[1]:
                map_borders[1]=float(row[1])
            if float(row[1])>map_borders[3]:
                map_borders[3]=float(row[1])
            if index==0 :
                cord1=(row[0],row[1])
                index=1
            else:
                cord2=(row[0],row[1])
                distance=distance+geopy.distance.geodesic(cord1,cord2).m
                time=time+1
                cord1=cord2
    msspeed=(distance/time)*3.6
    Latcenter=(map_borders[0]+map_borders[2])/2                 #determin center cords
    longcenter=(map_borders[3]+map_borders[1])/2

    def setZoom(MapB):                                          #determin level of zoom
        Zsize=0
        size=0
        latD=MapB[0]-MapB[2]
        longD=MapB[3]-MapB[1]
        if latD<=longD:
            size=longD
        else:
            size=latD
        for i in range(len(zdata)):
            if size>zdata[i]:
                Zsize=i-1
                break
        return Zsize

    Zs=setZoom(map_borders)-1
    Mbpoints=[Latcenter+zdata[Zs]/2,longcenter-zdata[Zs]/2,Latcenter-zdata[Zs]/2,longcenter+zdata[Zs]/2]
    
    
    map_req_url="https://api.tomtom.com/map/1/staticimage?layer=basic&style=main&format=png&zoom="+str(setZoom(map_borders)-1)+"&center="+str(longcenter)+"%2C%20"+str(Latcenter)+"&view=Unified&key="+APIkey
    print(map_req_url)
    imageRequest = urllib.request.urlopen(map_req_url)
    imageBinary = imageRequest.read()
    open('SSF\static\img\Map.png', 'wb').write(imageBinary)
    
    vis = GPSVis(data_path='TEMP/cordscollector.csv',                            #Chemin du fichier contenant =l'historique des cordonnées envoyée par le gps
             map_path='SSF\static\img\Map.png',                     #Chemin du l'image dont on va dessiner la trajectoire
             points=tuple(Mbpoints))                                #les cordonnées d'image

    vis.create_image(color=(0, 0, 255), width=3)                    # couleur et largeur du trait choisient pour le dessin
    vis.plot_map(output='save')

    return round(msspeed,2)

def copymap(pt='resultMap.png'):                                        #change the img shown to user by new one
    with open("SSF/static/img/"+pt, "rb") as image:
        f = image.read()
        b = bytearray(f)
        open('SSF/static/img/outputMap.png', 'wb').write(b)
    return

def makemap_one_point(latitude,longitude,zoom=15):
    zdata=[360, 180.0, 90.0, 45.0, 22.5, 11.25, 5.625, 2.813, 1.406, 0.703, 0.352, 0.176, 0.088, 0.044, 0.022, 0.011, 0.005, 0.003,  0.001, 0.001 , 0.0005 , 0.00025]
    Zs=zoom
    Mbpoints=[latitude+zdata[Zs]/2,longitude-zdata[Zs]/2,latitude-zdata[Zs]/2,longitude+zdata[Zs]/2]
    map_req_url="https://api.tomtom.com/map/1/staticimage?layer=basic&style=main&format=png&zoom="+str(zoom)+"&center="+str(longitude)+"%2C%20"+str(latitude)+"&view=Unified&key="+APIkey
    print(map_req_url)
    imageRequest = urllib.request.urlopen(map_req_url)
    imageBinary = imageRequest.read()
    open('SSF\static\img\Map.png', 'wb').write(imageBinary)
    cords_collector=open('TEMP/cordscollector.csv','w',newline='')
    cords_writer=csv.writer(cords_collector)
    cords=[latitude,longitude]
    cords_writer.writerow(cords)
    cords_writer.writerow(cords)
    
    vis = GPSVis(data_path='TEMP/cordscollector.csv',                            #Chemin du fichier contenant =l'historique des cordonnées envoyée par le gps
             map_path='SSF\static\img\Map.png',                            #Chemin du l'image dont on va dessiner la trajectoire
             points=tuple(Mbpoints))                        #les cordonnées d'image

    vis.create_image(color=(0, 0, 255), width=3)                 # couleur et largeur du trait choisient pour le dessin
    vis.plot_map(output='save')


    return

def send_mail(nom_entreprise,pays,nom,prenom,email,telephone,message):
    strings="nom_entreprise: "+ nom_entreprise +"\n"+"pays: "+pays+"\n"+"Nom: "+nom+"\n"+"Prenom: "+prenom+"\n"+"email: "+email+"\n"+"telephone: "+telephone+"\n"+"message: "+"\n"+message+"\n"
    msg = """\
    Subject: Hi there

"""+strings

    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "sys.s.f.no.reply@gmail.com"  # Enter your address
    receiver_email = "anass.assila.7@gmail.com"  # Enter receiver address
    password = "SuiviFlotte1"
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg)

""" def getchauffeur(id_chauffeur):
    con = sqlite3.connect('db.sqlite3')
    cur= con.cursor()
    cur.execute(''' SELECT * FROM BE_chauffeurs
    WHERE id_chauffeur='''+"\'"+id_chauffeur+"\'")
    rows=cur.fetchall()
    if rows==[]:
        return
    else:
        return rows[0]

def getvehicule(id_vehicule):
    con = sqlite3.connect('db.sqlite3')
    cur= con.cursor()
    cur.execute(''' SELECT * FROM BE_vehicules
    WHERE id_vehicule='''+"\'"+id_vehicule+"\'")
    rows=cur.fetchall()
    if rows==[]:
        return
    else:
        return rows[0]
 """
