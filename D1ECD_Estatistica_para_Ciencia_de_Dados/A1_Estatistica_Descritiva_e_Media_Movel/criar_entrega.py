# -*- coding: utf-8 -*-
"""Gera o notebook da A1, executa as analises e exporta o PDF de entrega."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import nbformat
import numpy as np
import pandas as pd
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from nbclient import NotebookClient
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

BASE = Path(__file__).resolve().parent
FIGURAS = BASE / "figuras"
FIGURAS.mkdir(exist_ok=True)

ALUNO = "Rodrigo Gimenes Rodrigues"
MATRICULA = "CP3071782"
CAMPUS = "Campinas"
CURSO = "Especialização em Ciência de Dados"
PERIODO = "2026/2"
TURNO = "EAD"

NOTEBOOK_PATH = BASE / "ED1ECD_A1_Rodrigo_Campinas.ipynb"
PDF_PATH = BASE / "ED1ECD_A1_Rodrigo_Campinas.pdf"
PLOT_PATH = FIGURAS / "media_movel_transacoes.png"


def gerar_dados() -> pd.DataFrame:
    np.random.seed(42)
    dias = pd.date_range(start="2026-01-01", periods=60, freq="D")
    tendencia = np.linspace(50, 110, 60)
    sazonalidade = 15 * np.sin(np.linspace(0, 4 * np.pi, 60))
    ruido = np.random.normal(loc=0, scale=8, size=60)
    transacoes = tendencia + sazonalidade + ruido
    return pd.DataFrame(
        {
            "Data": dias,
            "Transacoes_Milhares": np.round(transacoes, 2),
        }
    )


def metricas(df: pd.DataFrame) -> dict:
    s = df["Transacoes_Milhares"]
    q1 = float(s.quantile(0.25))
    q2 = float(s.quantile(0.50))
    q3 = float(s.quantile(0.75))
    iqr = q3 - q1
    li = q1 - 1.5 * iqr
    ls = q3 + 1.5 * iqr
    outliers = df[(s < li) | (s > ls)]
    return {
        "n": int(s.size),
        "media": float(s.mean()),
        "mediana": float(s.median()),
        "min": float(s.min()),
        "max": float(s.max()),
        "midrange": float((s.min() + s.max()) / 2),
        "skew": float(s.skew()),
        "var": float(s.var(ddof=1)),
        "std": float(s.std(ddof=1)),
        "q1": q1,
        "q2": q2,
        "q3": q3,
        "iqr": iqr,
        "cv": float(s.std(ddof=1) / s.mean() * 100),
        "li": li,
        "ls": ls,
        "n_outliers": int(len(outliers)),
        "inicio": float(s.iloc[0]),
        "fim": float(s.iloc[-1]),
        "media_10_ini": float(s.iloc[:10].mean()),
        "media_10_fim": float(s.iloc[-10:].mean()),
        "data_min": df.loc[s.idxmin(), "Data"].strftime("%d/%m/%Y"),
        "data_max": df.loc[s.idxmax(), "Data"].strftime("%d/%m/%Y"),
        "mm7_fim": float(s.rolling(7).mean().iloc[-1]),
        "mm14_fim": float(s.rolling(14).mean().iloc[-1]),
        "unicos": int(s.nunique()),
    }


def salvar_grafico(df: pd.DataFrame) -> None:
    df = df.copy()
    df["MM7"] = df["Transacoes_Milhares"].rolling(window=7).mean()
    df["MM14"] = df["Transacoes_Milhares"].rolling(window=14).mean()

    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.plot(
        df["Data"],
        df["Transacoes_Milhares"],
        color="gray",
        linewidth=1.2,
        marker="o",
        markersize=3,
        alpha=0.7,
        label="Série original",
    )
    ax.plot(df["Data"], df["MM7"], color="orange", linewidth=2, label="MM 7 dias")
    ax.plot(df["Data"], df["MM14"], color="blue", linewidth=2, label="MM 14 dias")
    ax.set_title("Transações diárias e médias móveis")
    ax.set_xlabel("Data")
    ax.set_ylabel("Transações (milhares)")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(PLOT_PATH, dpi=150)
    plt.close(fig)


def criar_notebook() -> None:
    cells = [
        new_markdown_cell(
            f"""# D1ECD – Estatística para Ciência de Dados
## Atividade Avaliativa 01 – Estatística Descritiva e Média Móvel

