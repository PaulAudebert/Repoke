#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re
import urllib, urllib2


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
			
			mot_de_passe = raw_input("Mot de passe : ")
			configuration.write(mot_de_passe + '\n')
	
	return utilisateur,mot_de_passe


def authentification(utilisateur, mot_de_passe) :
	"""
	Fonction devant recupèrer un cookie et un PHPSESSID
	"""
	http_entete["Referer"] = "https://www.facebook.com/"
	http_entete["Cookie"] = "datr=psASTyV9gyaudS_xpdQmoADW; locale=fr_FR; lu=gA_lOq1SwkC8V3gBRWrcViKw; lsd=jtag5; reg_fb_gate=https%3A%2F%2Fwww.facebook.com%2Findex.php%3Flh%3DAc8DA0zryFrNu82e; reg_fb_ref=https%3A%2F%2Fwww.facebook.com%2F; wd=1100x650"
	
	http_post_auth = urllib.urlencode({
		"post_form_id" : "73649afc8a832a17a4f4d9e7f6a6e253",
		"lsd" : "jtag5",
		"locale" : "fr_FR",
		"email" : utilisateur,
		"pass" : mot_de_passe,
		"persistent" : 0,
		"default_persistent" : 0,
		"charset_test" : "%E2%82%AC%2C%C2%B4%2C%E2%82%AC%2C%C2%B4%2C%E6%B0%B4%2C%D0%94%2C%D0%84",
		"timezone" : -60
	})

	try :
		requete = urllib2.Request(site, http_post_auth, http_entete)
		page = urllib2.urlopen(requete)
	
	except IOError, e:
		if hasattr(e, "reason"):
			print("Nous avons échoué à joindre le serveur.")
			print("Raison: " + e.reason)
		elif hasattr(e, "code"):
			print("Le serveur n'a pu satisfaire la demande.")
			print("Code d' erreur : " + e.code)
		
	return cookie,mon_id


def analyse(cookie, mon_id) :
	"""
	Fonction traitant la page des pokes
	"""
	lpokeur_id = []
	
	http_entete["Referer"] = "https://www.facebook.com/pokes",
	http_entete["Cookie"] = cookie					#"datr=UTYYT8qS2b5brAX2qKTsZvAP; locale=fr_FR; lu=RADRThl1IybM0VRy_Mfh3wdQ; s=Aa6YqfEivdzyAs-9; c_user=1557923085; csm=1; xs=61%3Aede4be6b8532156de78f7ad76520530e%3A1%3A1326986855; act=1327096937409%2F11%3A2; p=6; presence=EDvFA22A2EtimeF1327096929EstateFDutF1327096929606EvisF1EvctF0H0EblcF0EsndF1ODiFA21323617443A2C_5dEfFA21323617443A2EuctF1327096596EsF0CEchFDp_5f1557923085F46CC; _e_0uOL_3=%5B%220uOL%22%2C1327096937418%2C%22act%22%2C1327096937409%2C11%2C%22%2Fajax%2Fpokes%2Fpoke_inline.php%3Fuid%3D1323617443%26pokeback%3D1%22%2C%22click%22%2C%22click%22%2C%22pokes%22%2C%22r%22%2C%22%2Fpokes%22%2C%7B%22ft%22%3A%7B%7D%2C%22gt%22%3A%7B%7D%7D%2C402%2C141%2C0%2C981%2C16%5D; x-src=%2Fajax%2Fpokes%2Fpoke_inline.php%7Cpagelet_pokes"
	
	http_post_poke = urllib.urlencode({
		"pokeback" : 1,
		"nctr_mod" : "pagelet_pokes",
		"post_form_id" : "4f4bb272c36a12ec9f7da6f82bd6df1b",
		"fb_dtsg" : "AQAFx_yU",
		"lsd" : "",
		"post_form_id_source" : "AsyncRequest",
		"__user" : mon_id,
		"phpstamp" : 1658165701209512185168
	})
	
	# On se connecte à la page des pokes
	requete = urllib2.Request(site + api, http_post_auth, http_entete)
	try : page = urllib2.urlopen(requete)
	except IOError, e:
		if hasattr(e, "reason"):
			print("Nous avons échoué à joindre le serveur.")
			print("Raison: " + e.reason)
		elif hasattr(e, "code"):
			print("Le serveur n'a pu satisfaire la demande.")
			print("Code d\' erreur : " + e.code)
	
	# On lit la page ligne pas ligne
	with urlopen(api) as page :
		for ligne in page :
			
			# On recupère tous les id des amis
			lpokeur_id.extend(regex_id_ami.findall(ligne))
	
	return lpokeur_id


def poke(mon_id, pokeur_id) :
	print("poke de " + pokeur_id)


################################################################################
# Fonction principale							       #

# Parametre
nom_script = os.path.split(sys.argv[0])[1]
nom_conf = os.path.splitext(nom_script)[0] + ".conf"
site = "https://www.facebook.com"
api = "/pokes"
regex_id_ami = re.compile("ajaxify=\"\/ajax\/pokes\/poke_inline\.php\?uid=([0-9]+)\&amp;pokeback=1\"")
regex_id_moi = re.compile("\"user\":\"([0-9]+)\"")
http_entete = {
	"Host" : "www.facebook.com",
	#"User-Agent" : "Mozilla/5.0 (Ubuntu; X11; Linux x86_64; rv:9.0.1) Gecko/20100101 Firefox/9.0.1",
	"Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
	"Accept-Language" : "fr,fr-fr;q=0.8,en-us;q=0.5,en;q=0.3",
	"Accept-Encoding" : "gzip, deflate",
	"Accept-Charset" : "ISO-8859-1,utf-8;q=0.7,*;q=0.7",
	"DNT" : 1,
	"Connection" : "keep-alive",
	"X-SVN-Rev" : "497856",
	"Content-Type" : "application/x-www-form-urlencoded; charset=UTF-8",
	"Content-Length" : 199,
}

# Etape I : Authentification sur facebook
print("Authentification...")
utilisateur,mot_de_passe = mon_compte()
cookie,mon_id = authentification(utilisateur, mot_de_passe)

# Etape II : Récupération de la liste des pokeurs
print("Le script analyse qui vous à poké...")
lpokeur_id = analyse(cookie, mon_id)

# Etape III : On poke tout le monde
if lpokeur_id :
	print("Le script les poke en retour...")
	for pokeur_id in lpokeur_id :
		poke(mon_id, pokeur_id)
else :
	print("Personne à poker.")

print("C'est fait ! A bientôt.")

# Fin									       #
################################################################################
