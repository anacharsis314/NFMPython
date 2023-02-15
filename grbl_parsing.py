import re
import unittest

def parse_msg(msg: str) -> str:
    """
    Funcao que processa as mensagen so GRBL, ainda só o minimo e algumas coisas que sao usadas para testar.
    O objetivo principal é processar as mensagens do estado do GRBL para ver quando ele para e onde esta.
    
    Entrada: String da mensagem
    Saida: String de saida
    """
    # Dicionario com as patterns que vamos procurar
    patterns = {'error':'(^error:[0-9]*)',
                'state' : r'(?<=\<)([a-zA-Z]*?)(?=\|)|(?<=\<)(.*?)(?=\:)',
                'status_report' : r'(\<)(.*)(\>)',
                'ok' : 'ok'
                }
    msg = str.strip(msg)
    
    #passa por todas as patterns e retorna quando achar uma (se tudo estiver certo só vai ter um match)
    for p in patterns.items():
        msgtype, pattern = p
        msgmatch = re.search(pattern, msg)
        if msgmatch:
            return msgmatch.group(0)
        else:
            continue
    return "não implementado ou erro"

def get_mpos(msg):
    pattern = r'(?<=(?:MPos:))(.*?)(?=\|)'
    match = re.search(pattern,msg)
    x, y, z = [float(n) for n in match.group(0).split(',')]
    return (x, y, z)


# Classe com testes. Se executar esse arquivo sozinho eles vao ser rodados.
class GrblMsgProcessor(unittest.TestCase):
    def setUp(self):
        self.alarm = '<Alarm|MPos:0.000,0.000,0.000|F:0|WCO:-486.000,-591.000,-98.000>'
        self.idle  = '<Idle|MPos:0.000,0.000,0.000|F:0|WCO:-486.000,-591.000,-98.000>'
        self.hold  = '<Hold:0|MPos:-437.000,-398.000,-98.000|F:0>'
        self.errormsg     = 'error:10'

    def test_status_report(self):
        self.assertEqual(parse_msg(self.alarm), 'Alarm')
        self.assertEqual(parse_msg(self.hold), 'Hold')
        self.assertEqual(parse_msg(self.idle),  'Idle')
        self.assertNotEqual(parse_msg(self.idle), None)

        
    def test_error(self):
        self.assertEqual(parse_msg(self.errormsg),'error:10')
        self.assertNotEqual(parse_msg(self.errormsg),'Idle')

    def test_mpos(self):
        self.assertEqual(get_mpos(self.hold),(-437.0,-398.0,-98.00))

# Se o arquivo for rodado sozinho, roda os testes
if __name__ == '__main__':
    unittest.main()
