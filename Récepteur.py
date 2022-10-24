import numpy as np
import os

def ASK():
    #Lecture Fichier CSV
    ASK1 = np.genfromtxt("Message.csv")
    print("Signal modulé : ", ASK1)

    N = len(ASK1)
    Ns = 220
    Fe = 44100
    Fp = 2000

    t = np.arange (0.0,N)/Fe    #Vecteur temps

    Porteuse=np.sin(2 * np.pi * Fp * t) # Porteuse
    Produit = ASK1 * Porteuse   # Multiplier le signal modulé par le signal de la porteuse utilisée

    y = []

    for i in range(0, N, Ns):
        y.append (np.trapz(Produit[i:i+Ns], t[i:i+Ns]))

    message_demodule = np.array(y) > 0 

    message_recu_decode = []

    for ii in range (0, len(message_demodule)):
        
        if message_demodule [ii] == True:
            message_recu_decode.extend([int(1)]) 
        else:
            message_recu_decode.extend([int(0)]) 
    print("Signal démodulé : ", message_recu_decode)
    return(message_recu_decode)

def Manchester(bits):
    manchester = [] #Liste pour stocker le résultat du codage Manchester
    for i in range(0,round(len(bits)/2)):   #Parcours la suite binaire reçue
        if (bits[2*i] == 1 and bits[2*i+1] == 0):   #Parcours les éléments deux par deux
            manchester.append(1)    #Si on a 1 et 0 à la suite, on ajoute 1 dans une autre liste
        if (bits[2*i] == 0 and bits[2*i+1] == 1):
            manchester.append(0)    #Si on a 0 et 1 à la suite, on ajoute 0 dans une autre liste
    print("Décodage Manchester : ", manchester)   #On affiche les données une fois décodé
    return manchester

def trame(bits):
    fanion_debut = []
    fanion_fin = []
    type_fichier = ""

    for i in bits[0:8]:     #Vérification du premier octet
       fanion_debut.append(i) 
       del bits[0]
    print("Fanion de début : ", fanion_debut)
    for i in bits[-8:]:     #Vérification du dernier octet
        fanion_fin.append(i) 
        del bits[-1]
    print("Fanion de fin : ", fanion_fin)
    if fanion_debut == [1,1,1,1,1,1,1,1] and fanion_fin == [0,0,0,0,0,0,0,0]:   #Si les fanion de début et de fin sont correct
        print("Début de transmission")
        protocole = []
        for i in bits[0:8]:     #On vérifie l'octet de protocole
            protocole.append(i) 
            del bits[0]
        print("Type de message", protocole)
        if protocole == [1,1,0,0,0,0,1,1]:  #Identification du protocole envoyé
            print("Nouveau message reçu")
            print("Données", bits)
            type_fichier = "txt"    #Enregistre le type de fichier reçu
            return bits, type_fichier
        elif protocole == [1,1,0,1,1,0,1,1]:
            print("Nouveau fichier texte reçu")
            print("Données", bits)
            type_fichier = "txt2"
            return bits, type_fichier
        elif protocole == [0,1,1,0,0,1,1,0]:
            print("Nouveau fichier binaire reçu")
            print("Données", bits)
            type_fichier = "bin"
            return bits, type_fichier 
        else:
            print("Erreur protocole inconnu")
    else:
        print("Erreur fanion manquant dans la trame de données transmise")

