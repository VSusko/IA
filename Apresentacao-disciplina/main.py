from random import *
import matplotlib.pyplot as plt
import numpy as np

# Vetor que armazenará os valores para a simulação dos consumos diários
consumos = []
# São gerados 20 valores entre 200KWh e 400KWh
for i in range(20): 
  consumos.append(randint(200, 400))
  
# Vetor que armazenará os valores para a simulação do preço do KWh
precos = []
# São gerados 20 valores entre R$0.50 e R$2.00
for i in range(20): 
  precos.append(0.5 + 1.5 * random())

# Definicao da classe ambiente
class Ambiente():

  def __init__(self):
    # Ambiente explorado pelo agente de compra de papel higienico
    self.num_dias=0                       # Valor do numero de dias
    self.estoque=300                      # Valor do estoque inicial
    self.historico_preco=[1.5]            # Lista do estoque de preços
    self.historico_estoque=[self.estoque] # Lista do historico de estoques
    self.historico_qtde_comprados=[0]     # Lista da quantidade de produtos comprados

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
    qtde_consumidos = consumos[iteracao] # novo valor da quantidade consumida
    print(f"Consumo realizado no dia: {qtde_consumidos}")
    estoque_atual = self.historico_estoque[len(self.historico_estoque)-1] - qtde_consumidos + dic_acoes["comprar"]
    print(f"Estoque final após consumo e compra: {estoque_atual}")
    
    self.historico_estoque.append(estoque_atual) # Adicionando o estoque atual no histórico
    self.historico_qtde_comprados.append(dic_acoes["comprar"]) # Adicionando quantidade de carga comprada no histórico

    # Informando valor do produto no periodo (Atualizacao para o proximo dia)
    valor = precos[iteracao] # novo valor do produto, obtido pelo vetor de precos.
    self.historico_preco.append(valor)
    print(f"Novo valor do preço: {valor}")


# Definição da classe agente

class Agente():
  
  def __init__(self, ambiente):
    self.num_dias = 1
    self.ambiente= ambiente
    self.estoque= ambiente.percebe_estoque()
    self.total_gasto = 0
    self.preco_atual = self.media = ambiente.percebe_preco_atual()

  def executa_agente(self, media_movel, qtde_dias=20):
    
    for i in range(qtde_dias): 
      # O agente percebe o estado do ambiente
      print(f"Dia: {i+1}")
      self.estoque= self.ambiente.percebe_estoque()
      self.preco_atual= self.ambiente.percebe_preco_atual()
      
      '''
        Controlador do agente:
        - Define a regra para compra de produtos
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

      self.num_dias+=1
      if media_movel and self.num_dias > 5:
        self.media = (self.media*(5) + self.preco_atual - self.ambiente.historico_preco[(self.num_dias - 1) - 5])/5
      else:
        self.media = (self.media*(self.num_dias-1) + self.preco_atual)/self.num_dias
        
      print(f"Media atual = {self.media}")
      
      print(f"\n")
      if self.estoque <= 0 and i >= 1:
        print(f"Total de dias simulados: {i+1}")
        break
      
      if i == qtde_dias:
        print(f"Total de dias simulados: {qtde_dias}")

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


ambiente_atuacao_simples = Ambiente()
smart_house_media_simples = Agente(ambiente_atuacao_simples)
smart_house_media_simples.executa_agente(False, 20)
print(f"Total gasto: {smart_house_media_simples.total_gasto}\n")
Imprime.imprime_resultado(smart_house_media_simples)

ambiente_atuacao_movel = Ambiente()
smart_house_media_movel = Agente(ambiente_atuacao_movel)
smart_house_media_movel.executa_agente(True, 20)
print(f"Total gasto: {smart_house_media_movel.total_gasto}")
Imprime.imprime_resultado(smart_house_media_movel)
 
