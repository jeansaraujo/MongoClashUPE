# -*- coding: utf-8 -*-
"""
Created on Sun Jul 28 09:08:46 2024
@authors: Flavio, David e Jean
"""

import requests
from pymongo import MongoClient

# Conexão com o MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['clash_royale']
players_collection = db['players']
battles_collection = db['battles']

# Função para buscar dados de jogadores
def fetch_player_data(player_tag):
    url = f'https://api.clashroyale.com/v1/players/%23{player_tag}'
    headers = {
        'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6ImQ2YTg4MWJiLTEwZTItNDVmMS05N2UwLWI2ZjFhODg2N2ZmNSIsImlhdCI6MTcyMjE5OTU2MSwic3ViIjoiZGV2ZWxvcGVyLzQyYTVjNDQwLWJmYzgtZjVhNS1kNzczLWE1ZjhjNzFlMTYwMCIsInNjb3BlcyI6WyJyb3lhbGUiXSwibGltaXRzIjpbeyJ0aWVyIjoiZGV2ZWxvcGVyL3NpbHZlciIsInR5cGUiOiJ0aHJvdHRsaW5nIn0seyJjaWRycyI6WyIxNzcuMTIuMjI3Ljk4Il0sInR5cGUiOiJjbGllbnQifV19.KSUDLuGua2cdLzife-EatfJ8dn4feSg9xaF_qgsgrNoskphwYBwHz9Pn1BUhGX_aSjXa2YdHANnRWYaQwZfiEQ'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to retrieve player data for tag {player_tag}: {response.status_code}")
        return None

# Função para buscar dados de batalhas
def fetch_battle_data(player_tag):
    url = f'https://api.clashroyale.com/v1/players/%23{player_tag}/battlelog'
    headers = {
        'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6ImQ2YTg4MWJiLTEwZTItNDVmMS05N2UwLWI2ZjFhODg2N2ZmNSIsImlhdCI6MTcyMjE5OTU2MSwic3ViIjoiZGV2ZWxvcGVyLzQyYTVjNDQwLWJmYzgtZjVhNS1kNzczLWE1ZjhjNzFlMTYwMCIsInNjb3BlcyI6WyJyb3lhbGUiXSwibGltaXRzIjpbeyJ0aWVyIjoiZGV2ZWxvcGVyL3NpbHZlciIsInR5cGUiOiJ0aHJvdHRsaW5nIn0seyJjaWRycyI6WyIxNzcuMTIuMjI3Ljk4Il0sInR5cGUiOiJjbGllbnQifV19.KSUDLuGua2cdLzife-EatfJ8dn4feSg9xaF_qgsgrNoskphwYBwHz9Pn1BUhGX_aSjXa2YdHANnRWYaQwZfiEQ'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to retrieve battle data for tag {player_tag}: {response.status_code}")
        return None


'''
# TESTE PARA VERIFICAR OS DADOS DAS BATALHAS
player_tag = '9JPL980Y2'
battle_data = fetch_battle_data(player_tag)
print(battle_data)
'''

# Função para inserir dados de jogadores e batalhas no MongoDB
def insert_data(player_tags):
    print("---------------------------------------------")
    print("INSERINDO OS DADOS PLAYER E BATTLE")
    print("---------------------------------------------")

    for tag in player_tags:
        print(f"Iniciando a coleta de dados para o jogador com tag: {tag}")
        player_data = fetch_player_data(tag)
        if player_data:
            players_collection.insert_one(player_data)
            #print(f"Dados do jogador {tag} inseridos com sucesso.")
            print("Dados player inseridos com sucesso.")
        else:
            print(f"Falha ao obter dados para o jogador {tag}.")        
        
    
        battle_data = fetch_battle_data(tag)
        if battle_data:
            if isinstance(battle_data, list) and len(battle_data) > 0:
                battles_collection.insert_many(battle_data)
                #print(f"Dados de batalhas para o jogador {tag} inseridos com sucesso.")
                print("Dados battle inseridos com sucesso.")
            elif 'items' in battle_data and len(battle_data['items']) > 0:
                battles_collection.insert_many(battle_data['items'])
                print(f"Dados de batalhas para o jogador {tag} inseridos com sucesso.")
            else:
                print(f"Falha ao obter dados de batalhas para o jogador {tag} ou nenhum dado disponível.")
        else:
            print(f"Falha ao obter dados de batalhas para o jogador {tag} ou nenhum dado disponível.")
        print("---------------------------------------------")