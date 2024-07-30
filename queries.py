# -*- coding: utf-8 -*-
"""
Created on Sun Jul 28 09:09:48 2024
@authors: Flavio, David e Jean
"""

from database import battles_collection
from datetime import datetime
import pytz


# Listar todas as cartas únicas existentes nas batalhas e a quantidade de vezes que foi exibida
def list_existing_cards():
    # Criar um dicionário para armazenar a contagem de cartas
    cards_count = {}
    
    # Buscar todos os documentos na coleção de batalhas
    battles = battles_collection.find({})
    
    # Iterar sobre os documentos e contar as cartas
    for battle in battles:
        for card in battle.get('team', [{}])[0].get('cards', []):
            card_name = card['name']
            cards_count[card_name] = cards_count.get(card_name, 0) + 1
        for card in battle.get('opponent', [{}])[0].get('cards', []):
            card_name = card['name']
            cards_count[card_name] = cards_count.get(card_name, 0) + 1
    
    # Exibir as cartas existentes e suas quantidades
    if cards_count:        
        for card_name, count in sorted(cards_count.items()):
            print(f"{card_name} ({count})")
    else:
        print("Nenhuma carta encontrada nas batalhas.")

'''
# Converter uma string de data no formato ISO 8601 para um objeto datetime.
def parse_date(date_str):    
    try:
        # Ajustar o formato para corresponder ao seu JSON
        return datetime.strptime(date_str, '%Y%m%dT%H%M%S.%fZ').replace(tzinfo=pytz.UTC)
    except ValueError as e:
        print(f"Erro ao analisar a data: {e}")
        return None


# Encontrar o intervalo de datas (mais antiga e mais recente) para todas as batalhas na coleção.
def get_date_range_all_battles():
    
    # Contar o número total de batalhas
    total_battles = battles_collection.count_documents({})
    
    if total_battles == 0:
        return {'error': 'Nenhuma batalha encontrada na coleção.'}
    
    # Buscar todas as batalhas e inicializar variáveis para as datas
    earliest_date = None
    latest_date = None
    
    for battle in battles_collection.find({}, {'battleTime': 1}):
        battle_date = parse_date(battle['battleTime'])
                
        if battle_date is None:
            continue
        
        if earliest_date is None or battle_date < earliest_date:
            earliest_date = battle_date
        
        if latest_date is None or battle_date > latest_date:
            latest_date = battle_date
    
    # Retornar o intervalo de datas
    return {
        'earliest_date': earliest_date.isoformat() if earliest_date else None,
        'latest_date': latest_date.isoformat() if latest_date else None
    }
'''

# Converter uma string de data no formato 'YYYYMMDDTHHMMSS.sssZ' para um objeto datetime
def parse_date(date_str):    
    try:        
        return datetime.strptime(date_str, '%Y%m%dT%H%M%S.%fZ').replace(tzinfo=pytz.UTC)
    except ValueError as e:
        print(f"Erro ao analisar a data: {e}")
        return None

# Formatar um objeto datetime para o formato 'YYYY-MM-DD HH:MM:SS'.
def format_date(date_obj):    
    if date_obj:
        return date_obj.strftime('%Y-%m-%d %H:%M:%S')
    return None

# Encontra o intervalo de datas (mais antiga e mais recente) para todas as batalhas na coleção
def get_date_range_all_battles():
    # Contar o número total de batalhas
    total_battles = battles_collection.count_documents({})
    
    if total_battles == 0:
        return {'error': 'Nenhuma batalha encontrada na coleção.'}
    
    # Buscar todas as batalhas e inicializar variáveis para as datas
    earliest_date = None
    latest_date = None
    
    for battle in battles_collection.find({}, {'battleTime': 1}):
        battle_date = parse_date(battle['battleTime'])
        
        if battle_date is None:
            continue
        
        if earliest_date is None or battle_date < earliest_date:
            earliest_date = battle_date
        
        if latest_date is None or battle_date > latest_date:
            latest_date = battle_date
    
    # Formatar as datas
    earliest_date_formatted = format_date(earliest_date)
    latest_date_formatted = format_date(latest_date)
    
    # Retornar o intervalo de datas
    return {
        'earliest_date': earliest_date_formatted,
        'latest_date': latest_date_formatted
    }


