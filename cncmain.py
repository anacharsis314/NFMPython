## Autores: Frederico Ferreira Alves Pinto para o Maglab (2022), Dalton (2022 - 2023)
import time
import serial
import numpy as np
from grbl_parsing import parse_msg, get_mpos
from sadevice.sa_api import *
import matplotlib.pyplot as plt
import seaborn as sns; sns.set() # styling
import os
import pandas as pd

def zigzag(x0:int, x1:int, y0:int, y1:int, z0:int, z1:int, step:int, zstep:int)->str:
    """
    Funcao que recebe os dois pontos, um passo no plano xy e um passo em z e retorna uma string com instrucoes
    de g-code para movimento linear e paradas em cada ponto da grade. A grade e coberta de forma zigzag para minimizar o movimento.

    Inputs: x0, x1, y0, y1, z0, z1, step, zstep : Int
    Outputs: String
    """
    stop_instruction = 'M00\n'
    inst ='g00x0f500\n'
    for z in range(z0,z1+1,zstep):
        # move x 2n, pois vamos iterar x dentro do loop tambem (zig)
        for x in range(x0, x1+1, step * 2):
            # Move Y
            for y in range(y0, y1+1,step):
                inst += (f'G01 X{x} Y{y} Z{z}\n')
                inst += stop_instruction

            # Move para o lado, restringe para [x0,x1]
            x = min(x + step, x1)

            # Move para baixo (zag)
            for y in reversed(range(y0, y1+1, step)):
                inst += (f'G01 X{x} Y{y} Z{z}\n')
                inst += stop_instruction
    return inst



def send_instruction(device,inst,nl=False):
    if nl:
        device.write(bytes((inst+'\n'),"ascii"))
    else:
        device.write(bytes((inst),"ascii"))
########
# Open device
handle = sa_open_device()["handle"]

# Configure device
sa_config_center_span(handle, 515e6, 970e6)
sa_config_level(handle, 0)
sa_config_sweep_coupling(handle, 250e3, 250e3, 0)
sa_config_acquisition(handle, SA_MIN_MAX, SA_LOG_SCALE)

# Initialize
sa_initiate(handle, SA_SWEEPING, 0)
query = sa_query_sweep_info(handle)
sweep_length = query["sweep_length"]
start_freq = query["start_freq"]
bin_size = query["bin_size"]
freqs = [start_freq + i * bin_size for i in range(sweep_length)]

def sweep():


    # Get sweep
    sweep_max = sa_get_sweep_32f(handle)["max"]
    return sweep_max

    # Device no longer needed, close it
##    sa_close_device(handle)

    # Plot
##    freqs = [start_freq + i * bin_size for i in range(sweep_length)]
    return
##    plt.plot(freqs, sweep_max)
##    plt.show()


########
#iniciar conexão serial
s = serial.Serial(port='COM4', baudrate=115200, timeout=1)
s.flushInput()  
time.sleep(1)
send_instruction(s,"\r\n")
time.sleep(1)
print(s.readline().decode('ascii'))

###ciclo de homing
send_instruction(s,'$H\n')
time.sleep(1)
##block até receber Home
homed = False
homing_time = 0.0
while not homed:
    send_instruction(s,'?')
    homing_time += 0.2
    print("Esperando o home..." + str(homing_time))

    if s.in_waiting <= 0:
        time.sleep(0.2)
        
    else:
        msg = s.readline().decode('ascii').strip()
        msg = parse_msg(msg)
        if msg =='Home' or msg=='Idle':
            homed=True
#gera as instrucoes para o caminho             
##instructions = ['G01X50F500','M00','G01Y50','M00','G01X10']
instructions = zigzag(50,350,50,350,0,25,75,25)
s.flushInput()  
time.sleep(1)
df = pd.DataFrame()
## Loop mandar instrucoes, esperar idle ou hold, repeat...
for instruction in instructions.split(sep='\n'):
    paused = False
    print('mandando: ' + instruction)
    send_instruction(s,instruction, nl=True)
    msg = s.readline().decode('ascii').strip()
    if msg == '': msg = 'nada'
    print("Recebi " + msg + " apos mandar a instrução " + instruction)
    time.sleep(0.5)
    #bloqueia ate Hold, Idle ou Home
    while not paused:
        send_instruction(s,'?')
        #time.sleep(0.20)
        if s.in_waiting <= 1:
            time.sleep(0.2)
            
        else:
            msg = s.readline().decode('ascii').strip()
            parsed_msg = parse_msg(msg)
            if  parsed_msg == 'Hold':
                paused = True
                pos    = get_mpos(msg)
                x,y,z  = pos
                print('Recebi o estado Hold! Pos: ' + str(pos))
                data   = sweep()
                fdata  = pd.DataFrame([data],columns = freqs)
                posdf  = pd.DataFrame([[x,y,z]], columns = ['x','y','z'])
                row    = pd.concat([posdf,fdata],axis=1)
                print(row)
                df     = pd.concat([df,row],axis=0)
                print(df)
                print('Continuando...')
                send_instruction(s,'~')
                s.flushInput()  

            elif parsed_msg == 'Idle':
                print('Detectei um Idle, vou mandar a proxima instrução')
                paused = True
                s.flushInput()  
            elif parsed_msg == 'Run':
                print('Movendo..')
                
            else:
                print('Isso estava no buffer: '+ msg + '\n')
df.to_csv(r"C:\Users\MagLab 1\Desktop\campoprox-python\medidas\1ghzadroaldo.csv",index=False)
freq = pd.DataFrame(freqs)
freq.to_csv("freqs.csv",index=False)
s.close()
sa_close_device(handle)
