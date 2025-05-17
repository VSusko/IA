from random import *
import matplotlib.pyplot as plt
import numpy as np

# Função que gera um vetor de numeros entre 200 e 400 para o consumo diario
def gerar_consumos(qtd_dias=20):
  # Vetor que armazenará os valores para a simulação dos consumos diários
  consumos = []
  # São gerados 20 valores entre 200KWh e 400KWh
  for i in range(qtd_dias): 
    consumos.append(randint(200, 400))
  return consumos

# Função que gera um vetor de numeros entre 0.5 e 2 para o preço do Kwh
def gerar_precos(qtd_dias=20):
  # Vetor que armazenará os valores para a simulação do preço do KWh
  precos = []
  # São gerados 20 valores entre R$0.50 e R$2.00
  for i in range(qtd_dias): 
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
    print(f"Estoque atual: {self.historico_estoque[len(self.historico_estoque)-1]}")
    print(f"Consumo realizado no dia: {self.consumos_aleatorios[iteracao]}") # novo valor da quantidade consumida
    estoque_atual = self.historico_estoque[len(self.historico_estoque)-1] - self.consumos_aleatorios[iteracao] + dic_acoes["comprar"]
    print(f"Estoque final após consumo e compra: {estoque_atual}")
    
    self.historico_estoque.append(estoque_atual)               # Adicionando o estoque atual no histórico
    self.historico_qtde_comprados.append(dic_acoes["comprar"]) # Adicionando quantidade de carga comprada no histórico

    # Informando valor do produto no periodo (Atualizacao para o proximo dia)
    self.historico_preco.append(self.precos_aleatorios[iteracao]) # novo valor do produto, obtido pelo vetor de precos.
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
  def executa_agente(self, media_movel, qtde_dias=20):
    
    # Loop principal
    for i in range(qtde_dias): 
      # O agente percebe o estado do ambiente
      print(f"Dia: {i+1}")
      self.estoque= self.ambiente.percebe_estoque()         # Obtenção do novo estoque
      self.preco_atual= self.ambiente.percebe_preco_atual() # Obtenção do novo preço
      
      '''
        Controlador do agente:
        - Define a regra para compra de produtos:
          Se o preço atual for menor que a média ou o estoque estiver abaixo de 100, são comprados 300Kwh.
          
          Se a soma do estoque atual com 300 for maior do que o limite superior do DataCenter (500Kwh),
          então será comprado a quantidade para completar o estoque.
      '''
      if (self.preco_atual < self.media) or (self.estoque <= 100):
        if (self.estoque + 300) <= 500: 
          compra= 300
        else:
          compra= 500 - self.estoque
      else:
        compra= 0
      
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
        
      print(f"Media atual = {self.media}")
      
      print(f"\n")
      # Se o estoque zerar, a simulação termina
      if self.estoque <= 0 and i >= 1:
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

    axis1.plot(historico_dias, agente.ambiente.historico_preco, 'bo--', label='Historico (preço)')
    axis1.legend()

    # Segunda impressão: historico qtde itens comprados
    axis2.vlines(historico_dias, ymin=0, ymax=agente.ambiente.historico_qtde_comprados)
    axis2.plot(historico_dias, agente.ambiente.historico_qtde_comprados, "go")
    axis2.set_ylim(0, 300)

    # Terceira impressão: historico do estoque
    axis3.plot(historico_dias, agente.ambiente.historico_estoque, 'rD--', label='Historico (estoque)')
    axis3.legend()
    plt.show()

# # Agente da média simples
# ambiente_atuacao_simples = Ambiente()
# smart_house_media_simples = Agente(ambiente_atuacao_simples)
# total_dias_simulados_simples = smart_house_media_simples.executa_agente(False, 20)
# print(f"Total de dias simulados: {total_dias_simulados_simples}\n")
# print(f"Total gasto: {smart_house_media_simples.total_gasto}\n")
# Imprime.imprime_resultado(smart_house_media_simples)

# # Agente da média móvel
# ambiente_atuacao_movel = Ambiente()
# smart_house_media_movel = Agente(ambiente_atuacao_movel)
# total_dias_simulados_movel = smart_house_media_movel.executa_agente(True, 20)
# print(f"Total de dias simulados: {total_dias_simulados_movel}\n")
# print(f"Total gasto: {smart_house_media_movel.total_gasto}")
# Imprime.imprime_resultado(smart_house_media_movel)

metrica_media_simples_dias = 0        # Variável que contabiliza quantas vezes a média simples durou mais tempo
metrica_media_simples_total_gasto = 0 # Variável que contabiliza quantas vezes a média simples produziu gastos menores
metrica_media_movel_dias = 0          # Variável que contabiliza quantas vezes a média móvel durou mais tempo
metrica_media_movel_total_gasto = 0   # Variável que contabiliza quantas vezes a média móvel produziu gastos menores
empate_total_gasto = 0 # Variável que contabiliza empate no dinheiro total gasto nas duas médias
empate_dias = 0 # Variável que contabiliza empate no número de dias das duas médias
simulacoes = 0 # Número de simulacoes totais
while True:
  # Agente da média simples
  ambiente = Ambiente()
  smart_house_media_simples = Agente(ambiente)
  total_dias_simulados_simples = smart_house_media_simples.executa_agente(False, 20)

  # Se o numero de dias simulado for menor ou igual a 5, recomece
  if total_dias_simulados_simples <= 5: 
    continue
  
  # Reset do ambiente
  ambiente.num_dias=0                       
  ambiente.estoque=300                      
  ambiente.historico_preco=[1.5]            
  ambiente.historico_estoque=[ambiente.estoque] 
  ambiente.historico_qtde_comprados=[0]     
  
  # Agente da média móvel
  smart_house_media_movel = Agente(ambiente)
  total_dias_simulados_movel = smart_house_media_movel.executa_agente(True, 20)
  
  # Se o numero de dias for menor ou igual a 5, recomece
  if total_dias_simulados_movel <= 5:
    continue
  
  print(f"Total de dias simulados (media simples): {total_dias_simulados_simples}\n")
  print(f"Total gasto (media simples): {smart_house_media_simples.total_gasto}\n")
  print(f"Total de dias simulados (media movel): {total_dias_simulados_movel}\n")
  print(f"Total gasto (media movel): {smart_house_media_movel.total_gasto}")
  
  ''' Se a media simples durou por mais tempo, o contador aumenta em 1 
      Se a media movel durou por mais tempo, o contador aumenta em 1
      Em caso de empate, nenhumas das duas aumenta e ele é contabilizado
  '''
  if total_dias_simulados_simples > total_dias_simulados_movel:
     metrica_media_simples_dias += 1
  elif total_dias_simulados_simples < total_dias_simulados_movel:
     metrica_media_movel_dias += 1
  else:
    empate_dias += 1
  
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
  
  if simulacoes == 2000:
    break

print(f"Métrica media simples dias: {metrica_media_simples_dias}\n")
print(f"Métrica media móvel dias: {metrica_media_movel_dias}\n")
print(f"Métrica empate em dias: {empate_dias}\n")
print(f"Métrica media simples total gasto: {metrica_media_simples_total_gasto}\n")
print(f"Métrica media móvel total gasto: {metrica_media_movel_total_gasto}\n")
print(f"Métrica empate em total gasto: {empate_total_gasto}\n")
    