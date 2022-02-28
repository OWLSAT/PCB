# -*- coding: utf-8 -*-

import empro.toolkit.adv as adv

def main():
	path=r"C:/Users/james/Desktop/OWLSAT_Antenna"
	lib=r"OWLSAT_Antenna_lib"
	subst=r"OWLSAT_Antenna_lib/Antenna.subst"
	substlib=r"OWLSAT_Antenna_lib"
	substname=r"Antenna"
	cell=r"Antenna"
	view=r"layout"
	libS3D=r"simulation/OWLSAT_Antenna_lib/%Antenna/_3%D%Viewer/extra/0/proj_libS3D.xml"
	varDictionary={}
	exprDictionary={}
	adv.loadDesign(path=path, lib=lib, subst=subst, substlib=substlib, substname=substname, cell=cell, view=view, libS3D=libS3D, var_dict=varDictionary, expr_dict=exprDictionary)
