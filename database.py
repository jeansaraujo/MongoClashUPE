# -*- coding: utf-8 -*-
"""
Created on Sun Jul 28 09:08:46 2024
Authors: Flavio, David e Jean
"""

import os
import requests
from pymongo import MongoClient
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Obter URI de conexão do MongoDB Atlas e Bearer token das variáveis de ambiente
MONGO_URI = os.getenv('MONGO_URI')
BEARER_TOKEN = os.getenv('BEARER_TOKEN')

# Conexão com o MongoDB Atlas
client = MongoClient(MONGO_URI)
db = client['clash_royale']
players_collection = db['players']
battles_collection = db['battles']

# Função para buscar dados de jogadores
def fetch_player_data(player_tag):
    url = 'https://api.clashroyale.com/v1/players/%23{player_tag}'
    headers = {
        'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6IjBhMmZmMDg5LTUyMmItNGE1Mi1iYzFhLTNkZTE2ZjIzYzYzMCIsImlhdCI6MTcyMjE0MDEwOCwic3ViIjoiZGV2ZWxvcGVyLzEwY2YyNWNkLWQ0NzgtY2VmYy0wMGE0LTllODA0MTU0NWYxZSIsInNjb3BlcyI6WyJyb3lhbGUiXSwibGltaXRzIjpbeyJ0aWVyIjoiZGV2ZWxvcGVyL3NpbHZlciIsInR5cGUiOiJ0aHJvdHRsaW5nIn0seyJjaWRycyI6WyIxODYuMjE2LjIxNi43MSJdLCJ0eXBlIjoiY2xpZW50In1dfQ.gGVx-VXla497Q8NXNdY8bm0f5mTasSopKUjwqCCK-skpje-oQTjx9QgKjKDRZrQau4XSrWpxaK9BoO7_p0MLew'          
        
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
        'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6IjBhMmZmMDg5LTUyMmItNGE1Mi1iYzFhLTNkZTE2ZjIzYzYzMCIsImlhdCI6MTcyMjE0MDEwOCwic3ViIjoiZGV2ZWxvcGVyLzEwY2YyNWNkLWQ0NzgtY2VmYy0wMGE0LTllODA0MTU0NWYxZSIsInNjb3BlcyI6WyJyb3lhbGUiXSwibGltaXRzIjpbeyJ0aWVyIjoiZGV2ZWxvcGVyL3NpbHZlciIsInR5cGUiOiJ0aHJvdHRsaW5nIn0seyJjaWRycyI6WyIxODYuMjE2LjIxNi43MSJdLCJ0eXBlIjoiY2xpZW50In1dfQ.gGVx-VXla497Q8NXNdY8bm0f5mTasSopKUjwqCCK-skpje-oQTjx9QgKjKDRZrQau4XSrWpxaK9BoO7_p0MLew'          
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to retrieve battle data for tag {player_tag}: {response.status_code}")
        return None

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
            print("Dados player inseridos com sucesso.")
        else:
            print(f"Falha ao obter dados para o jogador {tag}.")        
        
        battle_data = fetch_battle_data(tag)
        if battle_data:
            if isinstance(battle_data, list) and len(battle_data) > 0:
                battles_collection.insert_many(battle_data)
                print("Dados battle inseridos com sucesso.")
            elif 'items' in battle_data and len(battle_data['items']) > 0:
                battles_collection.insert_many(battle_data['items'])
                print(f"Dados de batalhas para o jogador {tag} inseridos com sucesso.")
            else:
                print(f"Falha ao obter dados de batalhas para o jogador {tag} ou nenhum dado disponível.")
        else:
            print(f"Falha ao obter dados de batalhas para o jogador {tag} ou nenhum dado disponível.")
        print("---------------------------------------------")

# Exemplo de uso da função insert_data com uma lista de player_tags   9JPL980Y2
player_tags = ['2GYRQJRR8'] 
insert_data(player_tags)
