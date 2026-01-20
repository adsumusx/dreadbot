#!/usr/bin/env python3
"""
Interface Gráfica para o Bot de Monitoramento DreadmystDB
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import threading
import sys
import os
import time
import webbrowser
from pathlib import Path
from datetime import datetime
try:
    import winsound  # Para Windows
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False
import platform

# Importa o bot
from bot import TradeMonitor, Item
from license import LicenseManager


class BotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Bot DreadmystDB - Monitor de Trade")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # Variáveis
        self.monitor = None
        self.monitor_thread = None
        self.is_running = False
        self.config_file = "config.json"
        self.license_manager = LicenseManager()
        
        # Verifica licença antes de continuar
        if not self.check_license():
            return  # A janela será fechada pelo check_license
        
        # Carrega configuração
        self.load_config()
        
        # Cria interface
        self.create_widgets()
        
        # Atualiza interface com valores carregados
        self.update_interface_from_config()
    
    def check_license(self) -> bool:
        """
        Verifica se a licença é válida. Se não for, mostra diálogo e fecha o app.
        
        Returns:
            True se licença válida, False caso contrário
        """
        is_valid, message = self.license_manager.load_license()
        
        if not is_valid:
            # Mostra diálogo de licença
            license_window = tk.Toplevel(self.root)
            license_window.title("Licença Necessária")
            license_window.geometry("500x400")
            license_window.resizable(False, False)
            license_window.transient(self.root)
            license_window.grab_set()
            
            # Centraliza a janela
            license_window.update_idletasks()
            x = (license_window.winfo_screenwidth() // 2) - (500 // 2)
            y = (license_window.winfo_screenheight() // 2) - (400 // 2)
            license_window.geometry(f"500x400+{x}+{y}")
            
            # Frame principal
            main_frame = ttk.Frame(license_window, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Título
            title_label = ttk.Label(
                main_frame,
                text="🔐 Licença Necessária",
                font=("Arial", 16, "bold")
            )
            title_label.pack(pady=(0, 20))
            
            # Mensagem
            msg_text = f"""
{message}

Para usar este software, você precisa de uma licença válida.

Por favor, entre em contato com o desenvolvedor para obter uma chave de licença.

