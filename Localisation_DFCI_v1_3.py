##Repertoire_des_carreaux_DFCI=folder
##Coordonnees_DFCI=string LE06L1.2


""" Localisation_DFCI.py: Permet de localiser la fenetre carte sur des coordonnees DFCI.
Celles-ci doivent etre installees sur le poste de l utilisateur."""

__author__ = "Sylvain CHARAUD"
__copyright__ = "Faites-en bon usage ..."
__version__ = "17/08/2016"

import os, processing
from PyQt4.QtCore import *
from qgis.core import *
from qgis.utils import *


def Zoom(couche):
    """
    Fonction permettant de zoomer la fenetre carte sur la selection en cours dans la "couche"
    """
    fenetre = couche.boundingBoxOfSelected()
    if fenetre.height() > 0:
        iface.mapCanvas().setExtent(fenetre)
        iface.mapCanvas().refresh()
    return fenetre

def ZoomFin(fenetre, cote, dec_x, dec_y):
    """
    Fonction permettant de zoomer sur un carre de "cote",
    dont le centre est decale de dec_x et dec_y par rapport a la fenetre (QgsRectangle) donnee
    """
    centreQgis = fenetre.center()
    centre = [0,0]

    centre[0] = centreQgis.x() + dec_x
    centre[1] = centreQgis.y() + dec_y

    xmin = centre[0] - cote/2
    ymin = centre[1] - cote/2
    xmax = centre[0] + cote/2
    ymax = centre[1] + cote/2

    fenetre = QgsRectangle(xmin, ymin, xmax, ymax)

    if fenetre.height() > 0:
        iface.mapCanvas().setExtent(fenetre)
        iface.mapCanvas().refresh()
    return fenetre

def Recherche(expression, couche):
    """
    Fonction permettant de rechercher le carreau dans la "couche" de carreaux
    qui repond a la "l expression" demandee (filtre de la requete)
    Zoome sur le carreau avec la fonction "Zoom" s il a ete trouve
    """
    #Remise a 0 de la selection
    couche.removeSelection()

    #Construction de la requete
    requete = QgsFeatureRequest()
    requete.setFilterExpression(expression)

    #Lancement de la requete
    for carreau in couche.getFeatures(requete):
        couche.select(carreau.id())

    #Comptage et affichage du nombre de carreaux trouves
    nb_carreaux = couche.selectedFeatureCount()
    message = str(nb_carreaux) + " carreau trouve"
    print(message)
    progress.setText(message)


    #Zoom sur le carreau
    fenetre = Zoom(couche)
    #Invite a relancer la recherche si aucun carreau trouve
    if nb_carreaux == 0:
        message = 'Carreau non trouve. Relancez la recherche. Les coordonnees doivent ressembler a "LE06L1.5", "LE06L1", "LE06" ou "LE"'
        print(message)
        iface.messageBar().pushMessage(message)

    return fenetre


