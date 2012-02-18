#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, pickle
import getpass
import urllib, urllib2, cookielib
import re


""" Fonction de déboguage, ne pas y faire attention... """
iii = 1
def DEBOGUE(nom_variable, variable) :
	global iii
	print("\033[31mdébogue {0} : {1} {2} = {3}\033[0m".format(iii, nom_variable, type(variable), variable))
	iii += 1
""" ...merci """


def mon_compte() :
	"""
	Fonction retournant le login et le mot de passe de l'utilisateur
	"""
	try :
		with open(nom_conf) as configuration :
			utilisateur = configuration.readline().strip('\n')
			mot_de_passe = configuration.readline().strip('\n')

	except IOError :
		with open(nom_conf, 'w') as configuration :
			
			utilisateur = raw_input("Adresse électronique : ").strip()
			configuration.write(utilisateur + '\n')
			
			mot_de_passe = getpass.getpass("Mot de passe : ")
			configuration.write(mot_de_passe + '\n')
	
	return utilisateur,mot_de_passe


def authentification() :
	"""
	Fonction devant recupèrer un cookie et un PHPSESSID
	"""
	global urlOpener
	page_auth = ""
	page_auth_post = "login.php?"
	regex_auth = re.compile("Accueil")
	regex_pseudo = re.compile("href=\"https:\/\/www\.facebook\.com\/([a-z0-9]*)\?ref=tn_tnmn\" title=\"Profil\"")
	
	# On va sur le site
	requete = urllib2.Request(site_web + page_auth)
	retour = urlOpener.open(requete).read()
	
	# Si le cookie n'est plus valable
	if not regex_auth.search(retour) :
		
		DEBOGUE("on passe par", "la case authentification")
		
		# On a besoin du login et du mot de passe
		utilisateur,mot_de_passe = mon_compte()
		
		# On prépare les données en POST
		donnees = urllib.urlencode({
			#"post_form_id" : "ae15b2e2cac8401714f442f505c1d1da",
			#"lsd" : "Ufapr",
			#"locate" : "fr_FR",
			#"default_persistent : 1,
			#"charset_test : "%E2%82%AC%2C%C2%B4%2C%E2%82%AC%2C%C2%B4%2C%E6%B0%B4%2C%D0%94%2C%D0%84",
			#"timezone" : -60,
			#"lgnrnd" : "145207_9HFU",
			#"lgnjs" : 1329519129,
			"persistent" : 1,
			"email" : utilisateur,
			"pass" : mot_de_passe
			})
		
		# On va sur le site
		requete = urllib2.Request(site_web + page_auth_post, donnees)
		retour = urlOpener.open(requete).read()
	
	# On récupére les informations sur nous
	try :
		identifiant, = [cookie.value for cookie in cj if cookie.name == "c_user"]
		pseudo, = regex_pseudo.findall(retour)
	
	# Si l'authentification à raté
	except ValueError :
		print("Erreur de connection, regardez erreur.html")
		with open("erreur.html", 'w') as page : page.write(retour.read())
		os.remove(nom_conf)
		os.remove(nom_cookies)
		sys.exit(1)
	
	return identifiant,pseudo


def analyse(page, regex) :
	"""
	Fonction traitant la page des amis
	"""
	global urlOpener
	liste_ami = set()
	
	# On prépare la requête
	requete = urllib2.Request(site_web + page)  # de l'ajax lance https://www.facebook.com/ajax/browser/list/allfriends/index.php?uid=1557923085&infinitescroll=1&location=friends_tab&start=39&__a=1&__user=1557923085
	
	while 1 :
		
		# On envoie la requete
		retour = urlOpener.open(requete).read()
		
		# Analyse du retour
		liste = regex.findall(retour)
		DEBOGUE("liste", liste)
		
		# On tourne jusqu'à ce qu'on ait vraisemblablement pompé tous les amis
		if liste_ami.issuperset(liste) : break
		liste_ami.update(liste)
	
	return liste_ami