**Nome:** {ALUNO}  
**Matrícula:** {MATRICULA}  
**Curso:** {CURSO}  
**Período/Ano:** {PERIODO}  
**Campus:** {CAMPUS}  
**Turno:** {TURNO}  
**Professor:** Kakimoto
"""
        ),
        new_markdown_cell(
            """## Conjunto de dados

Código fornecido no enunciado para gerar a série de 60 dias.
"""
        ),
        new_code_cell(
            """import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Fixa a semente aleatória para reprodutibilidade dos resultados
np.random.seed(42)

dias = pd.date_range(start='2026-01-01', periods=60, freq='D')
tendencia = np.linspace(50, 110, 60)
sazonalidade = 15 * np.sin(np.linspace(0, 4 * np.pi, 60))
ruido = np.random.normal(loc=0, scale=8, size=60)
transacoes = tendencia + sazonalidade + ruido

df = pd.DataFrame({
    'Data': dias,
    'Transacoes_Milhares': np.round(transacoes, 2)
})

serie = df['Transacoes_Milhares']
df.head()"""
        ),
        new_markdown_cell(
            """## Parte 1 – Estatística descritiva e medidas de tendência central
"""
        ),
        new_code_cell(
            """media = serie.mean()
mediana = serie.median()
moda = serie.mode()
minimo = serie.min()
maximo = serie.max()
medio_alcance = (minimo + maximo) / 2

print('Média:', round(media, 2))
print('Mediana:', round(mediana, 2))
print('Moda:', moda.tolist() if serie.value_counts().max() > 1 else 'não há moda (todos os valores são únicos)')
print('Mínimo:', minimo)
print('Máximo:', maximo)
print('Médio alcance:', round(medio_alcance, 2))
print('Média - mediana:', round(media - mediana, 2))"""
        ),
        new_markdown_cell(
            """### Comentário – Parte 1

Rodando o código, a média deu 78,76 e a mediana 77,91. São valores bem próximos. A média um pouco maior que a mediana sugere uma leve assimetria positiva, mas nada muito forte.

Sobre a moda: não tem. Cada dia deu um valor diferente, então a série é amodal.

O médio alcance ficou em 82,02 ((46,23 + 117,80) / 2). Esse número usa só o menor e o maior valor, então acaba sendo puxado pelos extremos. Aqui o máximo é o último dia da série, que já vem de uma tendência de alta, e o mínimo parece um vale. Por isso o médio alcance não representa bem o centro desses dados. Média e mediana fazem mais sentido.
"""
        ),
        new_markdown_cell(
            """## Parte 2 – Variabilidade e dispersão
"""
        ),
        new_code_cell(
            """variancia = serie.var(ddof=1)
desvio = serie.std(ddof=1)
q1 = serie.quantile(0.25)
q2 = serie.quantile(0.50)
q3 = serie.quantile(0.75)
iqr = q3 - q1
cv = (desvio / media) * 100

limite_inf = q1 - 1.5 * iqr
limite_sup = q3 + 1.5 * iqr
outliers = df[(serie < limite_inf) | (serie > limite_sup)]

print('Variância amostral:', round(variancia, 2))
print('Desvio padrão:', round(desvio, 2))
print('Q1:', round(q1, 2))
print('Q2:', round(q2, 2))
print('Q3:', round(q3, 2))
print('IQR:', round(iqr, 2))
print('CV (%):', round(cv, 2))
print('Limite inferior:', round(limite_inf, 2))
print('Limite superior:', round(limite_sup, 2))
print('Qtd de outliers:', len(outliers))
print(outliers if len(outliers) else 'Nenhum outlier encontrado.')"""
        ),
        new_markdown_cell(
            """### Comentário – Parte 2

A variância amostral deu 341,98 e o desvio padrão 18,49. Ou seja, os dias costumam variar cerca de 18,5 mil transações em relação à média.

Os percentis ficaram: Q1 = 63,46, Q2 = 77,91 e Q3 = 93,05. O IQR foi 29,59, então a metade central dos dias está entre esses valores.

O CV deu 23,48%. Dá para dizer que a dispersão relativa é moderada. Vale lembrar que a série tem tendência de crescimento e sazonalidade, então parte dessa variação não é só “ruído do dia a dia”.

Usando o critério do boxplot (1,5 × IQR), os limites foram 19,08 e 137,43. Nenhum ponto ficou fora, então não apareceu outlier.
"""
        ),
        new_markdown_cell(
            """## Parte 3 – Média móvel