# Consulta para encontrar a data mais antiga e a mais recente para ser utilizadas nas pesquisas
def get_date_range_from_db():    
    pipeline = [
        {
            '$group': {
                '_id': None,
                'earliest_date': {'$min': '$battleTime'},
                'latest_date': {'$max': '$battleTime'}
            }
        }
    ]
    
    result = list(battles_collection.aggregate(pipeline))
    
    if result:
        earliest_date = result[0]['earliest_date']
        latest_date = result[0]['latest_date']
        
        return {
            'earliest_date': earliest_date,
            'latest_date': latest_date
        }
    else:
        return {'error': 'No battles found in the database.'}
    

# Consulta 1: Porcentagem de vitórias e derrotas utilizando a carta X
def victory_defeat_percentage(card_name, start_date, end_date):
    # Filtros para a consulta
    query = {
        'battleTime': {'$gte': start_date, '$lte': end_date},
        '$or': [
            {'team.cards.name': card_name},
            {'opponent.cards.name': card_name}
        ]
    }
    
    # Contadores
    total_battles = 0
    victories = 0
    defeats = 0
    
    # Buscar batalhas
    battles = battles_collection.find(query)
    
    for battle in battles:
        total_battles += 1
        # Verificar se a carta foi usada pela equipe do jogador
        card_used_by_team = any(card['name'] == card_name for card in battle.get('team', [{}])[0].get('cards', []))
        # Verificar se a equipe do jogador venceu ou perdeu
        if battle.get('team', [{}])[0].get('trophyChange', 0) > 0:
            if card_used_by_team:
                victories += 1
        else:
            if card_used_by_team:
                defeats += 1
    
    # Calcular porcentagens
    victory_percentage = (victories / total_battles * 100) if total_battles > 0 else None
    defeat_percentage = (defeats / total_battles * 100) if total_battles > 0 else None
    
    # Formatar os resultados
    formatted_victory_percentage = f"{victory_percentage:.2f}%" if victory_percentage is not None else "N/A"
    formatted_defeat_percentage = f"{defeat_percentage:.2f}%" if defeat_percentage is not None else "N/A"
    
    # Retornar os resultados formatados
    return f"Percentual de Vitória: {formatted_victory_percentage}\nPercentual de Derrota: {formatted_defeat_percentage}"

'''
def victory_defeat_percentage(card_name, start_date, end_date):
    # Conversão das datas para formato ISO
    start_date = start_date
    end_date = end_date
    
    # Filtros para a consulta
    query = {
        'battleTime': {'$gte': start_date, '$lte': end_date},
        '$or': [
            {'team.cards.name': card_name},
            {'opponent.cards.name': card_name}
        ]
    }
    
    # Contadores
    total_battles = 0
    victories = 0
    defeats = 0
    
    # Buscar batalhas
    battles = battles_collection.find(query)
    
    for battle in battles:
        total_battles += 1
        # Verificar se a carta foi usada pela equipe do jogador
        card_used_by_team = any(card['name'] == card_name for card in battle.get('team', [{}])[0].get('cards', []))
        # Verificar se a equipe do jogador venceu ou perdeu
        if battle.get('team', [{}])[0].get('trophyChange', 0) > 0:
            if card_used_by_team:
                victories += 1
        else:
            if card_used_by_team:
                defeats += 1
    
    # Calcular porcentagens
    victory_percentage = (victories / total_battles * 100) if total_battles > 0 else None
    defeat_percentage = (defeats / total_battles * 100) if total_battles > 0 else None
    
    # Retornar os resultados
    return [{'victory_percentage': victory_percentage, 'defeat_percentage': defeat_percentage}]
'''

'''
# Consulta 1: Porcentagem de vitórias e derrotas utilizando a carta X
def victory_defeat_percentage(card, start_time, end_time):
    pipeline = [
        {"$match": {"battleTime": {"$gte": start_time, "$lte": end_time}}},
        {"$facet": {
            "victories": [
                {"$match": {"team.cards": card, "win": True}},
                {"$count": "count"}
            ],
            "defeats": [
                {"$match": {"opponent.cards": card, "win": False}},
                {"$count": "count"}
            ]
        }},
        {"$project": {
            "victory_percentage": {"$cond": [{"$eq": [{"$arrayElemAt": ["$victories.count", 0]}, None]}, 0, {"$multiply": [{"$divide": [{"$arrayElemAt": ["$victories.count", 0]}, {"$sum": [{"$arrayElemAt": ["$victories.count", 0]}, {"$arrayElemAt": ["$defeats.count", 0]}]}]}, 100]}]},
            "defeat_percentage": {"$cond": [{"$eq": [{"$arrayElemAt": ["$defeats.count", 0]}, None]}, 0, {"$multiply": [{"$divide": [{"$arrayElemAt": ["$defeats.count", 0]}, {"$sum": [{"$arrayElemAt": ["$victories.count", 0]}, {"$arrayElemAt": ["$defeats.count", 0]}]}]}, 100]}]}
        }}
    ]
    return list(battles_collection.aggregate(pipeline))
'''

