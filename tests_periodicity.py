# Description: This file contains the functions to map the periodicity of the tests for each equipment.

def map_gc_periodicity(name):
    list_tests_gc_periodicity = {
                'Uniformidade intrínseca para alta densidade de contagem': 'Mensal',
                'Resolução e linearidade espacial intrínseca': 'Mensal',
                'Centro de rotação LEHR': 'Mensal',
                'Centro de rotação MEGP': 'Mensal',
                'Centro de rotação HEGP': 'Mensal',
                'Resolução energética Tc-99m': 'Semestral',
                'Resolução energética Tl-201': 'Semestral',
                'Resolução energética Ga-67': 'Semestral',
                'Resolução energética I-131': 'Semestral',
                'Taxa máxima de contagem': 'Semestral',
                'Resolução espacial íntriseca para fontes multi-energética I-131': 'Semestral',
                'Resolução espacial íntriseca para fontes multi-energética Ga-67': 'Semestral',
                'Resolução espacial íntriseca para fontes multi-energética Tl-201': 'Semestral',
                'Corregistro espacial para fontes multi-energéticas Ga-67': 'Semestral',
                'Corregistro espacial para fontes multi-energéticas Tl-201': 'Semestral',
                'Sensibilidade planar Tc-99m': 'Semestral',
                'Sensibilidade planar Ga-67': 'Semestral',
                'Sensibilidade planar I-131': 'Semestral',
                'Sensibilidade planar Tl-201': 'Semestral',
                'Uniformidade extrínseca para alta densidade de contagem LEHR': 'Semestral',
                'Uniformidade extrínseca para alta densidade de contagem MEGP': 'Semestral',
                'Uniformidade extrínseca para alta densidade de contagem HEGP': 'Semestral',
                'Verificação da angulação dos furos LEHR': 'Semestral',
                'Verificação da angulação dos furos MEGP': 'Semestral',
                'Verificação da angulação dos furos HEGP': 'Semestral',
                'Velocidade da mesa em varreduras de corpo inteiro': 'Semestral',
                'Desempenho geral da câmara SPECT': 'Semestral',
                'Uniformidade íntrinseca para I-131': 'Anual',
                'Uniformidade íntrinseca para Ga-67': 'Anual',
                'Uniformidade íntrinseca para Tl-201': 'Anual',
                'Uniformidade intrínseca com janelas energéticas assimétricas': 'Anual',
                'Resolução e linearidade espacial extrínseca LEHR': 'Anual',
                'Resolução e linearidade espacial extrínseca MEGP': 'Anual',
                'Resolução e linearidade espacial extrínseca HEGP': 'Anual'
            }
    
    return list_tests_gc_periodicity[name]

def map_pet_periodicity(name):
    list_tests_pet_periodicity = {
                'Uniformidade e verificação da calibração do sistema PET-CT': 'Mensal',
                'Normalização e Calibração cruzada': 'Trimestral',
                'Resolução espacial': 'Semestral',
                'Sensibilidade': 'Semestral',
                'Corregistro das imagens de PET e CT': 'Semestral',
                '''Desempenho da taxa de contagens (NECR), 
                taxa de eventos aleatórios, espalhados e verdadeiros, 
                fração de espalhamento e 
                exatidão das correções de eventos aleatórios e de perda de contagens''': 'Anual',
                'Desempenho geral e exatidão das correções de atenuação e espalhamento': 'Anual',
            }
    return list_tests_pet_periodicity[name]

def map_curiometro_periodicity(name):
    list_tests_curiometro_periodicity = {
                'Reprodutibilidade': 'Mensal',
                'Precisão e exatidão': 'Semestral',
                'Linearidade': 'Semestral',
                'Geometria': 'Anual'
            }
    return list_tests_curiometro_periodicity[name]

def map_gm_periodicity(name):
    list_tests_gm_periodicity = {
                'Reprodutibilidade': 'Mensal'
            }
    return list_tests_gm_periodicity[name]

def map_gp_periodicity(name):
    list_tests_gp_periodicity = {
                'Repetibilidade': 'Semestral'
            }
    return list_tests_gp_periodicity[name]