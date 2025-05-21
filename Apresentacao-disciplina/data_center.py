from random import *
import matplotlib.pyplot as plt
import numpy as np

# Definição das constantes
QTD_DIAS       = 100   # Quantidade de dias simulados
NUM_SIMULACOES = 2000  # Número total de simulações
MODO_IMPRESSAO = False # Define se serão mostrados os valores no terminal
CODIGO_MAIN    = 2     # Define qual main será executada: 1 para geração de gráficos e 2 para geração das estatísticas

# Função que gera um vetor de numeros entre 200 e 400 para o consumo diario
def gerar_consumos():
  # Vetor que armazenará os valores para a simulação dos consumos diários
  consumos = []
  # São gerados 20 valores entre 200KWh e 400KWh
  for i in range(QTD_DIAS): 
    consumos.append(randint(200, 400))
  return consumos

# Função que gera um vetor de numeros entre 0.5 e 2 para o preço do Kwh
def gerar_precos():
  # Vetor que armazenará os valores para a simulação do preço do KWh
  precos = []
  # São gerados 20 valores entre R$0.50 e R$2.00, mas existe uma chance de 10% de aparecer um preço de 7, ou seja, muito fora do padrão
  for i in range(QTD_DIAS): 
    if(randint(1, 25) == 1):
      precos.append(20)
    else:
      precos.append(0.5 + 1.5 * random())
      
  return precos

# Definicao da classe ambiente
class Ambiente():

  def __init__(self):
    # Ambiente explorado pelo agente de compra de papel higienico
    self.num_dias=0                       # Valor do numero de dias
    self.estoque=300                      # Valor do estoque inicial
    self.historico_preco=[1.5]            # Lista do estoque de preços
    self.historico_estoque=[self.estoque] # Lista do historico de estoques
    self.historico_qtde_comprados=[0]     # Lista da quantidade de produtos comprados
    self.precos_aleatorios = gerar_precos()     # Vetor do preco de cada dia
    self.consumos_aleatorios = gerar_consumos() # Vetor do consumo de cada dia

  # Função que retorna o preço atual do kwh
  def percebe_preco_atual(self):
    return self.historico_preco[len(self.historico_preco)-1]
  
  # Função que retorna o estoque atual
  def percebe_estoque(self):
    return self.historico_estoque[len(self.historico_estoque)-1]    

  # Função que simula o ambiente
  def run(self, dic_acoes, iteracao):
    '''Realizar alteracoes no ambiente: 
       Definir, aleatoriamente, uma quantidade de produtos consumidos
       Atualizar o historico do preco atual e do estoque.
       Essas informacoes serao utilizadas pelo agente para decidir a compra ou nao de produtos
    '''
    # Consumo realizado (valores gerados aleatoriamente)
    if MODO_IMPRESSAO:
      print(f"Estoque atual: {self.historico_estoque[len(self.historico_estoque)-1]}")
      print(f"Consumo realizado no dia: {self.consumos_aleatorios[iteracao]}") # novo valor da quantidade consumida
    estoque_atual = self.historico_estoque[len(self.historico_estoque)-1] - self.consumos_aleatorios[iteracao] + dic_acoes["comprar"]
    if MODO_IMPRESSAO:
      print(f"Estoque final após consumo e compra: {estoque_atual}")
    
    self.historico_estoque.append(estoque_atual)               # Adicionando o estoque atual no histórico
    self.historico_qtde_comprados.append(dic_acoes["comprar"]) # Adicionando quantidade de carga comprada no histórico

    # Informando valor do produto no periodo (Atualizacao para o proximo dia)
    self.historico_preco.append(self.precos_aleatorios[iteracao]) # novo valor do produto, obtido pelo vetor de precos.
    if MODO_IMPRESSAO:
      print(f"Novo valor do preço: {self.precos_aleatorios[iteracao]}")


