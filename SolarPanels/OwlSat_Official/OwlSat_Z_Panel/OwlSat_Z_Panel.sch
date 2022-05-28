EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L OwlSat_Symbols:Spectrolab_XTE-SF_Solar_Cells U2
U 1 1 611D1AF6
P 5600 5225
F 0 "U2" H 6228 5604 50  0000 L CNN
F 1 "Spectrolab_XTE-SF_Solar_Cells" H 6228 5513 50  0000 L CNN
F 2 "Battery:Spectrolab_XTE-SF_Solar_Cell" H 5600 5225 50  0001 C CNN
F 3 "" H 5600 5225 50  0001 C CNN
	1    5600 5225
	1    0    0    -1  
$EndComp
$Comp
L OwlSat_Symbols:Spectrolab_XTE-SF_Solar_Cells U1
U 1 1 611D2A06
P 5600 2500
F 0 "U1" H 6228 2879 50  0000 L CNN
F 1 "Spectrolab_XTE-SF_Solar_Cells" H 6228 2788 50  0000 L CNN
F 2 "Battery:Spectrolab_XTE-SF_Solar_Cell" H 5600 2500 50  0001 C CNN
F 3 "" H 5600 2500 50  0001 C CNN
	1    5600 2500
	-1   0    0    1   
$EndComp
$Comp
L OwlSat_Symbols:PicoBlade_Connector U3
U 1 1 611D2D8F
P 6600 4175
F 0 "U3" H 6322 3851 50  0000 R CNN
F 1 "PicoBlade_Connector" H 6322 3942 50  0000 R CNN
F 2 "Connector_Molex:Molex_PicoBlade_53261-0471_1x04-1MP_P1.25mm_Horizontal" H 6600 4175 50  0001 C CNN
F 3 "" H 6600 4175 50  0001 C CNN
	1    6600 4175
	-1   0    0    1   
$EndComp
Wire Wire Line
	5100 3200 5100 3775
Wire Wire Line
	5100 3775 5500 3775
Wire Wire Line
	6425 3775 6425 3725
Wire Wire Line
	6425 3725 6500 3725
Wire Wire Line
	6500 3825 6425 3825
Wire Wire Line
	6425 3825 6425 3775
Connection ~ 6425 3775
Wire Wire Line
	5500 3200 5500 3775
Connection ~ 5500 3775
Wire Wire Line
	5500 3775 5700 3775
Wire Wire Line
	6100 3200 6100 3775
Connection ~ 6100 3775
Wire Wire Line
	6100 3775 6425 3775
Wire Wire Line
	5500 4525 5500 3975
Wire Wire Line
	6425 3975 6425 3925
Wire Wire Line
	6425 3925 6500 3925
Wire Wire Line
	6500 4025 6425 4025
Wire Wire Line
	6425 4025 6425 3975
Connection ~ 6425 3975
Wire Wire Line
	5500 3975 5800 3975
Wire Wire Line
	5700 4525 5700 3775
Connection ~ 5700 3775
Wire Wire Line
	5700 3775 6100 3775
Wire Wire Line
	6100 3775 6100 4525
Wire Wire Line
	5100 4525 5100 3775
Connection ~ 5100 3775
Wire Wire Line
	5700 3200 5700 3675
Wire Wire Line
	5700 3675 5800 3675
Wire Wire Line
	5800 3675 5800 3975
Connection ~ 5800 3975
Wire Wire Line
	5800 3975 6425 3975
$Comp
L OwlSat_Symbols:RBF_Pin U5
U 1 1 619A8EC7
P 4250 3575
F 0 "U5" H 4378 3413 50  0000 L CNN
F 1 "RBF_Pin" H 4378 3322 50  0000 L CNN
F 2 "Battery:RBF" H 4250 3575 50  0001 C CNN
F 3 "" H 4250 3575 50  0001 C CNN
	1    4250 3575
	1    0    0    -1  
$EndComp
$Comp
L OwlSat_Symbols:PicoBlade_2 U4
U 1 1 619A98BB
P 4000 4175
F 0 "U4" V 3946 4063 50  0000 L CNN
F 1 "PicoBlade_2" V 4037 4063 50  0000 L CNN
F 2 "Connector_Molex:Molex_PicoBlade_53261-0271_1x02-1MP_P1.25mm_Horizontal" H 4000 4175 50  0001 C CNN
F 3 "" H 4000 4175 50  0001 C CNN
	1    4000 4175
	0    -1   1    0   
$EndComp
Wire Wire Line
	4200 3875 4200 4075
Wire Wire Line
	4300 3875 4300 4075
$EndSCHEMATC
