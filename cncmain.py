import time
import serial
import numpy as np
from grbl_parsing import parse_msg, get_mpos

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

##def send_instruction(device,inst,nl=False,read=False):
##    """
##    Função que envia uma string [inst] pela porta serial para o dispositivo [device].
##    Se [nl], ela coloca uma '\n' no final, caso contrario não.
##    Se [read] ela espera 100ms e le o que tem na porta serial, caso contrario so manda a instrução
##    Inputs:
##        Device : Serial Handle
##        inst   : String
##        nl     : Bool
##    Outputs:
##        Se [read] ela retorna uma string, caso contrario não retorna nada.
##    """
##    if nl:
##        inst = inst + '\n'
##    else:
##        inst = inst
##    if read:
##        device.write(bytes(inst,'ascii'))
##        time.sleep(0.1)
##        return device.readline().decode('ascii')
##    else:
##        device.write(bytes(inst,'ascii'))

def send_instruction(device,inst,nl=False):
    if nl:
        device.write(bytes((inst+'\n'),"ascii"))
    else:
        device.write(bytes((inst),"ascii"))


########
#iniciar conexão serial
s = serial.Serial(port='/dev/ttyUSB0', baudrate=115200, timeout=1)
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
instructions = zigzag(300,400,300,400,10,10,10,1)
s.flushInput()  
time.sleep(1)
## Loop mandar instrucoes, esperar idle ou hold, repeat...
for instruction in instructions.split(sep='\n'):
    paused = False
    print('mandando: ' + instruction)
    send_instruction(s,instruction, nl=True)
    time.sleep(0.25)
    msg = s.readline().decode('ascii').strip()
    if msg == '': msg = 'nada'
    print("Recebi " + msg + " apos mandar a instrução " + instruction)
    time.sleep(0.5)
    
    #bloqueia ate Hold, Idle ou Home
    while not paused:
        send_instruction(s,'?')
        time.sleep(0.5)
        if s.in_waiting <= 1:
            time.sleep(0.2)
            
        else:
            msg = s.readline().decode('ascii').strip()
            parsed_msg = parse_msg(msg)
            if  parsed_msg == 'Hold':
                paused = True
                pos = get_mpos(msg)
                print('Recebi o estado Hold! Pos: ' + str(pos))
                time.sleep(1)
                print('Continuando...')
                send_instruction(s,'~')
                s.flushInput()  

            elif parsed_msg == 'Idle':
                print('Detectei um Idle, vou mandar a proxima instrução')
##                time.sleep(1)
                paused = True
                s.flushInput()  
            elif parsed_msg == 'Run':
                print('Movendo..')
                
            else:
                print('Isso estava no buffer: '+ msg + '\n')

s.close()