# Definição da classe agente
class Agente():
  
  def __init__(self, ambiente):
    self.num_dias = 1                                               # Definição do número de dias
    self.ambiente= ambiente                                         # Copia do objeto ambiente
    self.estoque= ambiente.percebe_estoque()                        # Definição do estoque inicial
    self.total_gasto = 0                                            # Variável para armazenar a quantidade total gasta
    self.preco_atual = self.media = ambiente.percebe_preco_atual()  # Variável para o preço atual do Kwh

  # Função que executa o agente, decidindo ou não comprar mais cargas 
  def executa_agente(self, media_movel):
    
    # Loop principal
    for i in range(QTD_DIAS): 
      # O agente percebe o estado do ambiente
      if MODO_IMPRESSAO:
        print(f"Dia: {i+1}")

      self.estoque= self.ambiente.percebe_estoque()         # Obtenção do novo estoque
      self.preco_atual= self.ambiente.percebe_preco_atual() # Obtenção do novo preço
      
      '''
        Controlador do agente:
        - Define a regra para compra de produtos:
          Se a o preço estiver menor que a média, completar a bateria e comprar o consumo do dia
          
          Se o estoque estiver em caso muito crítico (<=100), comprar o consumo do dia + 200 de carga para a bateria
          
          Se o estoque estiver em caso crítico (<=200), comprar metade do consumo do dia + 100 de carga para a bateria

          Se o estoque estiver em caso moderado (<300), comprar um quarto do consumo do dia + 100 de carga para a bateria
          
          Caso contrário, não comprar nada
      '''
      if self.preco_atual < self.media:
        compra = self.ambiente.consumos_aleatorios[i] + 500 - self.estoque  
      elif self.estoque <= 100:
        compra = self.ambiente.consumos_aleatorios[i] + 200
      elif self.estoque <= 200:
        compra = (self.ambiente.consumos_aleatorios[i] / 2) + 100
      elif self.estoque < 300:
        compra = (self.ambiente.consumos_aleatorios[i] / 4) + 100
      else:
        compra = 0
      
      if MODO_IMPRESSAO:      
        print(f"Compra = {compra}")
      
      # Fim do controlador
      self.total_gasto += self.preco_atual*compra
      # O agente aplica modificacoes ao ambiente)
      self.ambiente.run({"comprar": compra}, i)
      # Aumentando o contador de dias
      self.num_dias+=1
      # Cálculo das médias: o primeiro caso representa a média móvel, e o segundo a média simples
      if media_movel and self.num_dias > 5:
        self.media = (self.media*(5) + self.preco_atual - self.ambiente.historico_preco[(self.num_dias - 1) - 5])/5
      else:
        self.media = (self.media*(self.num_dias-1) + self.preco_atual)/self.num_dias
      
      if MODO_IMPRESSAO:      
        print(f"Media atual = {self.media}")
        print(f"\n")
      
      # Se o estoque zerar, a simulação termina
      if self.ambiente.percebe_estoque() <= 0 and i > 1:
        return self.num_dias
      
    return self.num_dias
      

# Classe para a impressão dos gráficos
class Imprime:
  @staticmethod
  def imprime_resultado(agente):
    historico_dias = np.linspace(0, agente.num_dias, agente.num_dias)

    # Primeira impressão: historico do preco
    fig = plt.figure(figsize=(16,8))
    spec = fig.add_gridspec(1,3)

    axis1 = fig.add_subplot(spec[0,0])
    axis2 = fig.add_subplot(spec[0,1])
    axis3 = fig.add_subplot(spec[0,2])

    axis1.plot(historico_dias, agente.ambiente.historico_preco, 'b-', label='Historico (preço)')
    axis1.legend()

    # Segunda impressão: historico qtde itens comprados
    axis2.vlines(historico_dias, ymin=0, ymax=agente.ambiente.historico_qtde_comprados)
    axis2.plot(historico_dias, agente.ambiente.historico_qtde_comprados, "g-")
    axis2.set_ylim(0, 800)

    # Terceira impressão: historico do estoque
    axis3.plot(historico_dias, agente.ambiente.historico_estoque, 'r-', label='Historico (estoque)')
    axis3.legend()
    plt.show()