A chave deve ser salva em um arquivo chamado 'license.key' no mesmo diretório do executável.
"""
            msg_label = ttk.Label(
                main_frame,
                text=msg_text,
                justify=tk.LEFT,
                wraplength=450
            )
            msg_label.pack(pady=10)
            
            # Campo para inserir chave
            ttk.Label(main_frame, text="Cole sua chave de licença aqui:", font=("Arial", 10, "bold")).pack(pady=(20, 5))
            
            key_text = scrolledtext.ScrolledText(main_frame, height=6, width=50, wrap=tk.WORD)
            key_text.pack(pady=5, fill=tk.BOTH, expand=True)
            key_text.focus()
            
            # Frame de botões
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(pady=20)
            
            def validate_and_save():
                license_key = key_text.get("1.0", tk.END).strip()
                if not license_key:
                    messagebox.showerror("Erro", "Por favor, cole sua chave de licença.")
                    return
                
                is_valid, msg = self.license_manager.validate_license_key(license_key)
                if is_valid:
                    # Salva a licença (valida novamente internamente para garantir lock)
                    if self.license_manager.save_license(license_key):
                        messagebox.showinfo("Sucesso", f"Licença válida e ativada!\n\n{msg}\n\n⚠ Esta licença agora está vinculada a esta máquina e não pode ser usada em outra.")
                        license_window.destroy()
                        # Recarrega a interface
                        self.root.after(100, lambda: self.__init__(self.root))
                    else:
                        messagebox.showerror("Erro", "Erro ao salvar licença.")
                else:
                    messagebox.showerror("Licença Inválida", f"Chave inválida:\n\n{msg}")
            
            def exit_app():
                self.root.quit()
                self.root.destroy()
            
            # Botões
            validate_button = ttk.Button(button_frame, text="Validar e Salvar", command=validate_and_save)
            validate_button.pack(side=tk.LEFT, padx=5)
            
            exit_button = ttk.Button(button_frame, text="Sair", command=exit_app)
            exit_button.pack(side=tk.LEFT, padx=5)
            
            # Bind Enter no campo de texto (Enter simples, não Ctrl+Enter)
            def on_enter(event):
                validate_and_save()
                return "break"  # Previne comportamento padrão (nova linha)
            
            key_text.bind('<Return>', on_enter)
            key_text.bind('<KP_Enter>', on_enter)  # Enter do teclado numérico
            
            # Foca na janela
            license_window.lift()
            license_window.attributes('-topmost', True)
            license_window.after_idle(license_window.attributes, '-topmost', False)
            
            # Aguarda o usuário
            license_window.wait_window()
            
            # Se chegou aqui e ainda não tem licença válida, fecha o app
            if not self.license_manager.is_license_valid():
                self.root.quit()
                self.root.destroy()
                return False
        
        else:
            # Licença válida - mostra informações na barra de status se houver
            info = self.license_manager.get_license_info()
            if info:
                expiration_date = datetime.strptime(info.get('expiration_date'), "%Y-%m-%d %H:%M:%S")
                days_left = (expiration_date - datetime.now()).days
                if days_left <= 7:
                    messagebox.showwarning(
                        "Licença Expirando",
                        f"Sua licença expira em {days_left} dia(s).\n\nData de expiração: {info.get('expiration_date')}"
                    )
        
        return True
    
    def load_config(self):
        """Carrega configuração do arquivo"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            else:
                self.config = self.get_default_config()
                self.save_config()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar configuração: {e}")
            self.config = self.get_default_config()
    
    def get_default_config(self):
        """Retorna configuração padrão"""
        return {
            "quality": [5, 6],
            "min_level": 24,
            "max_level": None,
            "min_price": None,
            "max_price": None,
            "primary_stats": [],
            "primary_stats_mode": "OR",  # OR = um dos, AND = todos
            "stats": [],
            "slots": [],
            "affix_quality": [],
            "check_interval": 30,
            "alert_method": "console",
            "log_file": "alerts.log",
            "debug": False,
            "filter_mode": "AND",
            "sound_alert": True
        }
    
    def save_config(self):
        """Salva configuração no arquivo"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar configuração: {e}")
            return False
    
    def create_widgets(self):
        """Cria os widgets da interface"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configuração do grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # Título
        title_label = ttk.Label(main_frame, text="🤖 Bot de Monitoramento DreadmystDB", 
                                font=("Arial", 16, "bold"))
        title_label.grid(row=row, column=0, columnspan=3, pady=(0, 20))
        row += 1
        
        # === QUALIDADE ===
        ttk.Label(main_frame, text="Qualidade do Item:", font=("Arial", 10, "bold")).grid(
            row=row, column=0, sticky=tk.W, pady=5)
        row += 1
        
        quality_frame = ttk.Frame(main_frame)
        quality_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        self.quality_vars = {}
        quality_options = [
            (1, "Junk"), (2, "Normal"), (3, "Radiant"),
            (4, "Blessed"), (5, "Holy"), (6, "Godly")
        ]
        
        for i, (value, name) in enumerate(quality_options):
            var = tk.BooleanVar()
            self.quality_vars[value] = var
            ttk.Checkbutton(quality_frame, text=name, variable=var).grid(
                row=0, column=i, padx=5, sticky=tk.W)
        
        row += 1
        
        # === NÍVEL ===
        ttk.Label(main_frame, text="Nível do Item:", font=("Arial", 10, "bold")).grid(
            row=row, column=0, sticky=tk.W, pady=5)
        row += 1
        
        level_frame = ttk.Frame(main_frame)
        level_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(level_frame, text="Mínimo:").grid(row=0, column=0, padx=5)
        self.min_level_var = tk.StringVar()
        ttk.Spinbox(level_frame, from_=1, to=25, textvariable=self.min_level_var, width=10).grid(
            row=0, column=1, padx=5)
        
        ttk.Label(level_frame, text="Máximo:").grid(row=0, column=2, padx=5)
        self.max_level_var = tk.StringVar()
        ttk.Spinbox(level_frame, from_=1, to=25, textvariable=self.max_level_var, width=10).grid(
            row=0, column=3, padx=5)
        
        row += 1
        
        # === PREÇO ===
        ttk.Label(main_frame, text="Preço (Gold):", font=("Arial", 10, "bold")).grid(
            row=row, column=0, sticky=tk.W, pady=5)
        row += 1
        
        price_frame = ttk.Frame(main_frame)
        price_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(price_frame, text="Mínimo:").grid(row=0, column=0, padx=5)
        self.min_price_var = tk.StringVar()
        ttk.Entry(price_frame, textvariable=self.min_price_var, width=15).grid(
            row=0, column=1, padx=5)
        
        ttk.Label(price_frame, text="Máximo:").grid(row=0, column=2, padx=5)
        self.max_price_var = tk.StringVar()
        ttk.Entry(price_frame, textvariable=self.max_price_var, width=15).grid(
            row=0, column=3, padx=5)
        
        row += 1
        
        # === ATRIBUTOS PRIMÁRIOS (OBRIGATÓRIOS) ===
        primary_header_frame = ttk.Frame(main_frame)
        primary_header_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(primary_header_frame, text="Atributos Primários (Obrigatórios):", 
                 font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W)
        
        # Checkbox para escolher modo (um dos / todos)
        self.primary_stats_mode_var = tk.StringVar(value="OR")  # OR = um dos, AND = todos
        primary_mode_frame = ttk.Frame(primary_header_frame)
        primary_mode_frame.grid(row=0, column=1, sticky=tk.W, padx=(20, 0))
        
        ttk.Radiobutton(primary_mode_frame, text="Um dos selecionados (OR)", 
                       variable=self.primary_stats_mode_var, value="OR").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(primary_mode_frame, text="Todos selecionados (AND)", 
                       variable=self.primary_stats_mode_var, value="AND").pack(side=tk.LEFT, padx=5)
        
        row += 1
        
        primary_stats_frame = ttk.Frame(main_frame)
        primary_stats_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Atributos primários
        primary_stats = ["Agility", "Strength", "Intelligence", "Willpower", "Courage"]
        
        self.primary_stats_vars = {}
        cols = 5
        for i, stat in enumerate(primary_stats):
            var = tk.BooleanVar()
            self.primary_stats_vars[stat] = var
            ttk.Checkbutton(primary_stats_frame, text=stat, variable=var).grid(
                row=i//cols, column=i%cols, padx=5, sticky=tk.W)
        
        row += 1
        
        # === OUTROS ATRIBUTOS (OPCIONAIS) ===
        ttk.Label(main_frame, text="Outros Atributos (Opcionais):", 
                 font=("Arial", 10, "bold")).grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Label(main_frame, text="Item deve ter pelo menos um destes (se selecionados)", 
                 font=("Arial", 8), foreground="gray").grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        stats_frame = ttk.Frame(main_frame)
        stats_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Lista de outros stats (sem os primários)
        other_stats = [
            "Armor Value", "Axes", "Block Rating", "Daggers", "Dodge Rating", 
            "Health", "Maces", "Mana", "Meditate", "Melee Critical", "Melee Speed", 
            "Ranged", "Ranged Critical", "Ranged Speed", "Ranged Weapon Value", 
            "Regeneration", "Resist Fire", "Resist Frost", "Resist Holy", "Resist Shadow",
            "Shields", "Spell Critical", "Staves", "Swords", "Wands", "Weapon Value"
        ]
        
        self.stats_vars = {}
        cols = 4
        for i, stat in enumerate(other_stats):
            var = tk.BooleanVar()
            self.stats_vars[stat] = var
            ttk.Checkbutton(stats_frame, text=stat, variable=var).grid(
                row=i//cols, column=i%cols, padx=5, sticky=tk.W)
        
        # Campo para stats customizados
        ttk.Label(main_frame, text="Outros atributos (separados por vírgula):").grid(
            row=row+1, column=0, sticky=tk.W, pady=5)
        self.custom_stats_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.custom_stats_var, width=50).grid(
            row=row+1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        row += 2
        
        # === SLOTS ===
        ttk.Label(main_frame, text="Slots de Equipamento:", font=("Arial", 10, "bold")).grid(
            row=row, column=0, sticky=tk.W, pady=5)
        row += 1
        
        slots_frame = ttk.Frame(main_frame)
        slots_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        slot_options = [
            "head", "necklace", "chest", "waist", "legs", 
            "feet", "hands", "ring", "main hand", "off hand", "ranged"
        ]
        
        self.slots_vars = {}
        cols = 4
        for i, slot in enumerate(slot_options):
            var = tk.BooleanVar()
            self.slots_vars[slot] = var
            ttk.Checkbutton(slots_frame, text=slot.title(), variable=var).grid(
                row=i//cols, column=i%cols, padx=5, sticky=tk.W)
        
        row += 1
        
        # === QUALIDADE DE AFFIX ===
        ttk.Label(main_frame, text="Qualidade de Affix:", font=("Arial", 10, "bold")).grid(
            row=row, column=0, sticky=tk.W, pady=5)
        row += 1
        
        affix_quality_frame = ttk.Frame(main_frame)
        affix_quality_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        affix_quality_options = ["Fine", "Pristine", "Superior", "Exquisite"]
        
        self.affix_quality_vars = {}
        cols = 4
        for i, quality in enumerate(affix_quality_options):
            var = tk.BooleanVar()
            self.affix_quality_vars[quality] = var
            ttk.Checkbutton(affix_quality_frame, text=quality, variable=var).grid(
                row=i//cols, column=i%cols, padx=5, sticky=tk.W)
        
        row += 1
        
        # === CONFIGURAÇÕES AVANÇADAS ===
        ttk.Label(main_frame, text="Configurações:", font=("Arial", 10, "bold")).grid(
            row=row, column=0, sticky=tk.W, pady=5)
        row += 1
        
        config_frame = ttk.Frame(main_frame)
        config_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(config_frame, text="Intervalo (segundos):").grid(row=0, column=0, padx=5)
        self.interval_var = tk.StringVar(value="30")
        ttk.Spinbox(config_frame, from_=10, to=300, textvariable=self.interval_var, width=10).grid(
            row=0, column=1, padx=5)
        
        self.filter_mode_var = tk.StringVar(value="AND")
        ttk.Label(config_frame, text="Modo:").grid(row=0, column=2, padx=5)
        filter_combo = ttk.Combobox(config_frame, textvariable=self.filter_mode_var, 
                                    values=["AND", "OR"], width=10, state="readonly")
        filter_combo.grid(row=0, column=3, padx=5)
        
        self.sound_alert_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(config_frame, text="Alerta Sonoro", variable=self.sound_alert_var).grid(
            row=0, column=4, padx=5)
        
        row += 1
        
        # === ÁREA DE LOG ===
        ttk.Label(main_frame, text="Log de Atividades:", font=("Arial", 10, "bold")).grid(
            row=row, column=0, sticky=tk.W, pady=5)
        row += 1
        
        self.log_text = scrolledtext.ScrolledText(main_frame, height=10, width=80)
        self.log_text.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        main_frame.rowconfigure(row, weight=1)
        row += 1
        
        # === BOTÕES ===
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=3, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="▶ Iniciar Monitoramento", 
                                       command=self.start_monitoring, width=20)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="⏹ Parar", 
                                     command=self.stop_monitoring, width=20, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="💾 Salvar Configuração", 
                  command=self.save_config_from_ui).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="🔄 Carregar Configuração", 
                  command=self.load_config_to_ui).pack(side=tk.LEFT, padx=5)
    
    def update_interface_from_config(self):
        """Atualiza a interface com os valores do config"""
        # Qualidade
        for value, var in self.quality_vars.items():
            var.set(value in self.config.get('quality', []))
        
        # Nível
        self.min_level_var.set(str(self.config.get('min_level', '')) if self.config.get('min_level') else '')
        self.max_level_var.set(str(self.config.get('max_level', '')) if self.config.get('max_level') else '')
        
        # Preço
        self.min_price_var.set(str(self.config.get('min_price', '')) if self.config.get('min_price') else '')
        self.max_price_var.set(str(self.config.get('max_price', '')) if self.config.get('max_price') else '')
        
        # Stats primários
        config_primary_stats = self.config.get('primary_stats', [])
        primary_reverse_mapping = {
            "AGI": "Agility",
            "STR": "Strength",
            "INT": "Intelligence",
            "WIL": "Willpower",
            "COU": "Courage"
        }
        
        mapped_primary = []
        for stat in config_primary_stats:
            full_name = primary_reverse_mapping.get(stat, stat)
            if full_name in self.primary_stats_vars:
                mapped_primary.append(full_name)
        
        for stat, var in self.primary_stats_vars.items():
            var.set(stat in mapped_primary)
        
        # Modo dos atributos primários (OR/AND)
        primary_mode = self.config.get('primary_stats_mode', 'OR')
        self.primary_stats_mode_var.set(primary_mode)
        
        # Outros stats - mapeia de volta os nomes normalizados para os nomes completos
        config_stats = self.config.get('stats', [])
        
        # Mapeamento reverso (de abreviações para nomes completos)
        reverse_mapping = {
            "HP": "Health",
            "Wpn Dmg": "Weapon Value",
            "Spell Crit": "Spell Critical",
            "Melee Crit": "Melee Critical",
            "Ranged Wpn": "Ranged Weapon Value",
            "Fire Res": "Resist Fire",
            "Frost Res": "Resist Frost",
            "Holy Res": "Resist Holy",
            "Shadow Res": "Resist Shadow"
        }
        
        # Mapeia stats configurados para nomes da interface
        mapped_stats = []
        custom_stats = []
        for stat in config_stats:
            # Tenta mapear de volta
            full_name = reverse_mapping.get(stat, stat)
            if full_name in self.stats_vars:
                mapped_stats.append(full_name)
            else:
                # Se não está na lista, é customizado
                custom_stats.append(stat)
        
        # Marca os stats na interface
        for stat, var in self.stats_vars.items():
            var.set(stat in mapped_stats)
        
        # Custom stats
        self.custom_stats_var.set(', '.join(custom_stats))
        
        # Slots
        config_slots = self.config.get('slots', [])
        for slot, var in self.slots_vars.items():
            var.set(slot in config_slots)
        
        # Qualidade de Affix
        config_affix_quality = self.config.get('affix_quality', [])
        for quality, var in self.affix_quality_vars.items():
            var.set(quality in config_affix_quality)
        
        # Configurações
        self.interval_var.set(str(self.config.get('check_interval', 30)))
        self.filter_mode_var.set(self.config.get('filter_mode', 'AND'))
        self.sound_alert_var.set(self.config.get('sound_alert', True))
    
    def get_config_from_ui(self):
        """Obtém a configuração da interface"""
        config = {}
        
        # Qualidade
        config['quality'] = [v for v, var in self.quality_vars.items() if var.get()]
        
        # Nível
        min_level = self.min_level_var.get().strip()
        config['min_level'] = int(min_level) if min_level else None
        max_level = self.max_level_var.get().strip()
        config['max_level'] = int(max_level) if max_level else None
        
        # Preço
        min_price = self.min_price_var.get().strip()
        config['min_price'] = int(min_price) if min_price else None
        max_price = self.max_price_var.get().strip()
        config['max_price'] = int(max_price) if max_price else None
        
        # Stats primários - normaliza para os nomes que o bot espera
        primary_stats = [s for s, var in self.primary_stats_vars.items() if var.get()]
        primary_stat_normalization = {
            "Agility": "AGI",
            "Strength": "STR",
            "Intelligence": "INT",
            "Willpower": "WIL",
            "Courage": "COU"
        }
        
        normalized_primary = []
        for stat in primary_stats:
            normalized = primary_stat_normalization.get(stat, stat)
            if normalized not in normalized_primary:
                normalized_primary.append(normalized)
        
        config['primary_stats'] = normalized_primary
        config['primary_stats_mode'] = self.primary_stats_mode_var.get()  # OR ou AND
        
        # Outros stats - normaliza para os nomes que o bot espera
        stats = [s for s, var in self.stats_vars.items() if var.get()]
        custom_stats = [s.strip() for s in self.custom_stats_var.get().split(',') if s.strip()]
        
        # Normaliza alguns nomes para as abreviações que o bot reconhece melhor
        normalized_stats = []
        stat_normalization = {
            "Health": "HP",
            "Weapon Value": "Wpn Dmg",
            "Spell Critical": "Spell Crit",
            "Melee Critical": "Melee Crit",
            "Ranged Weapon Value": "Ranged Wpn",
            "Resist Fire": "Fire Res",
            "Resist Frost": "Frost Res",
            "Resist Holy": "Holy Res",
            "Resist Shadow": "Shadow Res"
        }
        
        for stat in stats + custom_stats:
            # Tenta normalizar, senão usa o nome original
            normalized = stat_normalization.get(stat, stat)
            if normalized not in normalized_stats:
                normalized_stats.append(normalized)
        
        config['stats'] = normalized_stats
        
        # Slots
        config['slots'] = [s for s, var in self.slots_vars.items() if var.get()]
        
        # Configurações
        config['check_interval'] = int(self.interval_var.get())
        config['filter_mode'] = self.filter_mode_var.get()
        config['sound_alert'] = self.sound_alert_var.get()
        config['alert_method'] = 'console'
        config['log_file'] = 'alerts.log'
        config['debug'] = False
        
        return config
    
    def save_config_from_ui(self):
        """Salva a configuração da interface"""
        self.config = self.get_config_from_ui()
        if self.save_config():
            self.log("✓ Configuração salva com sucesso!")
            messagebox.showinfo("Sucesso", "Configuração salva com sucesso!")
    
    def load_config_to_ui(self):
        """Carrega configuração e atualiza interface"""
        self.load_config()
        self.update_interface_from_config()
        self.log("✓ Configuração carregada!")
    
    def log(self, message):
        """Adiciona mensagem ao log"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def play_sound(self):
        """Toca som de alerta"""
        try:
            if platform.system() == "Windows" and HAS_WINSOUND:
                # Toca um beep do sistema Windows (mais longo e chamativo)
                winsound.Beep(1000, 500)  # Frequência 1000Hz, duração 500ms
                time.sleep(0.1)
                winsound.Beep(1500, 300)  # Segundo beep mais agudo
                time.sleep(0.1)
                winsound.Beep(1000, 500)  # Terceiro beep para garantir que foi ouvido
            elif platform.system() == "Linux":
                # Para Linux, tenta usar beep ou speaker-test
                os.system('beep -f 1000 -l 500 2>/dev/null || speaker-test -t sine -f 1000 -l 100 2>/dev/null || true')
            elif platform.system() == "Darwin":  # macOS
                os.system('say "Item encontrado" 2>/dev/null || afplay /System/Library/Sounds/Glass.aiff 2>/dev/null || true')
            else:
                # Fallback: apenas print
                print('\a')  # Bell character
        except Exception as e:
            self.log(f"⚠ Erro ao tocar som: {e}")
            # Tenta fallback mesmo em caso de erro
            try:
                print('\a')
            except:
                pass
    
    def alert_item_found(self, item: Item):
        """Alerta quando item é encontrado"""
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
        self.log(message)
        self.log(f"🔗 URL completa: {item.url}")
        
        # Alerta sonoro
        sound_enabled = self.config.get('sound_alert', True)
        self.log(f"🔊 Alerta sonoro configurado: {sound_enabled}")
        if sound_enabled:
            try:
                self.log("🔊 Tentando tocar som...")
                self.play_sound()
                self.log("🔊 Alerta sonoro tocado com sucesso!")
            except Exception as e:
                self.log(f"⚠ Erro ao tocar som: {e}")
                import traceback
                self.log(f"⚠ Traceback: {traceback.format_exc()}")
        
        # Mostra popup
        popup = tk.Toplevel(self.root)
        popup.title("🎯 Item Encontrado!")
        popup.geometry("600x500")
        
        # Frame principal
        main_frame = tk.Frame(popup)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Texto do item
        text_widget = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, padx=10, pady=10, height=15)
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        # Remove a linha da URL da mensagem para adicionar como botão
        message_without_url = message.replace(f"URL: {item.url}\n", "")
        text_widget.insert(tk.END, message_without_url)
        text_widget.config(state=tk.DISABLED)
        
        # Frame para botões
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Botão para abrir URL
        if item.url and item.url.strip():
            def open_url():
                import webbrowser
                try:
                    webbrowser.open(item.url)
                    self.log(f"🌐 Abrindo URL: {item.url}")
                except Exception as e:
                    self.log(f"⚠ Erro ao abrir URL: {e}")
                    messagebox.showerror("Erro", f"Erro ao abrir URL:\n{item.url}\n\n{e}")
            
            url_button = ttk.Button(button_frame, text="🔗 Abrir Link do Item", command=open_url)
            url_button.pack(side=tk.LEFT, padx=5)
        else:
            # Mostra que não há URL disponível
            no_url_label = tk.Label(button_frame, text="⚠ URL não disponível", fg="red")
            no_url_label.pack(side=tk.LEFT, padx=5)
            self.log(f"⚠ ATENÇÃO: Item {item.name} não tem URL! (item.url = {repr(item.url)})")
        
        # Botão fechar
        close_button = ttk.Button(button_frame, text="Fechar", command=popup.destroy)
        close_button.pack(side=tk.RIGHT, padx=5)
        
        # Faz o popup aparecer na frente
        popup.lift()
        popup.attributes('-topmost', True)
        popup.after_idle(popup.attributes, '-topmost', False)
        
        # Foca na janela
        popup.focus_force()
    
    def start_monitoring(self):
        """Inicia o monitoramento"""
        if self.is_running:
            return
        
        # Salva configuração atual
        self.config = self.get_config_from_ui()
        self.save_config()
        
        # Cria monitor
        try:
            self.monitor = TradeMonitor(self.config_file)
            # Sobrescreve o método alert do monitor para usar nossa interface
            def custom_alert(item):
                # Log de debug
                print(f"[DEBUG] custom_alert chamado para: {item.name}, URL: {item.url}")
                # Usa lambda com default para capturar corretamente o item
                self.root.after(0, lambda i=item: self.alert_item_found(i))
            self.monitor.alert = custom_alert
            
            self.is_running = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            
            self.log("🤖 Bot iniciado!")
            primary = self.config.get('primary_stats', [])
            stats = self.config.get('stats', [])
            self.log(f"📋 Monitorando: Quality={self.config.get('quality')}, "
                    f"Level={self.config.get('min_level')}+")
            if primary:
                self.log(f"⭐ Atributos Primários (obrigatórios): {primary}")
            if stats:
                self.log(f"⚡ Outros Atributos: {stats}")
            if self.config.get('slots'):
                self.log(f"📦 Slots: {self.config.get('slots')}")
            self.log(f"⏱️  Intervalo: {self.config.get('check_interval')} segundos")
            self.log("="*60)
            
            # Inicia thread de monitoramento customizado
            self.monitor_thread = threading.Thread(target=self.run_monitor, daemon=True)
            self.monitor_thread.start()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao iniciar bot: {e}")
            self.log(f"❌ Erro: {e}")
            self.is_running = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
    
    def run_monitor(self):
        """Executa o monitor em thread separada"""
        import time
        try:
            check_interval = self.config.get('check_interval', 30)
            
            while self.is_running:
                items = self.monitor.fetch_items()
                
                if items:
                    self.root.after(0, lambda n=len(items): self.log(
                        f"[{datetime.now().strftime('%H:%M:%S')}] Verificando {n} itens..."))
                    
                    new_items_found = 0
                    for item in items:
                        if item.listing_id in self.monitor.seen_items:
                            continue
                        
                        if self.monitor.item_matches_filters(item):
                            # Chama o alerta (que foi sobrescrito para usar a GUI)
                            self.monitor.alert(item)
                            self.monitor.seen_items.add(item.listing_id)
                            new_items_found += 1
                    
                    if new_items_found > 0:
                        self.root.after(0, lambda n=new_items_found: self.log(
                            f"  ✓ {n} novo(s) item(ns) encontrado(s)!"))
                    elif len(items) > 0:
                        self.root.after(0, lambda: self.log(
                            f"  ⚠ Nenhum item novo correspondente aos filtros."))
                else:
                    self.root.after(0, lambda: self.log(
                        f"[{datetime.now().strftime('%H:%M:%S')}] ⚠ Nenhum item encontrado ou erro na requisição."))
                
                # Aguarda intervalo
                for _ in range(check_interval):
                    if not self.is_running:
                        break
                    time.sleep(1)
                    
        except Exception as e:
            self.root.after(0, lambda: self.log(f"❌ Erro no monitoramento: {e}"))
            self.root.after(0, lambda: self.stop_monitoring())
    
    def stop_monitoring(self):
        """Para o monitoramento"""
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.log("⏹ Monitoramento parado.")


def main():
    root = tk.Tk()
    app = BotGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()

