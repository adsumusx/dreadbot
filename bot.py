#!/usr/bin/env python3
"""
Bot de Monitoramento DreadmystDB Trade
Monitora a rota de trade e alerta quando encontrar itens que correspondam aos filtros configurados.
"""

import requests
from bs4 import BeautifulSoup
import time
import json
import re
from datetime import datetime
from typing import List, Dict, Set, Optional
from dataclasses import dataclass, asdict
import sys


@dataclass
class Item:
    """Representa um item encontrado no trade"""
    listing_id: str
    name: str
    item_level: str
    stats: List[str]
    price: str
    seller: str
    time_left: str
    url: str
    slot: Optional[str] = None
    affix_quality: Optional[str] = None  # Fine, Pristine, Superior, Exquisite

    def to_dict(self):
        return asdict(self)


class TradeMonitor:
    """Monitor de trade do DreadmystDB"""
    
    BASE_URL = "https://dreadmystdb.com/trade"
    
    # Mapeamento de slots baseado no nome do item
    SLOT_KEYWORDS = {
        'head': ['coif', 'hood', 'helmet', 'cap', 'crown'],
        'necklace': ['choker', 'pendant', 'necklace', 'amulet'],
        'chest': ['breastplate', 'vestments', 'chest', 'armor', 'torso'],
        'waist': ['sash', 'belt', 'waist'],
        'legs': ['greaves', 'leggings', 'legs', 'pants'],
        'feet': ['slippers', 'boots', 'feet', 'shoes'],
        'hands': ['handwraps', 'grips', 'gloves', 'hands', 'gauntlets'],
        'ring': ['ring'],
        'main hand': ['sword', 'mace', 'axe', 'dagger', 'staff', 'wand', 'blade'],
        'off hand': ['barricade', 'shield', 'offhand'],
        'ranged': ['bow', 'crossbow', 'ranged', 'dragonslayer']
    }
    
    # Mapeamento de stats para valores numéricos (baseado no HTML)
    STAT_MAPPING = {
        'agility': 'AGI',
        'armor value': 'Armor',
        'armor': 'Armor',
        'axes': 'Axes',
        'block rating': 'Block',
        'block': 'Block',
        'courage': 'COU',
        'daggers': 'Daggers',
        'dodge rating': 'Dodge',
        'dodge': 'Dodge',
        'health': 'HP',
        'intelligence': 'INT',
        'maces': 'Maces',
        'mana': 'Mana',
        'meditate': 'Meditate',
        'melee critical': 'Melee Crit',
        'melee crit': 'Melee Crit',
        'melee speed': 'Melee Speed',
        'ranged': 'Ranged',
        'ranged critical': 'Ranged Crit',
        'rng crit': 'Ranged Crit',
        'ranged speed': 'Ranged Speed',
        'ranged weapon value': 'Ranged Wpn',
        'rng dmg': 'Ranged Wpn',
        'rng wpn': 'Ranged Wpn',
        'regeneration': 'Regen',
        'regen': 'Regen',
        'resist fire': 'Fire Res',
        'fire res': 'Fire Res',
        'resist frost': 'Frost Res',
        'frost res': 'Frost Res',
        'resist holy': 'Holy Res',
        'holy res': 'Holy Res',
        'resist shadow': 'Shadow Res',
        'shadow res': 'Shadow Res',
        'shields': 'Shields',
        'spell critical': 'Spell Crit',
        'spell crit': 'Spell Crit',
        'staves': 'Staves',
        'strength': 'STR',
        'swords': 'Swords',
        'wands': 'Wands',
        'weapon value': 'Wpn Dmg',
        'wpn dmg': 'Wpn Dmg',
        'willpower': 'WIL'
    }
    
    def __init__(self, config_file: str = "config.json"):
        """Inicializa o monitor com configurações"""
        self.config = self.load_config(config_file)
        self.seen_items: Set[str] = set()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def load_config(self, config_file: str) -> Dict:
        """Carrega configurações do arquivo JSON"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Configuração padrão
            default_config = {
                "quality": [5, 6],  # Holy e Godly
                "min_level": 24,
                "max_level": None,
                "min_price": None,
                "max_price": None,
                "stats": [],  # Lista de stats desejados (ex: ["STR", "INT", "COU", "AGI"])
                "slots": [],  # Lista de slots desejados (ex: ["chest", "hands", "head"])
                "check_interval": 20,  # Segundos entre verificações
                "alert_method": "console",  # console, file, both
                "debug": False,  # Ativa modo debug para ver detalhes da verificação
                "filter_mode": "AND"  # "AND" = ambos filtros devem corresponder, "OR" = pelo menos um deve corresponder
            }
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            print(f"Arquivo de configuração criado: {config_file}")
            print("Por favor, edite o arquivo e configure seus filtros.")
            return default_config
    
    def build_url(self) -> str:
        """Constrói a URL com os parâmetros de filtro"""
        params = {
            'q': '',
            'sort': 'newest',
            'commit': 'Apply'
        }
        
        # Quality
        if self.config.get('quality'):
            params['quality[]'] = self.config['quality']
        
        # Level
        if self.config.get('min_level'):
            params['min_level'] = self.config['min_level']
        if self.config.get('max_level'):
            params['max_level'] = self.config['max_level']
        
        # Price
        if self.config.get('min_price'):
            params['min_price'] = self.config['min_price']
        if self.config.get('max_price'):
            params['max_price'] = self.config['max_price']
        
        # Stats e Slots são filtrados localmente, não na URL
        # (o site espera IDs numéricos, não nomes)
        
        # Affix Quality (mapeia nomes para valores numéricos)
        if self.config.get('affix_quality'):
            affix_quality_mapping = {
                'Fine': 2,
                'Pristine': 3,
                'Superior': 4,
                'Exquisite': 5
            }
            affix_scores = []
            for quality in self.config['affix_quality']:
                if quality in affix_quality_mapping:
                    affix_scores.append(affix_quality_mapping[quality])
            if affix_scores:
                params['affix_score[]'] = affix_scores
        
        # Constrói a URL
        url = self.BASE_URL + '?'
        param_parts = []
        for key, value in params.items():
            if isinstance(value, list):
                for v in value:
                    param_parts.append(f"{key}={v}")
            else:
                param_parts.append(f"{key}={value}")
        
        return url + '&'.join(param_parts)
    
    def detect_slot(self, item_name: str) -> Optional[str]:
        """Detecta o slot do equipamento baseado no nome"""
        item_name_lower = item_name.lower()
        for slot, keywords in self.SLOT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in item_name_lower:
                    return slot
        return None
    
    def normalize_slot_name(self, slot: str) -> str:
        """Normaliza o nome do slot para comparação"""
        slot_lower = slot.lower().strip()
        # Mapeia variações comuns para os slots padrão
        slot_mapping = {
            'helmet': 'head',
            'helm': 'head',
            'cap': 'head',
            'crown': 'head',
            'coif': 'head',
            'hood': 'head',
            'head': 'head',
            'necklace': 'necklace',
            'choker': 'necklace',
            'pendant': 'necklace',
            'amulet': 'necklace',
            'chest': 'chest',
            'breastplate': 'chest',
            'vestments': 'chest',
            'torso': 'chest',
            'waist': 'waist',
            'sash': 'waist',
            'belt': 'waist',
            'legs': 'legs',
            'greaves': 'legs',
            'leggings': 'legs',
            'pants': 'legs',
            'feet': 'feet',
            'slippers': 'feet',
            'boots': 'feet',
            'shoes': 'feet',
            'hands': 'hands',
            'handwraps': 'hands',
            'grips': 'hands',
            'gloves': 'hands',
            'gauntlets': 'hands',
            'ring': 'ring',
            'main hand': 'main hand',
            'mainhand': 'main hand',
            'off hand': 'off hand',
            'offhand': 'off hand',
            'shield': 'off hand',
            'barricade': 'off hand',
            'ranged': 'ranged',
            'bow': 'ranged',
            'crossbow': 'ranged',
            'dragonslayer': 'ranged'
        }
        return slot_mapping.get(slot_lower, slot_lower)
    
    def parse_stats(self, stats_text: str) -> List[str]:
        """Extrai as estatísticas do texto"""
        stats = []
        # Padrão para encontrar stats como "+44 STR", "+94 Fire Res", "+157 HP", etc.
        # Procura por spans com classes de cor que contêm os stats
        # Mas também tenta extrair do texto direto
        pattern = r'\+(\d+)\s+([A-Za-z\s]+?)(?=\s+[+\-]|$|•|by)'
        matches = re.findall(pattern, stats_text)
        for value, stat_name in matches:
            stat_name_clean = stat_name.strip()
            if stat_name_clean:
                stats.append(f"+{value} {stat_name_clean}")
        return stats
    
    def normalize_stat(self, stat: str) -> str:
        """Normaliza o nome do stat para comparação"""
        # Remove o sinal de + e espaços extras
        stat_clean = stat.replace('+', '').strip()
        stat_lower = stat_clean.lower()
        
        # Remove números do início (ex: "21 Rng Dmg" -> "Rng Dmg")
        stat_lower = re.sub(r'^\d+\s+', '', stat_lower)
        
        # Tenta encontrar correspondência no mapeamento
        for key, value in self.STAT_MAPPING.items():
            if key in stat_lower or value.lower() in stat_lower:
                return value
        
        # Se não encontrou, retorna o stat original sem o +
        return stat_clean.strip()
    
    def item_matches_filters(self, item: Item, debug: bool = False) -> bool:
        """Verifica se o item corresponde aos filtros configurados"""
        # Filtros disponíveis
        has_slot_filter = self.config.get('slots') and len(self.config['slots']) > 0
        has_primary_stat_filter = self.config.get('primary_stats') and len(self.config['primary_stats']) > 0
        has_stat_filter = self.config.get('stats') and len(self.config['stats']) > 0
        has_affix_quality_filter = self.config.get('affix_quality') and len(self.config['affix_quality']) > 0
        
        # Modo de filtro: "AND" (ambos devem corresponder) ou "OR" (pelo menos um)
        filter_mode = self.config.get('filter_mode', 'AND').upper()
        
        if debug:
            print(f"\n  [DEBUG] Verificando item: {item.name}")
            print(f"  [DEBUG] Slot detectado: {item.slot}")
            print(f"  [DEBUG] Stats: {item.stats}")
            print(f"  [DEBUG] Modo de filtro: {filter_mode}")
        
        # Se não há filtros, aceita tudo
        if not has_slot_filter and not has_primary_stat_filter and not has_stat_filter and not has_affix_quality_filter:
            if debug:
                print(f"  [DEBUG] ✓ Sem filtros - aceita todos")
            return True
        
        slot_matches = False
        primary_stat_matches = False
        stat_matches = False
        affix_quality_matches = False
        
        # Verifica slot
        if has_slot_filter:
            if not item.slot:
                if debug:
                    print(f"  [DEBUG] ❌ Item sem slot detectado")
                if filter_mode == 'AND':
                    return False
            else:
                # Normaliza os slots para comparação
                item_slot_normalized = self.normalize_slot_name(item.slot)
                config_slots_normalized = [self.normalize_slot_name(s) for s in self.config['slots']]
                
                slot_matches = item_slot_normalized in config_slots_normalized
                
                if debug:
                    print(f"  [DEBUG] Slot normalizado: {item_slot_normalized}")
                    print(f"  [DEBUG] Slots configurados normalizados: {config_slots_normalized}")
                    print(f"  [DEBUG] Slot match: {slot_matches}")
        else:
            # Se não há filtro de slot, considera como match
            slot_matches = True
        
        # Verifica stats primários (OBRIGATÓRIOS)
        if has_primary_stat_filter:
            config_primary_stats = self.config['primary_stats']
            primary_stats_mode = self.config.get('primary_stats_mode', 'OR')  # OR = um dos, AND = todos
            
            # Normaliza os stats primários configurados
            config_primary_stats_normalized = [self.normalize_stat(stat).upper() for stat in config_primary_stats]
            
            if primary_stats_mode == 'AND':
                # Modo AND: item DEVE ter TODOS os stats primários selecionados
                found_stats = []
                for config_stat_normalized in config_primary_stats_normalized:
                    found = False
                    for item_stat in item.stats:
                        item_stat_normalized = self.normalize_stat(item_stat).upper()
                        if config_stat_normalized == item_stat_normalized or config_stat_normalized in item_stat_normalized or item_stat_normalized in config_stat_normalized:
                            found = True
                            if debug:
                                print(f"  [DEBUG] ✓ Stat primário encontrado (AND): {config_stat_normalized} em {item_stat_normalized}")
                            break
                    found_stats.append(found)
                
                # Verifica se todos foram encontrados
                primary_stat_matches = all(found_stats)
                
                if debug:
                    print(f"  [DEBUG] Stats primários configurados (AND): {config_primary_stats} -> normalizados: {config_primary_stats_normalized}")
                    print(f"  [DEBUG] Stats encontrados: {found_stats}")
                    print(f"  [DEBUG] Todos os stats primários encontrados: {primary_stat_matches}")
                
                if not primary_stat_matches:
                    if debug:
                        print(f"  [DEBUG] ❌ Item não tem todos os stats primários obrigatórios")
                    return False
            else:
                # Modo OR (padrão): item DEVE ter pelo menos UM dos stats primários selecionados
                for item_stat in item.stats:
                    item_stat_normalized = self.normalize_stat(item_stat).upper()
                    
                    # Compara os stats normalizados
                    for config_stat_normalized in config_primary_stats_normalized:
                        if config_stat_normalized == item_stat_normalized or config_stat_normalized in item_stat_normalized or item_stat_normalized in config_stat_normalized:
                            primary_stat_matches = True
                            if debug:
                                print(f"  [DEBUG] ✓ Stat primário encontrado (OR): {config_stat_normalized} em {item_stat_normalized} (original: {item_stat})")
                            break
                    
                    if primary_stat_matches:
                        break
                
                if debug:
                    print(f"  [DEBUG] Stats primários configurados (OR): {config_primary_stats} -> normalizados: {config_primary_stats_normalized}")
                    print(f"  [DEBUG] Stat primário encontrado: {primary_stat_matches}")
                
                # Se não encontrou nenhum stat primário, item não corresponde
                if not primary_stat_matches:
                    if debug:
                        print(f"  [DEBUG] ❌ Item não tem nenhum stat primário obrigatório")
                    return False
        else:
            # Se não há filtro de stat primário, considera como match
            primary_stat_matches = True
        
        # Verifica outros stats (OR - pelo menos um deve estar presente se configurado)
        if has_stat_filter:
            config_stats = self.config['stats']
            
            # Normaliza os stats configurados
            config_stats_normalized = [self.normalize_stat(stat).upper() for stat in config_stats]
            
            # Verifica se pelo menos um stat configurado está presente no item
            for item_stat in item.stats:
                item_stat_normalized = self.normalize_stat(item_stat).upper()
                
                # Compara os stats normalizados
                for config_stat_normalized in config_stats_normalized:
                    if config_stat_normalized == item_stat_normalized or config_stat_normalized in item_stat_normalized or item_stat_normalized in config_stat_normalized:
                        stat_matches = True
                        if debug:
                            print(f"  [DEBUG] ✓ Stat encontrado: {config_stat_normalized} em {item_stat_normalized} (original: {item_stat})")
                        break
                
                if stat_matches:
                    break
            
            if debug:
                print(f"  [DEBUG] Stats configurados: {config_stats} -> normalizados: {config_stats_normalized}")
                print(f"  [DEBUG] Stat encontrado: {stat_matches}")
        else:
            # Se não há filtro de stat, considera como match
            stat_matches = True
        
        # Verifica qualidade de affix
        if has_affix_quality_filter:
            config_affix_qualities = [q.lower() for q in self.config['affix_quality']]
            if item.affix_quality:
                affix_quality_matches = item.affix_quality.lower() in config_affix_qualities
            else:
                # Se o item não tem qualidade de affix e há filtro, não corresponde
                affix_quality_matches = False
            
            if debug:
                print(f"  [DEBUG] Affix Quality do item: {item.affix_quality}")
                print(f"  [DEBUG] Affix Qualities configuradas: {self.config['affix_quality']}")
                print(f"  [DEBUG] Affix Quality match: {affix_quality_matches}")
        else:
            # Se não há filtro de affix quality, considera como match
            affix_quality_matches = True
        
        # Aplica a lógica do modo de filtro
        # Stats primários são sempre obrigatórios (AND)
        # Affix quality é sempre obrigatório se configurado (AND)
        # Outros stats e slots seguem o filter_mode
        if filter_mode == 'OR':
            # OR: slot OU outros stats (mas primários e affix quality são sempre obrigatórios)
            result = primary_stat_matches and affix_quality_matches and (slot_matches or stat_matches)
            if debug:
                print(f"  [DEBUG] Modo OR: Primário={primary_stat_matches} E Affix={affix_quality_matches} E (Slot={slot_matches} OU Stat={stat_matches}) = {result}")
        else:
            # AND: slot E outros stats E affix quality (e primários são sempre obrigatórios)
            result = primary_stat_matches and affix_quality_matches and slot_matches and stat_matches
            if debug:
                print(f"  [DEBUG] Modo AND: Primário={primary_stat_matches} E Affix={affix_quality_matches} E Slot={slot_matches} E Stat={stat_matches} = {result}")
        
        if result:
            if debug:
                print(f"  [DEBUG] ✓ Item corresponde aos filtros!")
        else:
            if debug:
                print(f"  [DEBUG] ❌ Item não corresponde aos filtros")
        
        return result
    
    def fetch_items(self) -> List[Item]:
        """Busca itens da página de trade"""
        url = self.build_url()
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Debug: mostra status da requisição
            if self.config.get('debug', False):
                print(f"  [DEBUG] Status da requisição: {response.status_code}")
                print(f"  [DEBUG] Tamanho da resposta: {len(response.text)} bytes")
            
            soup = BeautifulSoup(response.text, 'html.parser')
            items = []
            
            # Encontra todos os cards de itens
            item_cards = soup.find_all('div', class_='entity-card')
            
            if not item_cards:
                # Tenta encontrar de outra forma
                item_cards = soup.find_all('div', id=re.compile(r'listing-\d+'))
            
            if self.config.get('debug', False):
                print(f"  [DEBUG] Cards encontrados: {len(item_cards)}")
            
            for card in item_cards:
                try:
                    # ID do listing
                    listing_id = card.get('id', '').replace('listing-', '')
                    if not listing_id:
                        continue
                    
                    # Nome do item
                    name_elem = card.find('h3', class_=re.compile('quality-'))
                    if not name_elem:
                        continue
                    name = name_elem.get_text(strip=True)
                    
                    # Slot
                    slot = self.detect_slot(name)
                    
                    # Info do item (level, stats, seller)
                    info_elem = card.find('p', class_='text-text-muted')
                    if not info_elem:
                        continue
                    
                    # Extrai qualidade de affix (se presente)
                    affix_quality = None
                    affix_quality_spans = info_elem.find_all('span', class_='text-gold')
                    for span in affix_quality_spans:
                        span_text = span.get_text(strip=True)
                        # Verifica se é uma qualidade de affix conhecida
                        if span_text in ['Fine', 'Pristine', 'Superior', 'Exquisite']:
                            affix_quality = span_text
                            break
                    
                    # Extrai stats dos spans coloridos dentro do parágrafo
                    stats = []
                    stat_spans = info_elem.find_all('span', class_=re.compile(r'text-'))
                    for span in stat_spans:
                        span_text = span.get_text(strip=True)
                        # Remove espaços extras e normaliza
                        span_text = ' '.join(span_text.split())
                        # Ignora spans que são qualidade de affix
                        if span_text not in ['Fine', 'Pristine', 'Superior', 'Exquisite']:
                            if span_text.startswith('+'):
                                stats.append(span_text)
                    
                    info_text = info_elem.get_text()
                    
                    # Item level
                    level_match = re.search(r'iLvl\s+(\d+)', info_text)
                    item_level = level_match.group(1) if level_match else "?"
                    
                    # Stats (se não foram extraídos dos spans, tenta parsear do texto)
                    if not stats:
                        stats = self.parse_stats(info_text)
                    
                    # Seller
                    seller_match = re.search(r'by\s+(\w+)', info_text)
                    seller = seller_match.group(1) if seller_match else "Unknown"
                    
                    # Preço
                    price_elem = card.find('div', class_='text-gold')
                    price = price_elem.get_text(strip=True) if price_elem else "?"
                    
                    # Tempo restante
                    time_elem = card.find('div', class_='text-text-muted')
                    time_left = ""
                    if time_elem:
                        time_text = time_elem.get_text(strip=True)
                        if 'left' in time_text or 'day' in time_text or 'hour' in time_text:
                            time_left = time_text
                    
                    # URL
                    link_elem = card.find('a', href=re.compile(r'/trade/\d+'))
                    url_path = link_elem['href'] if link_elem else f"/trade/{listing_id}"
                    full_url = f"https://dreadmystdb.com{url_path}"
                    
                    item = Item(
                        listing_id=listing_id,
                        name=name,
                        item_level=item_level,
                        stats=stats,
                        price=price,
                        seller=seller,
                        time_left=time_left,
                        url=full_url,
                        slot=slot,
                        affix_quality=affix_quality
                    )
                    
                    items.append(item)
                    
                except Exception as e:
                    print(f"Erro ao processar item: {e}", file=sys.stderr)
                    continue
            
            return items
            
        except requests.RequestException as e:
            print(f"Erro ao buscar itens: {e}", file=sys.stderr)
            return []
        except Exception as e:
            print(f"Erro inesperado: {e}", file=sys.stderr)
            return []
    
    def alert(self, item: Item):
        """Envia alerta sobre item encontrado"""
        alert_method = self.config.get('alert_method', 'console')
        
        affix_quality_text = f"Qualidade Affix: {item.affix_quality}" if item.affix_quality else "Qualidade Affix: Nenhuma"
        message = f"""
{'='*60}
🎯 ITEM ENCONTRADO! 🎯
{'='*60}
Nome: {item.name}
Slot: {item.slot or 'Desconhecido'}
{affix_quality_text}
Item Level: {item.item_level}
Stats: {', '.join(item.stats)}
Preço: {item.price}
Vendedor: {item.seller}
Tempo restante: {item.time_left}
URL: {item.url}
{'='*60}
"""
        
        if alert_method in ['console', 'both']:
            print(message)
        
        if alert_method in ['file', 'both']:
            log_file = self.config.get('log_file', 'alerts.log')
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(message)
                f.write("\n")
    
    def run(self):
        """Executa o monitor em loop"""
        print("🤖 Bot de Monitoramento DreadmystDB iniciado!")
        print(f"📋 Configuração carregada:")
        print(json.dumps(self.config, indent=2, ensure_ascii=False))
        print(f"\n🔗 URL monitorada: {self.build_url()}")
        print(f"⏱️  Intervalo de verificação: {self.config.get('check_interval', 30)} segundos")
        
        # Mostra resumo dos filtros
        if self.config.get('slots'):
            print(f"📦 Slots filtrados: {', '.join(self.config['slots'])}")
        if self.config.get('stats'):
            print(f"⚡ Stats filtrados: {', '.join(self.config['stats'])}")
        
        print("\n" + "="*60)
        print("Aguardando novos itens...")
        print("="*60 + "\n")
        
        check_interval = self.config.get('check_interval', 30)
        
        try:
            while True:
                items = self.fetch_items()
                
                if items:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Verificando {len(items)} itens...")
                    
                    # Modo debug se configurado
                    debug_mode = self.config.get('debug', False)
                    
                    new_items_found = 0
                    items_checked = 0
                    items_already_seen = 0
                    for item in items:
                        # Verifica se já vimos este item
                        if item.listing_id in self.seen_items:
                            items_already_seen += 1
                            if debug_mode:
                                print(f"  [DEBUG] Item já visto: {item.name} (ID: {item.listing_id})")
                            continue
                        
                        items_checked += 1
                        
                        # Verifica se corresponde aos filtros
                        if self.item_matches_filters(item, debug=debug_mode):
                            self.alert(item)
                            self.seen_items.add(item.listing_id)
                            new_items_found += 1
                        elif debug_mode:
                            print(f"  [DEBUG] Item não corresponde aos filtros: {item.name}")
                    
                    if debug_mode:
                        print(f"  [DEBUG] Total de itens: {len(items)}")
                        print(f"  [DEBUG] Itens já vistos: {items_already_seen}")
                        print(f"  [DEBUG] Itens novos verificados: {items_checked}")
                        print(f"  [DEBUG] Itens correspondentes: {new_items_found}")
                    
                    if new_items_found == 0:
                        if items_checked > 0:
                            print(f"  ⚠ Nenhum item novo correspondente aos filtros (verificados {items_checked} novos itens, {items_already_seen} já vistos).")
                            if not debug_mode:
                                print(f"  💡 Dica: Ative 'debug: true' no config.json para ver detalhes")
                        else:
                            print(f"  ✓ Nenhum item novo.")
                    else:
                        print(f"  ✓ {new_items_found} novo(s) item(ns) encontrado(s)!")
                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠ Nenhum item encontrado ou erro na requisição.")
                
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Bot interrompido pelo usuário.")
        except Exception as e:
            print(f"\n❌ Erro fatal: {e}", file=sys.stderr)
            raise


def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Bot de Monitoramento DreadmystDB Trade')
    parser.add_argument('-c', '--config', default='config.json',
                       help='Arquivo de configuração (padrão: config.json)')
    
    args = parser.parse_args()
    
    monitor = TradeMonitor(args.config)
    monitor.run()


if __name__ == '__main__':
    main()

