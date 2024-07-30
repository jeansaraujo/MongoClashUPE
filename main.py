# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 12:47:29 2024
@authors: Flavio, David e Jean
"""

from MongoClashUPE._database import insert_data
from queries import (
    list_existing_cards, get_date_range_all_battles, get_date_range_from_db,
    victory_defeat_percentage, decks_with_high_win_rate, defeats_with_combo,
    victories_with_conditions, combo_win_rate, average_battle_duration,
    most_used_cards_in_wins, battles_won_without_card
)

# Lista de tags de jogadores públicos
player_tags = ['9JPL980Y2','RPURG9GR','2GYRQJRR8']
#player_tags = ['2P0LYQ', '82RLCVCC','929URQCL8','929URQCL8', 'RC2JGVVG', '9JPL980Y2', 'YU8R0VPP', 'RPURG9GR', '2GYRQJRR8']

# TESTAR
#player_tags = ['2Q9JG29RL','2LJ0ULYCC','Y9R22RQ2']

# Inserir dados de jogadores e batalhas no MongoDB
insert_data(player_tags)

# Exibindo as cartas existentes nas batalhas
print("CARTAS EXISTENTES NAS BATALHAS (QTD de vezes utilizadas):")
print("---------------------------------------------")
list_existing_cards()

'''
print("---------------------------------------------")
print("INTERVALO DE DATAS DE TODAS AS BATALHAS REALIZADAS:")
print(get_date_range_all_battles())
print("---------------------------------------------")
'''

print("---------------------------------------------")
print("INTERVALO DE DATAS DE TODAS AS BATALHAS REALIZADAS:")
result = get_date_range_all_battles()
if 'error' in result:
    print(result['error'])
else:
    print(f"Data mais antiga: {result['earliest_date']}")
    print(f"Data mais recente: {result['latest_date']}")
print("---------------------------------------------")

# Executar as consultas
print("---------------------------------------------")
print("INICIANDO AS CONSULTAS")
print("---------------------------------------------")

# Obter o intervalo de datas das batalhas no formato da base de dados
date_range = get_date_range_from_db()
if 'error' in date_range:
    print(date_range['error'])
else:
    start_date = date_range['earliest_date']
    end_date = date_range['latest_date']
#print(start_date) # 20240522T233455.000Z
#print(end_date)   # 20240729T054020.000Z


print("1. Porcentagem de vitórias e derrotas utilizando a carta Fireball:")
print(victory_defeat_percentage('Fireball', start_date, end_date))

print("\n2. Decks completos que produziram mais de 70% de vitórias:")
#print(decks_with_high_win_rate(70, start_date, end_date))
decks_with_high_win_rate(70, start_date, end_date)


print("\n3. Quantidade de derrotas utilizando o combo de cartas (Phoenix, The Log):")
combo = ['Phoenix', 'The Log']
defeats_with_combo(combo, start_date, end_date)


print("\n4. Vitórias envolvendo a carta Ice Spirit com condições específicas:")
print("Condição 1: Vitórias envolvendo a carta Ice Spirit.")                        # Cartas
print("Condição 2: O vencedor possui 10% menos troféus do que o perdedor.")         # Trofeus
print("Condição 3: A partida durou menos de 2 minutos.")                            # Duracao
print("Condição 4: O perdedor derrubou ao menos duas torres do adversário.")        # Torres
#print(victories_with_conditions('Ice Spirit', 20, start_date, end_date))
victories_with_conditions('Ice Spirit', 10, 2)


print("\n5. Combos de cartas de tamanho 3 com mais de 60% de vitórias:")
print(combo_win_rate(3, 60, start_date, end_date))

print("\n6. Média de duração das batalhas que utilizam a carta Knight:")
print(average_battle_duration('Knight', start_date, end_date))
    
print("\n7. Cartas mais utilizadas em vitórias com mais de 4000 troféus:")
print(most_used_cards_in_wins(4000))

print("\n8. Quantidade de batalhas vencidas com decks sem carta Lightning:")
print(battles_won_without_card('Lightning'))