Foram calculadas duas médias móveis simples: janela de 7 dias e janela de 14 dias.
"""
        ),
        new_code_cell(
            """def media_movel(dados, janela):
    valores = list(dados)
    resultado = [np.nan] * (janela - 1)
    for i in range(len(valores) - janela + 1):
        resultado.append(sum(valores[i:i+janela]) / janela)
    return resultado

df['MM7'] = media_movel(serie, 7)
df['MM14'] = media_movel(serie, 14)

print(df[['Data', 'Transacoes_Milhares', 'MM7', 'MM14']].tail(10))
print('MM7 no último dia:', round(df['MM7'].iloc[-1], 2))
print('MM14 no último dia:', round(df['MM14'].iloc[-1], 2))"""
        ),
        new_code_cell(
            """plt.figure(figsize=(11, 5.5))
plt.plot(df['Data'], df['Transacoes_Milhares'], color='gray', marker='o', markersize=3, alpha=0.7, label='Série original')
plt.plot(df['Data'], df['MM7'], color='orange', linewidth=2, label='MM 7 dias')
plt.plot(df['Data'], df['MM14'], color='blue', linewidth=2, label='MM 14 dias')
plt.title('Transações diárias e médias móveis')
plt.xlabel('Data')
plt.ylabel('Transações (milhares)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()"""
        ),
        new_markdown_cell(
            """### Comentário – Parte 3

No gráfico dá para ver bem a diferença entre as duas janelas. A de 7 dias acompanha mais de perto a série original: suaviza um pouco, mas ainda reage aos altos e baixos. No último dia ela ficou em 101,91.

A de 14 dias fica mais “lisa”. Ela mostra melhor a tendência geral, mas demora mais para acompanhar as mudanças. No final ficou em 94,18, abaixo da MM7, porque ainda carrega valores das semanas anteriores, que eram menores.

Resumindo: janela maior = mais suavização, mas também mais atraso.
"""
        ),
        new_markdown_cell(
            """## Parte 4 – Análise crítica e parecer de negócio

Olhando os 60 dias, a tendência geral é de crescimento. A série começa em 53,97 mil transações e termina em 117,80. A média dos 10 primeiros dias fica em 68,26 e sobe para 96,92 nos 10 últimos. Mesmo com oscilações e um vale mais baixo no meio (46,23 em 20/01), o volume no final do período é bem maior do que no começo. Para a fintech, isso significa mais carga na plataforma e, na prática, mais atenção com capacidade e infraestrutura.

Para o painel do time de infraestrutura, eu usaria a média móvel de 7 dias como principal. Ela suaviza o ruído do dia a dia e ainda reage rápido o suficiente quando a demanda muda. A de 14 dias pode ficar como apoio, mais para ver a tendência, mas sozinha ela atrasa demais e pode esconder um pico recente.

Sobre as medidas da Parte 1: os picos e a tendência de alta puxam a média um pouco acima da mediana (78,76 contra 77,91). Aqui a diferença é pequena, mas já mostra que a média sente mais os valores altos. O médio alcance sofre ainda mais, porque depende só do mínimo e do máximo. Então, para acompanhar a operação, faz mais sentido olhar a média móvel recente do que só a média geral dos 60 dias.
"""
        ),
    ]

    nb = new_notebook(
        cells=cells,
        metadata={
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "pygments_lexer": "ipython3"},
        },
    )
    nbformat.write(nb, NOTEBOOK_PATH)


def executar_notebook() -> None:
    nb = nbformat.read(NOTEBOOK_PATH, as_version=4)
    client = NotebookClient(
        nb,
        timeout=180,
        kernel_name="python3",
        resources={"metadata": {"path": str(BASE)}},
    )
    client.execute()
    nbformat.write(nb, NOTEBOOK_PATH)


FONT_DIR = Path(r"C:\Windows\Fonts")


class RelatorioPDF(FPDF):
    def __init__(self) -> None:
        super().__init__("P", "mm", "A4")
        self.add_font("ArialUni", "", str(FONT_DIR / "arial.ttf"))
        self.add_font("ArialUni", "B", str(FONT_DIR / "arialbd.ttf"))
        self.add_font("ArialUni", "I", str(FONT_DIR / "ariali.ttf"))

    def header(self) -> None:
        self.set_font("ArialUni", "B", 9)
        self.set_text_color(60, 60, 60)
        self.cell(
            0,
            8,
            "D1ECD – Estatística para Ciência de Dados – Atividade Avaliativa 01",
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )
        self.set_draw_color(80, 80, 80)
        self.set_line_width(0.3)
        self.line(15, self.get_y() + 1, 195, self.get_y() + 1)
        self.ln(6)

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("ArialUni", "I", 8)
        self.set_text_color(100, 100, 100)
        self.cell(
            0,
            10,
            f"Página {self.page_no()}/{{nb}}",
            align="C",
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )


