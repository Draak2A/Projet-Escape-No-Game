import matplotlib.pyplot as plt
import numpy as np

def crcAller(bits):
    diviseur = "1001"   #Diviseur pour notre protocole crc (diviseur commun à l'envoyeur et le recepteur)
    resultat_crc = []   #Liste pour stocker les données en ajoutant le reste de la division euclidienne

    for e in range(0, len(bits)//8):  #On parcours chaque octet de données
        donne_str = ""
        for i in bits[0:8]:     #On découpe nos données par paquet de 8 bits
            donne_str = donne_str + str(i)
            del bits[0]

        donne_str_dividende = donne_str + "0000"
        donne_int_dividende = int("0B" + donne_str_dividende,0) #Converti le dividende en décimal
        diviseur_dec = int("0B" + diviseur,0)   #Converti le diviseur en décimal
        reste = donne_int_dividende % diviseur_dec  #Récupère le reste de la division
        reste_bin = bin(reste)[2:].zfill(4)  #Le reste est en binaire et doit faire obligatoirement 4 bits (exemple : 0010; 1101; 0111...)
        donnee_int = bin(int("0B" + donne_str,0))[2:].zfill(8)

        for j in donnee_int:     #Ajoute les données dans une liste
            if j == "1":
                resultat_crc.append(1)
            if j == "0":
                resultat_crc.append(0) 
        for k in reste_bin:      #Ajoute le reste à la fin de l'octet
            if k == "1":
                resultat_crc.append(1)
            if k == "0":
                resultat_crc.append(0)

    print("resultat crc", resultat_crc) #Affiche les données une fois traité par le protocole crc
    return resultat_crc #Retourne les données une fois traité par le protocole crc

def trame(bits, type_fichier):
    #Octet pour définir le type de fichier envoyé, chaque type de fichier à un octet différent
    prot_txt = [1,1,0,0,0,0,1,1]
    prot_txt2 = [1,1,0,1,1,0,1,1]
    prot_bin = [0,1,1,0,0,1,1,0]

    if type_fichier == "txt":   #Si le type de fichier envoyé est un message on ajoute l'octet correspondant à ce type de fichier
        bits = prot_txt + bits
        print("Octet protocole type de fichier : ", prot_txt) #On affiche l'octet ajouté
    elif type_fichier == "txt2":
        bits = prot_txt2 + bits
        print("Octet protocole type de fichier : ", prot_txt2)
    elif type_fichier == "bin":
        bits = prot_bin + bits
        print("Octet protocole type de fichier : ", prot_bin)

    #Fanion
    fanion_debut = [1,1,1,1,1,1,1,1]    #Octet représentant le début de la trame
    fanion_fin = [0,0,0,0,0,0,0,0]  #Octet représentant la fin de la trame
    bits = fanion_debut + bits
    print("Fanion de début : ", fanion_debut)
    bits = bits + fanion_fin
    print("Fanion de fin : ", fanion_fin)
    print("Trame", bits)
    return bits #On retourne la trame entière

def Manchester(bits):
    manchester = [] #Liste pour stocker le résultat du codage Manchester
    for i in list(bits): #On parcour la liste bits
        if i == 1:  #Si 1 est dans la liste bits, on ajoute 1 et 0 dans une autre liste
            manchester.append(1)
            manchester.append(0)
        if i == 0:  #Si 0 est dans la liste bits, on ajoute 1 et 0 dans une autre liste
            manchester.append(0)
            manchester.append(1)

    print("Codage Manchester : ", manchester) #On affiche le résultat du codage Manchester
    return manchester   #On retourne le résultat du codage Manchester

def ASK(ASK_manchester):

    Fe = 44100                            # Fréquence d'échantillonnage
    baud = 200                            # Débit souhaité sur le canal de transmission exprimé en bit/s
    Nbits = len(ASK_manchester)           # Nombre de bits à transmettre
    Ns = int(Fe/baud)                     # Nombre de symboles par bit (Fréq d'echan / Débit binaire)
    N = int(Nbits * Ns)                   # Nombre de symboles total à envoyer (Nombre de symboles par bit * Nombre de bits)
    Fp = 2000                             # Fréquence de l'onde porteuse (2000 Hz)

    # Le message binaire initial est dupliqué Ns fois pour avoir un vecteur de même taille que le temps (t)
    message_bit_duplique= np.repeat(ASK_manchester, Ns)

    t = np.arange (0.0, N) / Fe

    # On rélalise la modulation en amplitude
    Porteuse = np.sin(2 * np.pi * Fp * t)

    ASK = message_bit_duplique * Porteuse

    # Enregitrer dans un ficheir CSV le résulats de la modulation ASK
    np.savetxt("Message.csv", ASK, fmt='%.6f', delimiter=',')

    print("Signal modulé : ", ASK) #On affiche le signal modulé

    plt.figure (figsize = (10,6))   #On définitla taille des graph
    plt.plot(t[0:2000],message_bit_duplique[0:2000])    #On affiche qu'une partie des échantillons (pour que cela soit lisible)
    plt.xlabel("Temps [s]")
    plt.title("Message binaire codé Manchester")

    plt.figure (figsize = (10,6))
    plt.plot(t[0:2000],Porteuse[0:2000])
    plt.title("Porteuse")

    plt.figure (figsize = (10,6))
    plt.plot(t[0:2000],ASK[0:2000])
    plt.xlabel("Temps [s]")
    plt.title("Modulation ASK (amplitude) du message binaire codé Manchester")

    plt.show()  #On affiche les graph

def message():
    texte = ""  #Initialisation des variables
    texte_bit = []

    reponse = int(input("""Quel type de message envoyer ? 
    Message -> 1 
    Fichier texte -> 2\n"""))
    print("Réponse sélectionnée : ", reponse)   #Affiche la réponse sélectionné

    if reponse == 1:
        type_fichier = "txt"    #Donne le type de fichier qui va être envoyé pour la composition de la trame
        while(len(texte) == 0): #Tant que le message que l'on souhaite envoyer est vide, on affiche le message suivant
            texte = input("Saisissez votre message\n")

    elif reponse == 2:
        fichier = ""
        type_fichier = "txt2"
        while(len(fichier) == 0):
            try :
                fichier = input("Entrez le nom du fichier (sans l'extension)\n")    #Demande la saisie du nom du fichier à envoyer
                searchfile = open(fichier + ".txt", "r")    #Ouvre le fichier demandé en lecture
                for i in searchfile:    #Parcours le fichier
                    texte = i   #Récupère les caractères dans le fichier
                searchfile.close()  #Ferme le fichier
                print(texte)    #Affiche le texte dans le fichier
            except FileNotFoundError:   #Si le fichier est introuvable ou n'existe pas cela est signalé et on attend la saisi d'un nom de fichier correct
                print("Fichier introuvable. Veuillez réessayer")
                fichier = ""

    for char in texte:  #Parcour le texte à envoyer pour le convertir en ASCII
        if len(bin(ord(char))[2:]) == 7:    #Si le caractère est codé sur 7 bits (table ASCII de base)
            binaire = "0" + bin(ord(char))[2:]  #On ajoute un 0 au début et on converti le code unique ASCII du caractère en binaire ([2:] permet d'enlever les deux premier caractère de la valeur binaire soit 0b)
        elif len(bin(ord(char))[2:]) == 6:  #Si le caractère est codé sur 6 bits tel que le caractère espace
            binaire = "00" + bin(ord(char))[2:] #On ajoute deux 0 au débutau début et on converti le code unique ASCII du caractère en binaire
        else:   #Si le caractère ASCII est déjà sur 8 bits (table ASCII étendue)
            binaire = bin(ord(char))[2:]
        texte_bit.extend(int(i) for i in binaire)   #On ajoute tout les bits dans une liste (après avoir converti les élément en int)

    print("Texte en binaire : ", texte_bit) #On affiche notre texte codé en binaire
    
    texte_bit_crc = crcAller(texte_bit)     #Phase aller du protocole CRC
    trame_bin = trame(texte_bit_crc, type_fichier)  #Création de la trame de données
    texte_bit_Manchester = Manchester(trame_bin)    #On encode le signal
    ASK(texte_bit_Manchester)   #On module le signal

def binaire():
    fichier = ""
    list_bin = []
    type_fichier = "bin"
    while(len(fichier) == 0):   #Tant que le aucun nom de fichier est saisi
        try :
            fichier = input("Entrez le nom du fichier (sans l'extension)\n")    #Demande la saisie du nom du fichier à envoyer
            searchfile = open(fichier + ".txt", "r")    #Ouvre le fichier en lecture
            for i in searchfile:    #Parcours le fichier et récupère la suite binaire entière
                for e in i: #Parcours chaque élément
                    list_bin.append(int(e)) #Ajoute chaque élément à une liste
            searchfile.close()  #Fermeture du fichier
        except FileNotFoundError:   #Si le fichier est introuvable ou n'existe pas cela est signalé et on attend la saisi d'un nom de fichier correct
            print("Fichier introuvable. Veuillez réessayer")
            fichier = ""

    print("Message binaire : ", list_bin)   #Affiche la suite binaire qui va être envoyer

    texte_bit_crc = crcAller(list_bin)
    trame_bin = trame(texte_bit_crc, type_fichier)
    texte_bit_Manchester = Manchester(trame_bin)
    ASK(texte_bit_Manchester)


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

Quel type de message souhaitez-vous envoyer ?
    Message écrit -> 1
    Fichier binaire -> 2""")

suivant = 0

while suivant == 0:
    try:
        reponse = int(input())
        print("Réponse sélectionnée : ", reponse)
        suivant = 1
    except ValueError:
        print("Veuillez sélectionner une réponse valide")

if reponse == 1 :
    message() 
elif reponse == 2 :
    binaire()
else :
    print("Réponse invalide")