def ZoomDFCI(coordDFCI):
    """
    Fonction permettant de construire la requete permettant de rechercher
    le carreau DFCI sur le bon carroyage
    en fonction de la longueur de la chaine de caracteres "coordDFCI"
    Appelle la fonction Recherche pour lancer la recherche du carreau et zoomer sur le bon carreau.
    """
    #Declaration des variables
    coordDFCI = coordDFCI.upper() #coordonnees a rechercher
    fenetre = dfci.boundingBoxOfSelected() #emprise de la fenetre carte

    nb_carreaux = 0 #nombre de carreaux DFCI trouves
    preciDFCI = 0 #"precision" des coordonnees a rechercher
    coordCarreau = ""
    coord100 = ""
    coord20 = ""
    coord2 = ""
    coordFin = 0

    #Decoupage des coordonnees par "precision" (100km, 20km, 2km et precision finale)
    preciDFCI = len(coordDFCI) #longueur de la chaine de caracteres des coordonnees DFCI a rechercher
    print(str(preciDFCI))
    progress.setText(str(preciDFCI))

    if preciDFCI > 8 : #Coordonnees DFCI trop longues (trop de caracteres saisis)
        message = 'Coordonnees invalides, relancez la recherche. Les coordonnees doivent ressembler a "LE06L1.5", "LE06L1", "LE06" ou "LE"'
        iface.messageBar().pushMessage(message)
    elif preciDFCI not in [2,4,6,8] : # Coordonnees DFCI incompletes (un caractere de trop ou qui manque)
        iface.messageBar().pushMessage("Precisez vos coordonnees, et relancez la requete.")
    else :
        if preciDFCI > 1:
            coord100 = coordDFCI [0:2] #Coordonnees  a 100km
            print(coord100)
            progress.setText(coord100)
        if preciDFCI > 3:
            coord20 = coordDFCI [2:4] # Coordonnees a 20km
            print(coord20)
            progress.setText(coord20)
        if preciDFCI > 5:
            coord2 = coordDFCI [4:6] # Coordonnees a 2km
            print(coord2)
            progress.setText(coord2)
        if preciDFCI > 6:
            try:
                coordFin = int(coordDFCI [7]) # reperage fin (de 1 a 5 : 4 coins + centre)
                print(str(coordFin))
                progress.setText(str(coordFin))
            except:
                message = 'Coordonnees invalides, relancez la recherche. Les coordonnees doivent ressembler a "LE06L1.5", "LE06L1", "LE06" ou "LE"'
                print (message)
                iface.messageBar().pushMessage(message)
        coordCarreau = coord100+coord20+coord2 # c est ces coordonnees qui vont etre utilisees pour les requetes
        print(coordCarreau)
        progress.setText(coordCarreau)

        if preciDFCI > 5:
            # Recherche des coordonnees dans le carroyage a 2km
            # la condition dans l editeur de requete SQL de QGIS a la syntaxe suivante : upper("NOM") =  LE06L1
            expression = 'upper("NOM") = ' +"'"+coordCarreau+"'"
            print("Expression : "+expression)
            progress.setText("Expression : "+expression)
            fenetre = Recherche(expression, dfci) # recherche et zoom sur le carreau

            #Zoom sur la subdivision du carreau
            #Carreau divise en 4 (de haut gauche a bas droite), plus centre = partie 5
            #-----------
            #|1 _|_ 2 |
            #|_| 5 |__|
            #|  |__|   |
            #|4   |   3 |
            #----------
            if preciDFCI == 8 and fenetre.height() > 0:
                """Centre de la fenetre decale de
                #0 si coordFin= 5
                #(-1km;+1km) si coordFin = 1
                #(+1;+1) si coordFin = 2
                #(+1;-1) si coordFin = 3
                #(-1;-1) si coordFin = 4
                #Zoom sur un carre de 1km dont le centre vient d etre defini"""

                cote = 1000. #largeur des carres de "precision" DFCI
                dec_x = 0
                dec_y = 0
                message = 'Zoom de precision sur le cadran numero ' + str(coordFin)
                if coordFin == 1:
                    dec_x = - cote/2
                    dec_y = cote/2
                elif coordFin == 2:
                    dec_x = cote/2
                    dec_y = cote/2
                elif coordFin == 3:
                    dec_x = cote/2
                    dec_y = - cote/2
                elif coordFin == 4:
                    dec_x = - cote/2
                    dec_y = - cote/2
                elif coordFin == 5:
                    dec_x = dec_y = 0
                else:
                    cote = fenetre.height()
                    message = 'Pas de zoom de precision, le numero de cadran doit etre compris entre 0 et 5 inclus.'
                print(message)
                progress.setText(message)
                iface.messageBar().pushMessage(message)
                fenetre = ZoomFin(fenetre, cote, dec_x, dec_y)
                return fenetre

        if preciDFCI == 2:
            # Recherche des coordonnees dans le carroyage a 2km
            # la condition dans l editeur de requete SQL de QGIS a la syntaxe suivante : upper("COORD_100") =  LE
            expression = 'upper("COORD_100") = ' +"'"+coordCarreau+"'"
            print("expression : "+expression)
            progress.setText("expression : "+expression)
            fenetre = Recherche(expression, dfci100) # recherche et zoom sur le carreau

        if preciDFCI == 4:
            # Recherche des coordonnees dans le carroyage a 2km
            # la condition dans l editeur de requete SQL de QGIS a la syntaxe suivante : upper("NOM") =  LE06
            expression = 'upper("NOM") = ' +"'"+coordCarreau+"'"
            print("expression : "+expression)
            progress.setText("expression : "+expression)
            fenetre = Recherche(expression, dfci20) # recherche et zoom sur le carreau


