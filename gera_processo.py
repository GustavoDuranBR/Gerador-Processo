import os
import sys
import random
import string # Necessário para gerar letras e números no CNPJ
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import Text, Menu
from faker import Faker
from validate_docbr import CPF, CNPJ
from datetime import datetime


fake = Faker('pt_BR')
cpf_gen = CPF()
cnpj_gen = CNPJ()

def resource_path(relative_path):
    """Obtém o caminho absoluto, compatível com o PyInstaller"""
    try:
        base_path = sys._MEIPASS  # Quando estiver no .exe
    except AttributeError:
        base_path = os.path.abspath(".")  # Quando estiver rodando o .py
    return os.path.join(base_path, relative_path)

class GeradorApp(ttk.Window):
    def __init__(self):
        super().__init__(themename="darkly")
        icon_path = resource_path("assets/icon_robot.ico")
        self.iconbitmap(icon_path)
        self.title("Gerador de Dados Fakes para Processo")
        self.geometry("600x600")
        self.resizable(False, False)

        self.resultados = []

        # =========================
        # Menu Tema
        # =========================
        self.menu_bar = ttk.Menu(self)
        self.config(menu=self.menu_bar)

        tema_menu = ttk.Menu(self.menu_bar, tearoff=0)
        tema_menu.add_command(label="Claro", command=lambda: self.mudar_tema("flatly"))
        tema_menu.add_command(label="Escuro", command=lambda: self.mudar_tema("darkly"))
        self.menu_bar.add_cascade(label="Tema", menu=tema_menu)

        # =========================
        # Layout principal
        # =========================
        self.tipo_var = ttk.StringVar(value="Judicial")
        ttk.Label(self, text="Tipo de Processo:").pack(pady=5)

        # 🔥 Ajuste recomendado: readonly (somente seleção)
        ttk.Combobox(
            self,
            textvariable=self.tipo_var,
            values=["Judicial", "CCP/NINTER"],
            state="readonly"
        ).pack()

        ttk.Label(self, text="Ano do Processo:").pack(pady=5)
        vcmd = (self.register(self.validar_ano), "%P")
        self.ano_var = ttk.Entry(self, validate="key", validatecommand=vcmd)
        self.ano_var.pack()

        ttk.Button(
            self,
            text="Gerar Dados",
            command=self.gerar_dados,
            bootstyle="success"
        ).pack(pady=10)

        self.campos = {}
        self.frame_resultado = ttk.Frame(self)
        self.frame_resultado.pack(pady=10, fill="x", padx=20)

        self.protocol("WM_DELETE_WINDOW", self.fechar_app)

    # ======================================================
    # VALIDAÇÃO / TEMA
    # ======================================================
    def validar_ano(self, entrada):
        return entrada.isdigit() or entrada == ""

    def mudar_tema(self, tema):
        self.style.theme_use(tema)
        self.atualizar_cores()

    def atualizar_cores(self):
        estilo_atual = self.style.theme.name
        cor_texto = "white" if "dark" in estilo_atual else "black"
        for campo in self.campos.values():
            campo.configure(foreground=cor_texto)

    # ======================================================
    # CORE
    # ======================================================
    def gerar_processo(self, digitos, ano):
        numero_base = ''.join([str(random.randint(0, 9)) for _ in range(digitos - 4)])
        return f"{numero_base}{ano}"

    def gerar_cnpj_alfanumerico(self, qtd_letras=2):
        """
        Gera CNPJ alfanumérico matematicamente válido com letras na raiz.
        """
        # 1. Gera uma base de 12 números (Raiz + Filial)
        base = list(''.join(random.choices(string.digits, k=12)))
        
        # 2. Injeta letras apenas na RAIZ (os 8 primeiros dígitos)
        posicoes = random.sample(range(8), k=qtd_letras)
        for pos in posicoes:
            base[pos] = random.choice(string.ascii_uppercase)
            
        base_str = ''.join(base)
        
        # 3. Função interna para calcular os DVs com a regra ASCII - 48
        def calcular_dv(cnpj_parcial):
            pesos = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
            pesos_atuais = pesos[-len(cnpj_parcial):]
            
            soma = 0
            for char, peso in zip(cnpj_parcial, pesos_atuais):
                valor = ord(char) - 48
                soma += valor * peso
                
            resto = soma % 11
            return '0' if resto < 2 else str(11 - resto)

        # 4. Calcula e anexa os dois dígitos finais
        dv1 = calcular_dv(base_str)
        dv2 = calcular_dv(base_str + dv1)
        
        cnpj_modificado = base_str + dv1 + dv2
        
        # 5. Retorna com a máscara padrão
        return f"{cnpj_modificado[:2]}.{cnpj_modificado[2:5]}.{cnpj_modificado[5:8]}/{cnpj_modificado[8:12]}-{cnpj_modificado[12:]}"

    def limpar_campos(self):
        for widget in self.frame_resultado.winfo_children():
            widget.destroy()
        self.campos.clear()

    # 🔥 botão copiar estilo CSV
    def copiar_texto(self, widget):
        self.clipboard_clear()
        self.clipboard_append(widget.get("1.0", "end-1c"))

    def gerar_dados(self):
        self.limpar_campos()
        tipo = self.tipo_var.get()
        ano = self.ano_var.get()

        if not ano.isdigit() or len(ano) != 4:
            erro = ttk.Label(
                self.frame_resultado,
                text="Ano inválido. Digite 4 dígitos.",
                foreground="red"
            )
            erro.pack()
            return

        digitos = 20 if tipo == "Judicial" else 15

        processo = self.gerar_processo(digitos, ano)
        nome = fake.name()
        # remove títulos comuns do Faker BR
        prefixos = ("Dr. ", "Dra. ", "Sr. ", "Sra. ", "Srta. ")
        for p in prefixos:
            if nome.startswith(p):
                nome = nome[len(p):]
                break
        nascimento = fake.date_of_birth(minimum_age=18, maximum_age=65).strftime("%d/%m/%Y")
        cpf = cpf_gen.generate()
        cnpj = cnpj_gen.generate()
        cnpj_alfanumerico = self.gerar_cnpj_alfanumerico()

        dados = {
            "Tipo de Processo": tipo,
            "Número do Processo": processo,
            "Nome": nome,
            "Data de Nascimento": nascimento,
            "CPF": cpf,
            "CNPJ": cnpj,
            "CNPJ Alfanumérico": cnpj_alfanumerico
        }

        texto_backup = ""

        for chave, valor in dados.items():

            linha = ttk.Frame(self.frame_resultado)
            linha.pack(fill="x", pady=2)

            ttk.Label(linha, text=chave + ":").pack(anchor="w")

            linha_input = ttk.Frame(linha)
            linha_input.pack(fill="x")

            entrada = Text(linha_input, height=1, wrap="word", width=40)
            entrada.insert("1.0", valor)
            entrada.pack(side="left", fill="x", expand=True)
            entrada.configure(state="normal")

            ttk.Button(
                linha_input,
                text="📋",
                width=3,
                command=lambda w=entrada: self.copiar_texto(w)
            ).pack(side="right", padx=4)

            # mantém menu direito + Ctrl+C original
            self.criar_menu_copia(entrada)

            self.campos[chave] = entrada
            texto_backup += f"{chave}: {valor}\n"

        self.resultados.append(texto_backup.strip())
        self.atualizar_cores()

    # ======================================================
    # COPIAR ORIGINAL (mantido)
    # ======================================================
    def criar_menu_copia(self, widget):
        menu_contexto = Menu(self, tearoff=0)
        menu_contexto.add_command(label="Copiar", command=lambda: self.copiar(widget))
        widget.bind("<Button-3>", lambda e: menu_contexto.post(e.x_root, e.y_root))
        widget.bind("<Control-c>", lambda e: self.copiar(widget))

    def copiar(self, widget):
        widget.clipboard_clear()
        widget.clipboard_append(widget.get("1.0", "end-1c"))

    # ======================================================
    # BACKUP
    # ======================================================
    def fechar_app(self):
        if self.resultados:
            if not os.path.exists("backups"):
                os.makedirs("backups")
            data = datetime.now().strftime("%Y-%m-%d")
            caminho = os.path.join("backups", f"backup_{data}.txt")
            with open(caminho, "a", encoding="utf-8") as f:
                for item in self.resultados:
                    f.write(item + "\n\n")
        self.destroy()


if __name__ == "__main__":
    app = GeradorApp()
    app.mainloop()