# Consulta 2: Listar decks com mais de X% de vitórias
def decks_with_high_win_rate(min_win_percentage, start_time, end_time):
    pipeline = [
        {"$match": {"battleTime": {"$gte": start_time, "$lte": end_time}}},
        {"$group": {
            "_id": "$team.cards",
            "win_count": {"$sum": {"$cond": [{"$gt": ["$team.crowns", "$opponent.crowns"]}, 1, 0]}},
            "total_count": {"$sum": 1}
        }},
        {"$project": {
            "deck": "$_id",
            "win_percentage": {"$multiply": [{"$divide": ["$win_count", "$total_count"]}, 100]}
        }},
        {"$match": {"win_percentage": {"$gte": min_win_percentage}}}
    ]
    
    decks = list(battles_collection.aggregate(pipeline))
    
    for deck in decks:
        deck_cards = deck.get('deck', [])
        
        # Checar se deck_cards é uma lista e se contém listas de dicionários
        if isinstance(deck_cards, list) and all(isinstance(sublist, list) and all(isinstance(card, dict) for card in sublist) for sublist in deck_cards):
            # Desaninhando a lista
            flat_deck_cards = [card for sublist in deck_cards for card in sublist]
            
            deck_names = [card.get('name', 'Desconhecido') for card in flat_deck_cards]
        else:
            print("Erro: Algum item em 'deck_cards' não é um dicionário ou 'deck_cards' não é uma lista.")
            continue
        
        win_percentage = deck.get('win_percentage', 0)
        
        # Formatar a porcentagem de vitória para duas casas decimais
        win_percentage_formatted = f"{win_percentage:.2f}"
        
        # Imprimir informações do deck
        print(f"Deck: {', '.join(deck_names)}")
        print(f"Porcentagem de Vitória: {win_percentage_formatted}%")
        print()  # Linha em branco para separar decks, se houver mais de um
    
    #return decks

'''
# Consulta 2: Listar decks com mais de X% de vitórias
def decks_with_high_win_rate(min_win_percentage, start_time, end_time):
    pipeline = [
        {"$match": {"battleTime": {"$gte": start_time, "$lte": end_time}}},
        {"$group": {
            "_id": "$team.cards",
            "win_count": {"$sum": {"$cond": [{"$gt": ["$team.crowns", "$opponent.crowns"]}, 1, 0]}},
            "total_count": {"$sum": 1}
        }},
        {"$project": {
            "_id": 0,
            "deck": "$_id",
            "win_percentage": {"$multiply": [{"$divide": ["$win_count", "$total_count"]}, 100]}
        }},
        {"$match": {"win_percentage": {"$gte": min_win_percentage}}}
    ]
    return list(battles_collection.aggregate(pipeline))
'''

      
# Consulta 3: Quantidade de derrotas usando o combo de cartas (X1, X2, ...)
def defeats_with_combo(combo, start_time, end_time):
    
    if not isinstance(combo, list):
        raise ValueError("Combo deve ser uma lista de cartas.")
    
    pipeline = [
        # Filtro pelo intervalo de datas
        {"$match": {"battleTime": {"$gte": start_time, "$lte": end_time}}},
        
        # Projeção com detecção de derrotas
        {"$project": {
            "team_defeat": {
                "$cond": [
                    {
                        "$and": [
                            {"$lt": [{"$arrayElemAt": ["$team.crowns", 0]}, {"$arrayElemAt": ["$opponent.crowns", 0]}]},
                            {"$setIsSubset": [combo, {"$arrayElemAt": ["$team.cards.name", 0]}]}
                        ]
                    }, 1, 0
                ]
            },
            "opponent_defeat": {
                "$cond": [
                    {
                        "$and": [
                            {"$lt": [{"$arrayElemAt": ["$opponent.crowns", 0]}, {"$arrayElemAt": ["$team.crowns", 0]}]},
                            {"$setIsSubset": [combo, {"$arrayElemAt": ["$opponent.cards.name", 0]}]}
                        ]
                    }, 1, 0
                ]
            }
        }},
        
        # Agrupar e somar derrotas
        {"$group": {
            "_id": None,
            "team_defeats": {"$sum": "$team_defeat"},
            "opponent_defeats": {"$sum": "$opponent_defeat"}
        }}
    ]
    
    result = list(battles_collection.aggregate(pipeline))

    # Exibir o resultado
    if result:
        team_defeats = result[0].get('team_defeats', 0)
        opponent_defeats = result[0].get('opponent_defeats', 0)
        total_defeats = team_defeats + opponent_defeats
    else:
        team_defeats = opponent_defeats = total_defeats = 0

    print(f"Quantidade de derrotas usando o combo de cartas {combo}:")
    print(f"- Derrotas do time: {team_defeats}")
    print(f"- Derrotas do oponente: {opponent_defeats}")
    print(f"- Total de derrotas: {total_defeats}")