def repoke(ami) :
	"""
	Fonction envoyant un poke en retour
	"""
	global urlOpener
	page_pokes_post = "ajax/pokes/poke_inline.php?"  #__a=1"
	
	# On prépare les données en POST
	donnees = urllib.urlencode({
		#"pokeback" : 1,
		#"nctr[_mod]" : "pagelet_pokes",
		#"post_form_id" : "c6806487deec5b8c3c21be49ded40aa5",
		#"lsd" : "",
		#"post_form_id_source" : "AsyncRequest",
		#"phstamp" : 16581667449665377168,
		"uid" : ami,
		"fb_dtsg" : "AQBJ1B5M",
		"__user" : utilisateur["id"]
		})
	
	# On prépare la requête
	requete = urllib2.Request(site_web + page_pokes_post, donnees)
	
	# On envoie la requete
	urlOpener.open(requete)


def poke(ami) :
	"""
	Fonction envoyant un poke normal
	"""
	global urlOpener
	page_amis_post = "ajax/poke_dialog.php?uid=" + ami  # + "&pokeback=0&ask_for_confirm=0&__a=1"
	
	# On prépare les données en POST
	donnees = urllib.urlencode({
		#"pokeback" : 0,
		#"__d" : 1,
		#"post_form_id" : "cee5b8ca9e5aecd437e569cf2224945e",
		#"lsd" : "",
		#"post_form_id_source" : "AsyncRequest",
		#"phstamp" : 16581651087687120112167,
		"uid" : ami,
		"ask_for_confirm" : 0,
		"fb_dtsg" : "AQAlLWxp",
		"__user" : utilisateur["id"]
		})
	
	# On prépare la requête
	requete = urllib2.Request(site_web + page_amis_post, donnees)
	
	# On envoie la requete
	urlOpener.open(requete)


def usage() :
	"""
	Fonction detaillant l'usage de la commande
	"""
	print("Utilisation : foke.py [OPTION]")
	print("Options :")
	for option in liste_option.items() :
		print("\t{0}\t\t{1}".format(option[0],option[1]))
	sys.exit(1)


################################################################################
# Fonction principale							       #

# Parametre
nom_script = os.path.split(sys.argv[0])[1]
nom_conf = os.path.splitext(nom_script)[0] + ".conf"
nom_cookies = os.path.splitext(nom_script)[0] + ".cookie"
liste_option = {
	"pokeurs" : "poke les amis qui vous ont poké.",
	"tous" : "poke tous vos amis."
	}

cj = cookielib.LWPCookieJar()
urlOpener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
site_web = "https://www.facebook.com/"

page_pokes = "pokes"
regex_pokeur = re.compile("\/ajax\/pokes\/poke_inline\.php\?uid=([0-9]+)")

page_amis = "friends"
regex_ami = re.compile("\/ajax\/hovercard\/user\.php\?id=([0-9]+)")

utilisateur = {}

# On recupère le mode d'attaque
try : option = sys.argv[1]
except IndexError : usage()
if not liste_option.has_key(option) : usage()

# On s'identifie sur facebook
print("Authentification...")
try : cj.load(nom_cookies)
except IOError : pass

utilisateur["id"],utilisateur["pseudo"] = authentification()

# On attaque les pokeurs
if option == "pokeurs" :
	
	# On récupére la liste des pokeurs
	print("Le script analyse qui vous à poké...")
	liste_ami = analyse(page_pokes, regex_pokeur)

	# On poke tout le monde
	if liste_ami :
		print("Le script va poker {0} personne(s) en retour...".format(len(liste_ami)))
		for ami in liste_ami :
			repoke(ami)
			sys.stdout.write('.'); sys.stdout.flush()
	
	# Ou personne
	else :
		print("Personne ne vous à poké.")
		sys.exit(0)

# On attaque les innocents
elif option == "tous" :
	
	# On récupére la liste des amis
	print("Le script analyse qui sont vos amis...")
	liste_ami = analyse(utilisateur["pseudo"] + '/' + page_amis, regex_ami)
	
	# On poke tout le monde
	if liste_ami :
		print("Le script va poker {0} personne(s)...".format(len(liste_ami)))
		for ami in liste_ami :
			poke(ami)
			sys.stdout.write('.'); sys.stdout.flush()
		print
	
	# Ou personne
	else :
		print("Vous n'avez pas d'amis. Forever Alone ?")
		sys.exit(0)

# Movais paramêtre rentré
else :
	usage()

# On a fini, en enregistre nos cookies
print("C'est fait ! A bientôt.")
cj.save(nom_cookies)

# Fin									       #
################################################################################