def _p(pdf: RelatorioPDF, text: str, size: int = 11, style: str = "", ln: float = 5.5) -> None:
    pdf.set_font("ArialUni", style, size)
    pdf.set_text_color(30, 30, 30)
    pdf.multi_cell(0, ln, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(1)


def _h(pdf: RelatorioPDF, text: str) -> None:
    pdf.ln(2)
    pdf.set_font("ArialUni", "B", 12)
    pdf.set_text_color(20, 20, 20)
    pdf.multi_cell(0, 7, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(1)


def _code(pdf: RelatorioPDF, text: str) -> None:
    pdf.set_font("Courier", size=8)
    pdf.set_fill_color(245, 245, 245)
    pdf.set_text_color(20, 20, 20)
    pdf.multi_cell(0, 4.0, text, fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(2)


def gerar_pdf(m: dict) -> None:
    pdf = RelatorioPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.set_left_margin(15)
    pdf.set_right_margin(15)
    pdf.add_page()

    pdf.set_font("ArialUni", "B", 14)
    pdf.multi_cell(
        0,
        7,
        "Atividade Avaliativa 01 – Estatística Descritiva e Média Móvel",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )
    pdf.ln(2)

    pdf.set_font("ArialUni", "", 11)
    pdf.multi_cell(
        0,
        5.5,
        f"Nome: {ALUNO}\n"
        f"Matrícula: {MATRICULA}\n"
        f"Curso: {CURSO}\n"
        f"Período/Ano Letivo: {PERIODO}\n"
        f"Campus: {CAMPUS}\n"
        f"Turno: {TURNO}\n"
        f"Professor: Kakimoto\n"
        f"Data: 06/11/2026",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )
    pdf.ln(3)

    _h(pdf, "Conjunto de dados")
    _p(pdf, "Segue o código do enunciado usado para gerar a série.")
    _code(
        pdf,
        "import numpy as np\n"
        "import pandas as pd\n"
        "np.random.seed(42)\n"
        "dias = pd.date_range(start='2026-01-01', periods=60, freq='D')\n"
        "tendencia = np.linspace(50, 110, 60)\n"
        "sazonalidade = 15 * np.sin(np.linspace(0, 4 * np.pi, 60))\n"
        "ruido = np.random.normal(loc=0, scale=8, size=60)\n"
        "transacoes = tendencia + sazonalidade + ruido\n"
        "df = pd.DataFrame({\n"
        "    'Data': dias,\n"
        "    'Transacoes_Milhares': np.round(transacoes, 2)\n"
        "})",
    )

    _h(pdf, "Parte 1 – Tendência central")
    _code(
        pdf,
        "media = serie.mean()\n"
        "mediana = serie.median()\n"
        "moda = serie.mode()\n"
        "medio_alcance = (serie.min() + serie.max()) / 2",
    )
    _p(
        pdf,
        f"Resultados obtidos: média = {m['media']:.2f}; mediana = {m['mediana']:.2f}; "
        f"mínimo = {m['min']:.2f}; máximo = {m['max']:.2f}; médio alcance = {m['midrange']:.2f}. "
        f"Não há moda, porque os {m['n']} valores são todos diferentes.",
    )
    _p(
        pdf,
        "A média um pouco acima da mediana sugere uma leve assimetria positiva, mas bem "
        "pequena. O médio alcance (82,02) não é uma boa medida aqui, porque "
        "ele só olha o mínimo e o máximo e acaba sendo influenciado pelos extremos. Média e "
        "mediana descrevem melhor o centro da série.",
    )

    _h(pdf, "Parte 2 – Variabilidade e dispersão")
    _code(
        pdf,
        "variancia = serie.var(ddof=1)\n"
        "desvio = serie.std(ddof=1)\n"
        "q1 = serie.quantile(0.25)\n"
        "q2 = serie.quantile(0.50)\n"
        "q3 = serie.quantile(0.75)\n"
        "iqr = q3 - q1\n"
        "cv = (desvio / media) * 100\n"
        "limite_inf = q1 - 1.5 * iqr\n"
        "limite_sup = q3 + 1.5 * iqr",
    )
    _p(
        pdf,
        f"Variância amostral = {m['var']:.2f}; desvio padrão = {m['std']:.2f}; "
        f"Q1 = {m['q1']:.2f}; Q2 = {m['q2']:.2f}; Q3 = {m['q3']:.2f}; IQR = {m['iqr']:.2f}; "
        f"CV = {m['cv']:.2f}%. Limites do boxplot: {m['li']:.2f} e {m['ls']:.2f}. "
        f"Outliers: {m['n_outliers']}.",
    )
    _p(
        pdf,
        "O desvio padrão de cerca de 18,5 mil transações mostra uma variação razoável em torno "
        "da média. O CV de 23,48% indica dispersão moderada. Parte dessa variação vem da "
        "tendência de crescimento e da sazonalidade, não só do ruído diário. Pelo critério "
        "1,5×IQR, não apareceu nenhum outlier.",
    )

    _h(pdf, "Parte 3 – Média móvel")
    _p(
        pdf,
        "Foram calculadas médias móveis simples com janelas de 7 e 14 dias.",
    )
    _code(
        pdf,
        "def media_movel(dados, janela):\n"
        "    valores = list(dados)\n"
        "    resultado = [np.nan] * (janela - 1)\n"
        "    for i in range(len(valores) - janela + 1):\n"
        "        resultado.append(sum(valores[i:i+janela]) / janela)\n"
        "    return resultado\n\n"
        "df['MM7'] = media_movel(serie, 7)\n"
        "df['MM14'] = media_movel(serie, 14)",
    )
    _p(
        pdf,
        f"No último dia, MM7 = {m['mm7_fim']:.2f} e MM14 = {m['mm14_fim']:.2f}.",
    )
    pdf.image(str(PLOT_PATH), w=175)
    pdf.ln(2)
    _p(
        pdf,
        "A janela de 7 dias acompanha melhor a série original: suaviza um pouco, mas ainda "
        "reage aos altos e baixos. A de 14 dias fica mais lisa e mostra melhor a tendência, "
        "porém demora mais para acompanhar as mudanças. No final ela fica abaixo da MM7 "
        "porque ainda carrega valores menores das semanas anteriores. Em resumo, janela "
        "maior suaviza mais, mas também atrasa mais.",
    )

    _h(pdf, "Parte 4 – Análise crítica e parecer de negócio")
    _p(
        pdf,
        f"Nos 60 dias a tendência geral é de crescimento. A série começa em {m['inicio']:.2f} "
        f"mil transações e termina em {m['fim']:.2f}. A média dos 10 primeiros dias "
        f"({m['media_10_ini']:.2f}) sobe para {m['media_10_fim']:.2f} nos 10 últimos. Mesmo "
        f"com oscilações e um vale mais baixo no meio ({m['min']:.2f} em {m['data_min']}), "
        f"o volume no final é bem maior do que no começo. Para a fintech, isso significa mais "
        f"carga na plataforma e mais atenção com capacidade e infraestrutura.",
    )
    _p(
        pdf,
        "Para o painel do time de infraestrutura, eu usaria a média móvel de 7 dias como "
        "principal. Ela suaviza o ruído do dia a dia e ainda reage rápido o suficiente quando "
        "a demanda muda. A de 14 dias pode ficar como apoio, mais para ver a tendência, mas "
        "sozinha ela atrasa demais e pode esconder um pico recente.",
    )
    _p(
        pdf,
        "Sobre as medidas da Parte 1: os picos e a tendência de alta puxam a média um pouco "
        "acima da mediana (78,76 contra 77,91). A diferença é pequena, mas já mostra que a "
        "média sente mais os valores altos. O médio alcance sofre ainda mais, porque depende "
        "só do mínimo e do máximo. Então, para acompanhar a operação, faz mais sentido olhar "
        "a média móvel recente do que só a média geral dos 60 dias.",
    )

    pdf.output(str(PDF_PATH))


def main() -> None:
    df = gerar_dados()
    m = metricas(df)
    salvar_grafico(df)
    criar_notebook()
    try:
        executar_notebook()
        print("Notebook executado com saidas.")
    except Exception as exc:
        print(f"Notebook gerado, mas a execucao do kernel falhou: {exc}")
    gerar_pdf(m)

    # remove arquivos antigos com nome anterior
    for antigo in [
        BASE / "ED1ECD_A1_Rodrigo.ipynb",
        BASE / "ED1ECD_A1_Rodrigo.pdf",
    ]:
        if antigo.exists():
            antigo.unlink()

    print(json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in m.items()}, indent=2))
    print(f"Notebook: {NOTEBOOK_PATH}")
    print(f"PDF: {PDF_PATH}")


if __name__ == "__main__":
    main()
