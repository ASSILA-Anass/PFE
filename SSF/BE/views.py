from django.shortcuts import render
from BE.models import checklogin, cleartable, copymap,saveposition,main_fetch,databasefiller ,send_mail
from django.http import HttpResponse

# Create your views here.
def home(request):
    with open("TEMP/data_file.json", "w") as write_file:
        print("deleting")
    return render(request, 'Hpage.html')

def contactus(request):
    # ne=fetch_nom_entreprise()
    return render(request,'contactus.html')

def aboutus(request):
    # ne=fetch_nom_entreprise()
    return render(request,'aboutus.html')

def managepage(request):
    return render(request,'mainpage.html')

def login(request):
    username=request.POST['username']
    password=request.POST['password']
    if checklogin(username,password)!=False :
        copymap('first_img.png')
        # ne=fetch_nom_entreprise()
        return render(request,'mainpage.html')      #si login vrai retourne page principale
    else:
        return render(request,'Hpage.html')         #si login faux retourne Hpage

def fetch(request):
    id_vehicule=request.POST['id_vehicule']
    date_heure_A=request.POST['date_heure_A']
    date_heure_B=request.POST['date_heure_B']
    dict=main_fetch(id_vehicule,date_heure_A,date_heure_B)
    # ne=fetch_nom_entreprise()
    # dict.update(ne)
    return render(request,'mainpage.html',dict)

def GPSPORT(request):
    latitude=request.GET['latitude']
    longitude=request.GET['longitude']
    id_chauffeur=request.GET['id_chauffeur']
    id_vehicule=request.GET['id_vehicule']
    Skey=request.GET['Skey']
    saveposition(latitude,longitude,id_chauffeur,id_vehicule,Skey)
    return HttpResponse('')



# cette view est utilisé pour remplir la base de donnée pour visualisation du projet et test
def dbfiller(request):
    latitude=request.GET['latitude']
    longitude=request.GET['longitude']
    id_chauffeur=request.GET['id_chauffeur']
    id_vehicule=request.GET['id_vehicule']
    date_heure=request.GET['date_heure']
    Skey=request.GET['Skey']
    databasefiller(latitude,longitude,id_chauffeur,id_vehicule,Skey,date_heure)
    return HttpResponse('')

def sendmail(request):
    nom_entreprise=request.POST['nom_entreprise']
    pays=request.POST['pays']
    nom=request.POST['nom']
    prenom=request.POST['prenom']
    email=request.POST['email']
    telephone=request.POST['telephone']
    message=request.POST['message']
    send_mail(nom_entreprise,pays,nom,prenom,email,telephone,message)
    dic={
        "response":"message envoyé avec succès"
    }
    return render(request,'contactus.html',dic)