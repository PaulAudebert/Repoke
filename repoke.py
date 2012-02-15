#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import getpass
import urllib, urllib2, cookielib
import re


def mon_compte() :
	"""
	Fonction retournant le login et le mot de passe de l'utilisateur
	"""
	try :
		with open(nom_conf) as configuration :
			utilisateur = configuration.readline().strip('\n')
			mot_de_passe = configuration.readline().strip('\n')

	except :
		with open(nom_conf, 'w') as configuration :
			
			utilisateur = raw_input("Adresse électronique : ")
			configuration.write(utilisateur + '\n')
			
			mot_de_passe = getpass.getpass("Mot de passe : ")
			configuration.write(mot_de_passe + '\n')
	
	return utilisateur,mot_de_passe


def authentification(utilisateur, mot_de_passe) :
	"""
	Fonction devant recupèrer un cookie et un PHPSESSID
	"""
	global urlOpener
	
	# On prépare les données en POST
	donnees = urllib.urlencode({
		"email" : utilisateur,		 # Champ du formulaire d'authentification
		"pass" : mot_de_passe		 # Champ du formulaire d'authentification
		})

	# On prépare la requête
	lrequete = [urllib2.Request(site_web + page_form), urllib2.Request(site_web + page_post, donnees)]

	# On envoie la requete
	for requete in lrequete : urlOpener.open(requete)
	
	# Récupération du l'identifiant de l'utilisateur
	identifiant, = [cookie.value for cookie in cj if cookie.name == "c_user"]
	
	return identifiant


def analyse() :
	"""
	Fonction traitant la page des pokes
	"""
	global urlOpener
	lpokeur = []
	
	# On prépare la requête
	requete = urllib2.Request(site_web + page_pokes)

	# On envoie la requete
	page = urlOpener.open(requete)
	retour = page.read()
	
	# Analyse du retour
	lpokeur = regex_pokeur.findall(retour)
	
	return lpokeur


def poke(pokeur) :
	"""
	Fonction pokant un amis
	"""
	global urlOpener
	
	# On prépare les données en POST
	donnees = urllib.urlencode({
		"uid" : pokeur,
		#"pokeback" : 1,
		#"nctr[_mod]" : "pagelet_pokes",
		#"post_form_id" : "c6806487deec5b8c3c21be49ded40aa5",
		"fb_dtsg" : "AQBJ1B5M",
		#"lsd" : "",
		#"post_form_id_source" : "AsyncRequest",
		#"phstamp" : 16581667449665377168,
		"__user" : utilisateur["id"]
		})
	
	# On prépare la requête
	requete = urllib2.Request(site_web + page_pokes_post, donnees)
	
	# On envoie la requete
	urlOpener.open(requete)


################################################################################
# Fonction principale							       #

# Parametre
nom_script = os.path.split(sys.argv[0])[1]
nom_conf = os.path.splitext(nom_script)[0] + ".conf"

cj = cookielib.CookieJar()
urlOpener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
site_web = "https://www.facebook.com/"
page_form = ""
page_post = "login.php?login_attempt=1"
page_pokes = "pokes"
page_pokes_post = "ajax/pokes/poke_inline.php?__a=1"

regex_pokeur = re.compile("\/ajax\/pokes\/poke_inline\.php\?uid=([0-9]+)")
utilisateur = {}

# Etape I : Authentification sur facebook
print("Authentification...")
utilisateur["courriel"],utilisateur["mot_de_passe"] = mon_compte()
utilisateur["id"] = authentification(utilisateur["courriel"], utilisateur["mot_de_passe"])
if not utilisateur["id"] :
	print("Erreur de connection.")
	sys.exit(1)

# Etape II : Récupération de la liste des pokeurs
print("Le script analyse qui vous à poké...")
lpokeur = analyse()

# Etape III : On poke tout le monde
if lpokeur :
	print("Le script va poker {0} personne(s) en retour...".format(len(lpokeur)))
	for pokeur in lpokeur : poke(pokeur)
else :
	print("Personne ne vous à poké.")
	sys.exit(0)

print("C'est fait ! A bientôt.")

# Fin									       #
################################################################################