# Lancement des tests

"""Reallon"""
#CoordDFCI = "LE06L1.2"
#ZoomDFCI(CoordDFCI)
#
"""Gare TGV d Aix"""
#CoordDFCI = "KD42A6.3"
#ZoomDFCI(CoordDFCI)

"""Aiguille d Argentiere"""
#CoordDFCI = "LG60B8"
#ZoomDFCI(CoordDFCI)

"""Paris Est"""
#CoordDFCI = "GL02"
#ZoomDFCI(CoordDFCI)

"""Corse du Sud"""
#CoordDFCI = "NB"
#ZoomDFCI(CoordDFCI)

#CoordDFCI = "HK1"
#ZoomDFCI(CoordDFCI)

#CoordDFCI = "mlkjmljm"
#ZoomDFCI(CoordDFCI)


#Lancement de l'instance

""" -------------------------------------------------------
Verifier les chemins et noms de fichiers ci-dessous (entre guillemets)
Vous pouvez trouver le carroyage DFCI sur internet (licence ouverte) aux adresses suivantes
https://www.data.gouv.fr/fr/datasets/carroyage-dfci-2-km/
https://www.data.gouv.fr/fr/datasets/carroyage-dfci-20-km/
https://www.data.gouv.fr/fr/datasets/carroyage-dfci-100-km/
Copier les fichiers dans un repertoire, et modifier la ligne ci-dessous ("cheminDFCI = ...")
------------------------------------------------------- """

#Chemin "de base" ou est stocke le carroyage DFCI
cheminDFCI = Repertoire_des_carreaux_DFCI

if Repertoire_des_carreaux_DFCI == "":
    cheminDFCI = "F:\Donnees\SIG\DFCI" # parametre saisi a la main dans le code pour eviter de saisie le repertoire a chaque fois

#Nom des fichiers de carroyage (extension incluse)
nomDFCI2km = "CARRO_DFCI_2x2_L93.shp"
nomDFCI20km = "CARRO_DFCI_20x20_L93.shp"
nomDFCI100km = "CARRO_DFCI_100X100_L93.shp"


#Import des carroyages DFCI (en mode muet)
cheminDFCI2km = os.path.join(cheminDFCI , nomDFCI2km[0:-4] , nomDFCI2km)
print(cheminDFCI2km)
progress.setText(cheminDFCI2km)
dfci = QgsVectorLayer(cheminDFCI2km, "DFCI2km", "ogr")
#dfci = iface.addVectorLayer(cheminDFCI2km, "DFCI2km", "ogr") #si besoin d afficher le carroyage

cheminDFCI20km = os.path.join(cheminDFCI , nomDFCI20km[0:-4] , nomDFCI20km)
print(cheminDFCI20km)
progress.setText(cheminDFCI20km)
dfci20 = QgsVectorLayer(cheminDFCI20km, "DFCI20km", "ogr")
#dfci20 = iface.addVectorLayer(cheminDFCI20km, "DFCI20km", "ogr") #si besoin d afficher le carroyage

cheminDFCI100km = os.path.join(cheminDFCI , nomDFCI100km[0:-4] , nomDFCI100km)
print(cheminDFCI100km)
progress.setText(cheminDFCI100km)
dfci100 = QgsVectorLayer(cheminDFCI100km, "DFCI100km", "ogr")
#dfci100 = iface.addVectorLayer(cheminDFCI100km, "DFCI100km", "ogr") #si besoin d afficher le carroyage


if not dfci:
    iface.messageBar().pushMessage("Le carroyage DFCI n a pas pu etre charge")
elif not dfci20:
    iface.messageBar().pushMessage("Le carroyage DFCI a 20km n a pas pu etre charge")
elif not dfci100:
    iface.messageBar().pushMessage("Le carroyage DFCI a 100 km n a pas pu etre charge")
else:
    ZoomDFCI(Coordonnees_DFCI) #Lancement de l instance uniquement si les 3 carroyages sont bien charges