'''
# Consulta 3: Quantidade de derrotas usando o combo de cartas (X1, X2, ...)
def defeats_with_combo(combo, start_time, end_time):
    pipeline = [
        {"$match": {"battleTime": {"$gte": start_time, "$lte": end_time}}},
        {"$project": {
            "team_defeat": {
                "$cond": [
                    {
                        "$and": [
                            {"$lt": [{"$arrayElemAt": ["$team.crowns", 0]}, {"$arrayElemAt": ["$opponent.crowns", 0]}]},
                            {"$setIsSubset": [combo, "$team.cards.name"]}
                        ]
                    }, 1, 0
                ]
            },
            "opponent_defeat": {
                "$cond": [
                    {
                        "$and": [
                            {"$lt": [{"$arrayElemAt": ["$opponent.crowns", 0]}, {"$arrayElemAt": ["$team.crowns", 0]}]},
                            {"$setIsSubset": [combo, "$opponent.cards.name"]}
                        ]
                    }, 1, 0
                ]
            }
        }},
        {"$group": {
            "_id": None,
            "team_defeats": {"$sum": "$team_defeat"},
            "opponent_defeats": {"$sum": "$opponent_defeat"}
        }}
    ]
    
    result = list(battles_collection.aggregate(pipeline))

    if result:
        team_defeats = result[0].get('team_defeats', 0)
        opponent_defeats = result[0].get('opponent_defeats', 0)
        total_defeats = team_defeats + opponent_defeats
    else:
        team_defeats = opponent_defeats = total_defeats = 0
    
    print(f"3. Quantidade de derrotas usando o combo de cartas {combo}:")
    print(f"- Derrotas do time: {team_defeats}")
    print(f"- Derrotas do oponente: {opponent_defeats}")
    print(f"- Total de derrotas: {total_defeats}")
'''    
    

'''
# Consulta 3: Quantidade de derrotas usando o combo de cartas (X1, X2, ...)
def defeats_with_combo(combo, start_time, end_time):
    pipeline = [
        {"$match": {
            "battleTime": {"$gte": start_time, "$lte": end_time}
        }},
        {"$project": {
            "team_defeat": {
                "$cond": [
                    {
                        "$and": [
                            {"$lt": [{"$arrayElemAt": ["$team.crowns", 0]}, {"$arrayElemAt": ["$opponent.crowns", 0]}]},
                            {"$setIsSubset": [combo, "$team.cards.name"]}
                        ]
                    }, 1, 0
                ]
            },
            "opponent_defeat": {
                "$cond": [
                    {
                        "$and": [
                            {"$lt": [{"$arrayElemAt": ["$opponent.crowns", 0]}, {"$arrayElemAt": ["$team.crowns", 0]}]},
                            {"$setIsSubset": [combo, "$opponent.cards.name"]}
                        ]
                    }, 1, 0
                ]
            }
        }},
        {"$group": {
            "_id": None,
            "team_defeats": {"$sum": "$team_defeat"},
            "opponent_defeats": {"$sum": "$opponent_defeat"}
        }}
    ]
    return list(battles_collection.aggregate(pipeline))
'''


'''
# Consulta 4: Vitórias com carta X e condições específicas
def victories_with_conditions(card, trophy_difference, start_time, end_time):
    pipeline = [
        {"$match": {"battleTime": {"$gte": start_time, "$lte": end_time}, "win": True, "team.cards": card}},
        {"$redact": {
            "$cond": {
                "if": {
                    "$and": [
                        {"$lt": ["$duration", 120]},
                        {"$gte": ["$opponent.towers", 2]},
                        {"$gte": [{"$subtract": ["$opponent.trophies", "$team.trophies"]}, trophy_difference]}
                    ]
                },
                "then": "$$KEEP",
                "else": "$$PRUNE"
            }
        }},
        {"$group": {"_id": None, "victories": {"$sum": 1}}}
    ]
    return list(battles_collection.aggregate(pipeline))
'''