# =========================== MAIN PARA GERAÇÃO DE GRÁFICOS ===========================
if CODIGO_MAIN == 1:
  # Agente da média simples
  ambiente = Ambiente()
  smart_house_media_simples = Agente(ambiente)
  total_dias_simulados_simples = smart_house_media_simples.executa_agente(False)
  Imprime.imprime_resultado(smart_house_media_simples)

  # Reset do ambiente
  ambiente.num_dias=0                       
  ambiente.estoque=300                      
  ambiente.historico_preco=[1.5]            
  ambiente.historico_estoque=[ambiente.estoque] 
  ambiente.historico_qtde_comprados=[0] 

  # Agente da média móvel
  smart_house_media_movel = Agente(ambiente)
  total_dias_simulados_movel = smart_house_media_movel.executa_agente(True)
  Imprime.imprime_resultado(smart_house_media_movel)

  print(f"Total de dias simulados na média simples: {total_dias_simulados_simples}\n")
  print(f"Total gasto na média simples: {smart_house_media_simples.total_gasto}\n")
  print(f"Total de dias simulados na média móvel: {total_dias_simulados_movel}\n")
  print(f"Total gasto na média móvel: {smart_house_media_movel.total_gasto}\n")
  if smart_house_media_movel.total_gasto - smart_house_media_simples.total_gasto > 0:
    print(f"A média simples produziu menos gastos. A diferença dos gastos é: {smart_house_media_movel.total_gasto - smart_house_media_simples.total_gasto}")
  else:
    print(f"A média móvel produziu menos gastos. A diferença dos gastos é: {smart_house_media_simples.total_gasto - smart_house_media_movel.total_gasto}")


# =========================== MAIN PARA GERAÇÃO DE ESTATÍSTICAS ===========================
if CODIGO_MAIN == 2:
  metrica_media_simples_total_gasto = 0 # Variável que contabiliza quantas vezes a média simples produziu gastos menores
  metrica_media_movel_total_gasto = 0   # Variável que contabiliza quantas vezes a média móvel produziu gastos menores
  empate_total_gasto = 0 # Variável que contabiliza empate no dinheiro total gasto nas duas médias
  simulacoes = 0 # Número de simulacoes totais
  while True:
    # Agente da média simples
    ambiente = Ambiente()
    smart_house_media_simples = Agente(ambiente)
    total_dias_simulados_simples = smart_house_media_simples.executa_agente(False)

    # Se o numero de dias simulado for menor ou igual a 5, recomece
    if total_dias_simulados_simples < QTD_DIAS: 
      continue
    
    # Reset do ambiente
    ambiente.num_dias=0                       
    ambiente.estoque=300                      
    ambiente.historico_preco=[1.5]            
    ambiente.historico_estoque=[ambiente.estoque] 
    ambiente.historico_qtde_comprados=[0]     
    
    # Agente da média móvel
    smart_house_media_movel = Agente(ambiente)
    total_dias_simulados_movel = smart_house_media_movel.executa_agente(True)
    
    # Se o numero de dias for menor ou igual a 5, recomece
    if total_dias_simulados_movel < QTD_DIAS:
      continue
    
    if MODO_IMPRESSAO:
      print(f"Total de dias simulados: {QTD_DIAS}\n")
      print(f"Total gasto (media simples): {smart_house_media_simples.total_gasto}\n")
      print(f"Total gasto (media movel): {smart_house_media_movel.total_gasto}")
    
    ''' Se a media simples produziu menos gasto, o contador aumenta em 1 
        Se a media movel produziu menos gasto, o contador aumenta em 1
        Em caso de empate, nenhumas das duas aumenta e ele é contabilizado
    '''
    if smart_house_media_simples.total_gasto < smart_house_media_movel.total_gasto:
      metrica_media_simples_total_gasto += 1
    elif smart_house_media_simples.total_gasto > smart_house_media_movel.total_gasto:
      metrica_media_movel_total_gasto += 1
    else:
      empate_total_gasto += 1
    
    # Aumento do numero de simulacoes
    simulacoes += 1
    
    if simulacoes == NUM_SIMULACOES:
      break

  print(f"Número de vezes em que a média simples gerou menos custo: {metrica_media_simples_total_gasto}\n")
  print(f"Número de vezes em que a média móvel gerou menos custo: {metrica_media_movel_total_gasto}\n")
  print(f"Número de empates do custo: {empate_total_gasto}\n")

  print(f"A média simples faz com que o Data Center tenha menos despesas em {metrica_media_simples_total_gasto/NUM_SIMULACOES*100:.2f}% dos casos\n")
  print(f"A média móvel faz com que o Data Center tenha menos despesas em {metrica_media_movel_total_gasto/NUM_SIMULACOES*100:.2f}% dos casos\n")
  print(f"As duas médias são iguais quanto às despesas do Data Center em {empate_total_gasto/NUM_SIMULACOES*100:.2f}% dos casos\n")