import cv2
import numpy as np
import HandTrackingModule as htm
import math

#control volume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

#configuração da camera

############################################################
wCam, hCam = 640, 480
#wCam, hCam = 1200, 600
############################################################

camera = 0 #1

cap = cv2.VideoCapture(camera)

cap.set(3, wCam) #tamanho horizontal
cap.set(4, hCam) #tamanho vertical

detector = htm.handDetector(detectionCon=0.7, maxHands=1)

#configurando o alto-falante com a biblioteca pycaw
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

print(volume.GetVolumeRange())

#descobrindo a faixa de volume entre o mínimo e o máximo
volRange = volume.GetVolumeRange()

minVol = volRange[0]
maxVol = volRange[1]

vol = -20.0
volBar = 318 #360
volPerc = 20

#capturar a imagem da camera e detectar a mão
while True:

    success, img = cap.read()

    img = detector.findHands(img)

    #captura o posicionamento da mão
    lmList = detector.findPosition(img, draw=False)

    if len(lmList) != 0:

        #coordenadas da mão que iremos utilizar para controlar o volume
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]

        cv2.circle(img, (x1, y1), 15, (255,0,255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)

        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)

        lengh = math.hypot(x2 - x1, y2 - y1)

        #coordenadas para ativar o sistema ou não

        #dedo do meio
        x3, y3 = lmList[12][1], lmList[12][2] 
        x4, y4 = lmList[9][1], lmList[9][2]

        lengh_dedo_meio = math.hypot(x4 - x3, y4 - y3)

        #print(lengh_dedo_meio)

        texto1 = 'Desativado'
        texto2 = 'Abaixado'


        if(lengh_dedo_meio>100):

            texto1 = 'Ativado'
            texto2 = 'Levantado' 

            vol = np.interp(lengh, [50, 300], [minVol, maxVol])
            volBar = np.interp(lengh, [50, 300], [360, 150])
            volPerc = np.interp(lengh, [50, 300], [0, 100])

            #print("volBar: ", volBar)

            #print("volPerc: ", round(volPerc))

            #volume.SetMasterVolumeLevel(vol, None)
            volume.SetMasterVolumeLevelScalar(volPerc / 100, None)
            #print(int(lengh), vol)

        cv2.putText(img, f'Sistema {texto1} (Dedo {texto2})', (50,45), (cv2.FONT_HERSHEY_SIMPLEX), 1, (0, 0, 0), 5)


    else:
        # seta um volume padrão é o ultimo volume feito pelo movimento das mãos
        #volume.SetMasterVolumeLevel(vol, None)
        volume.SetMasterVolumeLevelScalar(volPerc / 100, None)

    cv2.rectangle(img, (50, 150), (85, 360), (255,0,0), 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 360), (0, 255, 0), cv2.FILLED)

    cVol = round(volume.GetMasterVolumeLevelScalar() * 100) # mostra volume do windows
    cv2.putText(img, f'Vol: {cVol}', (40, 400), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)

    cv2.imshow("img", img)

    k = cv2.waitKey(1) & 0xFF

    if k == 27 or k == 13:
        break
