EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title "OwlSat Solar Panel (X/Y/Z no RBF)"
Date "2021-08-12"
Rev "4.0"
Comp "SEDS Rice"
Comment1 "This schematic works for panels of all faces except for the panel with the RBF pin."
Comment2 "See \"OwlSat Solar Panel (X/Y with RBF) for schematic of panel with RBF pin."
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L OwlSat_Symbols:Spectrolab_XTE-SF_Solar_Cells U2
U 1 1 6115468C
P 5525 5550
F 0 "U2" H 6153 5929 50  0000 L CNN
F 1 "Spectrolab_XTE-SF_Solar_Cells" H 6153 5838 50  0000 L CNN
F 2 "Battery:Spectrolab_XTE-SF_Solar_Cell" H 5525 5550 50  0001 C CNN
F 3 "" H 5525 5550 50  0001 C CNN
	1    5525 5550
	1    0    0    -1  
$EndComp
$Comp
L OwlSat_Symbols:Spectrolab_XTE-SF_Solar_Cells U1
U 1 1 611554CA
P 5525 2650
F 0 "U1" H 6153 3029 50  0000 L CNN
F 1 "Spectrolab_XTE-SF_Solar_Cells" H 6153 2938 50  0000 L CNN
F 2 "Battery:Spectrolab_XTE-SF_Solar_Cell" H 5525 2650 50  0001 C CNN
F 3 "" H 5525 2650 50  0001 C CNN
	1    5525 2650
	-1   0    0    1   
$EndComp
$Comp
L OwlSat_Symbols:PicoBlade_Connector U3
U 1 1 6115C32C
P 6750 4375
F 0 "U3" H 6472 4143 50  0000 R CNN
F 1 "PicoBlade_Connector" H 6472 4052 50  0000 R CNN
F 2 "Connector_Molex:Molex_PicoBlade_53261-0471_1x04-1MP_P1.25mm_Horizontal" H 6750 4375 50  0001 C CNN
F 3 "" H 6750 4375 50  0001 C CNN
	1    6750 4375
	-1   0    0    1   
$EndComp
Wire Wire Line
	5025 3350 5025 3975
Wire Wire Line
	5025 3975 5425 3975
Wire Wire Line
	5425 3350 5425 3975
Connection ~ 5425 3975
Wire Wire Line
	5425 3975 5625 3975
Wire Wire Line
	6025 3350 6025 3975
Connection ~ 6025 3975
Wire Wire Line
	5025 4850 5025 3975
Connection ~ 5025 3975
Wire Wire Line
	5625 4850 5625 3975
Connection ~ 5625 3975
Wire Wire Line
	5625 3975 6025 3975
Wire Wire Line
	6025 4850 6025 3975
Wire Wire Line
	6575 3975 6575 3925
Wire Wire Line
	6575 3925 6650 3925
Wire Wire Line
	6025 3975 6575 3975
Wire Wire Line
	6575 3975 6575 4025
Wire Wire Line
	6575 4025 6650 4025
Connection ~ 6575 3975
Wire Wire Line
	6650 4225 6575 4225
Wire Wire Line
	6575 4225 6575 4175
Wire Wire Line
	6575 4125 6650 4125
Wire Wire Line
	5425 4850 5425 4175
Connection ~ 6575 4175
Wire Wire Line
	6575 4175 6575 4125
Wire Wire Line
	5625 3350 5625 3925
Wire Wire Line
	5625 3925 5675 3925
Wire Wire Line
	5675 3925 5675 4175
Wire Wire Line
	5425 4175 5675 4175
Wire Wire Line
	5675 4175 6575 4175
Connection ~ 5675 4175
$EndSCHEMATC
