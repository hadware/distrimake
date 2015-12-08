# distrimake
Un sous-ensemble de Makefile distribué en utilisant Python-Pyro

## Prérequis

### Machine "Master"

Sur la machine "master", qui lance le processus *dispacher*, distrimake nécessite l'installation de python3, 
d'un client SSH et de quelques bibliothèques python. Pour installer les dépendances, il suffit de faire:

    sudo pip3 install -r requirements.txt

ou 
    
    pip install -r requirements.txt

si vous êtes dans un venv python3.

### Machine "Slave"

Une machine *slave* (ou cliente) ne nécessite que l'installation de trois paquets : 

    sudo apt-get install python3 python3-pip python-virtualenv

## Utilisation

### Lancement

L'intégralité de l'utilisation du programme se fait *via* un fichier de configuration, 
dont un exemple est proposé dans le dossier `configs/`. Une fois la configuration est jugée satisfaisante, 
il suffit de lancer la commande répartie avec:

    ./distrimake.py config/config-file.yaml

### Le fichier de configuration

Le fichier de configuration est en YAML, et sert à paramétrer principalement 3 choses: 

* le fichier Makefile à éxécuter
* les exécutables et fichiers annexes requis par les commandes utilisées à l'intérieur du Makefile
* les hôtes esclaves, et les identifiants nécessaires pour s'y connecter

Il est aussi judidieux de paramétrer 

 