# Consulta 4: Vitórias com carta X e condições específicas
from datetime import timedelta

def victories_with_conditions(card_name, trophy_diff_percentage, min_towers_downed):
    # Calcular o timestamp de 2 minutos para comparação
    max_duration = timedelta(minutes=2)
    
    # Contadores
    total_battles = 0
    victories = 0
    
    # Buscar batalhas
    battles = battles_collection.find({
        '$or': [
            {'team.cards.name': card_name},
            {'opponent.cards.name': card_name}
        ]
    })
    
    for battle in battles:
        total_battles += 1
        team = battle.get('team', [{}])[0]
        opponent = battle.get('opponent', [{}])[0]
        
        # Verificar se a carta foi usada pela equipe do jogador
        card_used_by_team = any(card['name'] == card_name for card in team.get('cards', []))
        card_used_by_opponent = any(card['name'] == card_name for card in opponent.get('cards', []))
        
        # Verificar se a partida durou menos de 2 minutos
        battle_duration = timedelta(seconds=battle.get('duration', 0))
        if battle_duration >= max_duration:
            continue
        
        # Verificar se o perdedor derrubou ao menos duas torres
        team_crowns = team.get('crowns', 0)
        opponent_crowns = opponent.get('crowns', 0)
        if team_crowns < 2 and opponent_crowns < 2:
            continue
        
        # Verificar se o vencedor possui n% menos troféus do que o perdedor
        team_starting_trophies = team.get('startingTrophies', 0)
        opponent_starting_trophies = opponent.get('startingTrophies', 0)
        
        if team_starting_trophies < opponent_starting_trophies * (1 - trophy_diff_percentage / 100.0):
            winner = team
            loser = opponent
        elif opponent_starting_trophies < team_starting_trophies * (1 - trophy_diff_percentage / 100.0):
            winner = opponent
            loser = team
        else:
            continue
        
        # Verificar se a carta estava no deck do vencedor
        card_used_by_winner = any(card['name'] == card_name for card in winner.get('cards', []))
        
        if card_used_by_winner:
            victories += 1

    # Formatar os resultados
    return f"Vitórias com as condições: {victories}\nTotal de batalhas avaliadas: {total_battles}"


    
    
    
    

# Consulta 5: Combos de cartas de tamanho N com mais de Y% de vitórias
def combo_win_rate(combo_size, min_win_percentage, start_time, end_time):
    pipeline = [
        {"$match": {"battleTime": {"$gte": start_time, "$lte": end_time}, "win": True}},
        {"$unwind": "$team.cards"},
        {"$group": {"_id": "$team.cards", "count": {"$sum": 1}}},
        {"$match": {"count": {"$gte": combo_size}}},
        {"$group": {"_id": None, "combos": {"$push": "$_id"}, "count": {"$sum": "$count"}}},
        {"$unwind": "$combos"},
        {"$project": {"combo": "$combos", "win_percentage": {"$multiply": [{"$divide": ["$count", {"$sum": ["$count"]}]}, 100]}}},
        {"$match": {"win_percentage": {"$gte": min_win_percentage}}}
    ]
    return list(battles_collection.aggregate(pipeline))


# Consulta 6 (Adicional): Média de duração das batalhas que utilizam a carta X
def average_battle_duration(card, start_time, end_time):
    pipeline = [
        {"$match": {"battleTime": {"$gte": start_time, "$lte": end_time}, "team.cards": card}},
        {"$group": {"_id": None, "average_duration": {"$avg": "$duration"}}}
    ]
    return list(battles_collection.aggregate(pipeline))


# Consulta 7 (Adicional): Cartas mais utilizadas em vitórias com mais de X troféus
def most_used_cards_in_wins(min_trophies):
    pipeline = [
        {"$match": {"win": True, "team.trophies": {"$gte": min_trophies}}},
        {"$unwind": "$team.cards"},
        {"$group": {"_id": "$team.cards", "usage_count": {"$sum": 1}}},
        {"$sort": {"usage_count": -1}}
    ]
    return list(battles_collection.aggregate(pipeline))


# Consulta 8 (Adicional): Quantidade de batalhas vencidas com decks sem carta X
def battles_won_without_card(card):
    pipeline = [
        {"$match": {"win": True, "team.cards": {"$ne": card}}},
        {"$group": {"_id": None, "battles_won": {"$sum": 1}}}
    ]
    return list(battles_collection.aggregate(pipeline))