def crcRetour(bits):
    diviseur = "1001"   #Diviseur pour notre protocole crc (diviseur commun à l'envoyeur et le recepteur)
    resultat_crc = []   #Liste pour stocker les données une fois le reste enlevé et les données vérifié
    integrite_donnee = True

    for e in range(0, len(bits)//12):  #On parcours chaque octet de données plus le reste ajouté
        donne_str = ""
        for i in bits[0:12]:    #On découpe nos données par paquet de 8 bits (octet de données + 4 bits de reste)
            donne_str = donne_str + str(i)
            del bits[0]

        reste_reçu = donne_str[8:]      #On isole l'octet de donnée reçu du reste ajouté dans la phase aller du CRC
        donne_str2 = donne_str[:-4]
        donne_str_dividende = donne_str2 + "0000"
        donne_int_dividende = int("0B" + donne_str_dividende,0) #Converti le dividende en décimal
        diviseur_dec = int("0B" + diviseur,0)   #Converti le diviseur en décimal
        reste = donne_int_dividende % diviseur_dec  #Récupère le reste de la division
        reste_bin = bin(reste)[2:].zfill(4)     #Le reste est en binaire et doit faire obligatoirement 4 bits (exemple : 0010; 1101; 0111...)
        donnee_int = bin(int("0B" + donne_str,0))[2:-4].zfill(8)

        for j in donnee_int: #Ajoute les données dans une liste
            if j == "1":
                resultat_crc.append(1)
            if j == "0":
                resultat_crc.append(0) 
        if reste_reçu == reste_bin: #Vérifie si le reste obtenu correspond au reste reçu
            integrite_donnee = True
        if reste_reçu != reste_bin:
            integrite_donnee = False
    if integrite_donnee:
        print("Aucune erreur de transmission détectée")
        print("Résultat crc", resultat_crc)
        return resultat_crc
    else:
        print("Erreur lors de la transmission des données")

def ASCII(bits, type_fichier):
    bin_data = ""
    for elem in bits:  
        bin_data += str(elem)

    data_reçu =""  #Initialisation d'une chaîne vide pour stocker les données reçues

    def BinaryToDecimal(binary):  
        decimal, i = 0, 0   #Initialisation des variables

        while(binary != 0): 
            dec = binary % 10
            decimal = decimal + dec * pow(2, i) 
            binary = binary//10
            i += 1
        return (decimal)

    for i in range(0, len(bin_data), 8): 
        temp_data = int(bin_data[i:i+8])
        decimal_data = BinaryToDecimal(temp_data)
        data_reçu = data_reçu + chr(decimal_data) 

    if type_fichier == "txt":
        print("Le message reçu est :", data_reçu) 
    if type_fichier == "txt2":
        return data_reçu

def creationFichier(bits):
    fichier_bin = open("message_recu.txt","w")  #Création d'un fichier vide
    bin_data = ""   
    for elem in bits:  
        bin_data += str(elem)
    fichier_bin.write(bin_data)
    fichier_bin.close()
    print("Fichier enregistré")
    os.startfile("message_recu.txt")

print("""                                                                                    
░█▀▀░█▀▄░█▀█░█░█░█▀█░█▀▀   ▄█░ ░ ░█▀█░ 
░█░█░█▀▄░█░█░█░█░█▀▀░█▀▀   ░█░ ▄ █▄▄█▄ 
░▀▀▀░▀░▀░▀▀▀░▀▀▀░▀░░░▀▀▀   ▄█▄ █ ░░░█░

███████╗███████╗ ██████╗ █████╗ ██████╗ ███████╗    ███╗   ██╗ ██████╗      ██████╗  █████╗ ███╗   ███╗███████╗
██╔════╝██╔════╝██╔════╝██╔══██╗██╔══██╗██╔════╝    ████╗  ██║██╔═══██╗    ██╔════╝ ██╔══██╗████╗ ████║██╔════╝
█████╗  ███████╗██║     ███████║██████╔╝█████╗      ██╔██╗ ██║██║   ██║    ██║  ███╗███████║██╔████╔██║█████╗  
██╔══╝  ╚════██║██║     ██╔══██║██╔═══╝ ██╔══╝      ██║╚██╗██║██║   ██║    ██║   ██║██╔══██║██║╚██╔╝██║██╔══╝  
███████╗███████║╚██████╗██║  ██║██║     ███████╗    ██║ ╚████║╚██████╔╝    ╚██████╔╝██║  ██║██║ ╚═╝ ██║███████╗
╚══════╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝     ╚══════╝    ╚═╝  ╚═══╝ ╚═════╝      ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝
""")

signal_reçu = ASK() #On démodule le signal
signal_decode = Manchester(signal_reçu) #On décode le signal
donnee, type_fichier = trame(signal_decode) #On vérifie la trame
signal_verif = crcRetour(donnee)    #On vérifie l'intégrité des données

if type_fichier == "txt":
    ASCII(signal_verif, type_fichier)
if type_fichier == "txt2":
    texte_ASCII = ASCII(signal_verif, type_fichier)
    creationFichier(texte_ASCII)
if type_fichier == "bin":
    creationFichier(signal_verif)