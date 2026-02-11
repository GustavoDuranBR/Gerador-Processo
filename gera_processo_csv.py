import os
import sys
import random
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from faker import Faker
from validate_docbr import CPF
from datetime import datetime, timedelta

fake = Faker('pt_BR')
cpf_gen = CPF()


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class GeradorApp(ttk.Window):

    def __init__(self):
        super().__init__(themename="darkly")
        self.title("Gerador QA GOD MODE – Processo Trabalhista")
        self.geometry("600x500")
        self.resizable(False, False)

        self.registros_csv = []

        container = ttk.Frame(self)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        self.left_panel = ttk.Frame(container, width=260)
        self.left_panel.pack(side="left", fill="y", padx=(0, 10))

        self.right_panel = ttk.Frame(container)
        self.right_panel.pack(side="right", fill="both", expand=True)

        self._build_left_panel()
        self._build_right_panel()

    # =========================================================
    # LEFT PANEL
    # =========================================================
    def _build_left_panel(self):

        ttk.Label(self.left_panel, text="Tipo de Processo").pack(anchor="w", pady=2)

        self.tipo_var = ttk.StringVar(value="Judicial")

        ttk.Combobox(
            self.left_panel,
            textvariable=self.tipo_var,
            values=["Judicial", "CCP/NINTER"],
            state="readonly"
        ).pack(fill="x")

        ttk.Label(self.left_panel, text="Ano do Processo").pack(anchor="w", pady=2)

        self.ano_var = ttk.Entry(self.left_panel)
        self.ano_var.insert(0, "2026")
        self.ano_var.pack(fill="x")

        ttk.Label(self.left_panel, text="Período de Apuração (YYYY-MM)").pack(anchor="w", pady=2)

        self.per_apur_var = ttk.Entry(self.left_panel)
        hoje = datetime.today()
        self.per_apur_var.insert(0, f"{hoje.year}-{hoje.month:02d}")
        self.per_apur_var.pack(fill="x")

        self.random_per_apur = ttk.BooleanVar(value=True)

        ttk.Checkbutton(
            self.left_panel,
            text="Período aleatório",
            variable=self.random_per_apur,
            bootstyle="round-toggle"
        ).pack(anchor="w")

        ttk.Label(self.left_panel, text="Quantidade de Registros").pack(anchor="w", pady=2)

        self.qtd_var = ttk.Spinbox(self.left_panel, from_=1, to=500)
        self.qtd_var.set(5)
        self.qtd_var.pack(fill="x")

        ttk.Button(
            self.left_panel,
            text="Gerar Registros",
            bootstyle="success",
            command=self.gerar_lote
        ).pack(fill="x", pady=10)

        ttk.Button(
            self.left_panel,
            text="Exportar CSV",
            bootstyle="primary",
            command=self.exportar_csv
        ).pack(fill="x")

    # =========================================================
    # RIGHT PANEL
    # =========================================================
    def _build_right_panel(self):

        self.canvas = ttk.Canvas(self.right_panel, height=450)

        self.scroll = ttk.Scrollbar(
            self.right_panel,
            orient="vertical",
            command=self.canvas.yview
        )

        self.result_frame = ttk.Frame(self.canvas)

        self.result_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.result_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scroll.set)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scroll.pack(side="right", fill="y")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # =========================================================
    # QA GOD MODE CORE
    # =========================================================

    def gerar_num_processo(self, digitos, ano):
        base = ''.join(str(random.randint(0, 9)) for _ in range(digitos - 4))
        return f"{base}{ano}"

    def gerar_per_apur_random(self):
        hoje = datetime.today()
        meses_atras = random.randint(0, 12)
        ano = hoje.year
        mes = hoje.month - meses_atras

        while mes <= 0:
            mes += 12
            ano -= 1

        return f"{ano}-{mes:02d}"

    # 🔥 FUNÇÃO QA GOD MODE
    def gerar_datas_esocial(self, per_apur):

        ano, mes = map(int, per_apur.split("-"))

        dt_sent = datetime(ano, mes, random.randint(1, 28))

        dt_deslig = dt_sent + timedelta(days=random.randint(1, 30))

        dt_remun = datetime(ano - 1, random.randint(1, 12), random.randint(1, 28))

        # gera 3 períodos sequenciais (evita rejeição)
        per_ref1 = f"{ano}-{mes:02d}"

        mes2 = mes + 1 if mes < 12 else 1
        ano2 = ano if mes < 12 else ano + 1

        per_ref2 = f"{ano2}-{mes2:02d}"

        mes3 = mes2 + 1 if mes2 < 12 else 1
        ano3 = ano2 if mes2 < 12 else ano2 + 1

        per_ref3 = f"{ano3}-{mes3:02d}"

        return {
            "dtSent": dt_sent.strftime("%Y-%m-%d"),
            "dtDeslig": dt_deslig.strftime("%Y-%m-%d"),
            "dtRemun": dt_remun.strftime("%Y-%m-%d"),
            "perRef1": per_ref1,
            "perRef2": per_ref2,
            "perRef3": per_ref3
        }

    def gerar_registro(self):

        ano = self.ano_var.get()

        if self.random_per_apur.get():
            per_apur = self.gerar_per_apur_random()
        else:
            per_apur = self.per_apur_var.get()

        if not ano.isdigit() or len(ano) != 4:
            raise ValueError("Ano inválido")

        digitos = 20 if self.tipo_var.get() == "Judicial" else 15

        datas = self.gerar_datas_esocial(per_apur)

        return {
            "nrProcTrab": self.gerar_num_processo(digitos, ano),
            "nmTrab": fake.name(),
            "dtNascto": fake.date_of_birth(minimum_age=18, maximum_age=65).strftime("%Y-%m-%d"),
            "perApurPgto": per_apur,
            "cpfTrab": cpf_gen.generate(),

            # 🔥 CAMPOS QA GOD MODE
            "dtSent": datas["dtSent"],
            "dtDeslig": datas["dtDeslig"],
            "dtRemun": datas["dtRemun"],
            "perRef1": datas["perRef1"],
            "perRef2": datas["perRef2"],
            "perRef3": datas["perRef3"],
        }

    def gerar_lote(self):

        self.registros_csv.clear()

        for w in self.result_frame.winfo_children():
            w.destroy()

        qtd = int(self.qtd_var.get())

        for _ in range(qtd):
            registro = self.gerar_registro()
            self.registros_csv.append(registro)
            self.render_registro(registro)

        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    # =========================================================
    # RENDER
    # =========================================================
    def render_registro(self, registro):

        ttk.Separator(self.result_frame).pack(fill="x", pady=4)

        for chave, valor in registro.items():

            linha = ttk.Frame(self.result_frame)
            linha.pack(fill="x", pady=2)

            ttk.Button(
                linha,
                text="📋",
                width=3,
                command=lambda v=valor: self.copiar(v)
            ).pack(side="left")

            ttk.Label(
                linha,
                text=f"{chave}: {valor}",
                anchor="w"
            ).pack(side="left", fill="x", padx=6)

    def copiar(self, texto):
        self.clipboard_clear()
        self.clipboard_append(texto)

    # =========================================================
    # CSV
    # =========================================================
    def exportar_csv(self):

        # 🔥 agora gera automático se não tiver massa
        if not self.registros_csv:
            qtd = int(self.qtd_var.get())
            for _ in range(qtd):
                self.registros_csv.append(self.gerar_registro())

        os.makedirs("csv", exist_ok=True)

        nome = f"massa_postman_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        caminho = os.path.join("csv", nome)

        with open(caminho, "w", encoding="utf-8") as f:

            f.write(
                "nrProcTrab,nmTrab,dtNascto,perApurPgto,cpfTrab,dtSent,dtDeslig,dtRemun,perRef1,perRef2,perRef3\n"
            )

            for r in self.registros_csv:
                f.write(
                    f"\"{r['nrProcTrab']}\","
                    f"{r['nmTrab']},"
                    f"{r['dtNascto']},"
                    f"{r['perApurPgto']},"
                    f"{r['cpfTrab']},"
                    f"{r['dtSent']},"
                    f"{r['dtDeslig']},"
                    f"{r['dtRemun']},"
                    f"{r['perRef1']},"
                    f"{r['perRef2']},"
                    f"{r['perRef3']}\n"
                )

        messagebox.showinfo("CSV Gerado", f"Arquivo salvo em:\n{caminho}")

        self.registros_csv.clear()


if __name__ == "__main__":
    app = GeradorApp()
    app.mainloop()
