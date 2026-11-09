# -*- coding: utf-8 -*-
"""Gera o projeto de coleta de Pokémon (PokeAPI) - 1ª geração + stats."""

from __future__ import annotations

import time
from datetime import date
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import nbformat
import pandas as pd
import requests
from nbclient import NotebookClient
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

BASE = Path(__file__).resolve().parent
NOTEBOOK = BASE / "projeto_coleta_pokemon.ipynb"
CSV_RAW = BASE / "pokemon_bruto.csv"
CSV_FINAL = BASE / "pokemon_dataset.csv"
DOC = BASE / "documentacao.md"
FIG_EXP = BASE / "grafico_experiencia_base.png"
FIG_ATK = BASE / "grafico_ataque_por_tipo.png"

LIMIT = 151
COLS_FINAIS = [
    "id",
    "nome",
    "altura_m",
    "peso_kg",
    "experiencia_base",
    "tipo_principal",
    "tipo_secundario",
    "hp",
    "ataque",
    "defesa",
    "ataque_especial",
    "defesa_especial",
    "velocidade",
    "total_stats",
    "qtd_habilidades",
    "qtd_movimentos",
]


def extrair_stats(det: dict) -> dict:
    mapa = {s["stat"]["name"]: s["base_stat"] for s in det["stats"]}
    return {
        "hp": mapa.get("hp"),
        "ataque": mapa.get("attack"),
        "defesa": mapa.get("defense"),
        "ataque_especial": mapa.get("special-attack"),
        "defesa_especial": mapa.get("special-defense"),
        "velocidade": mapa.get("speed"),
    }


def coletar(limit: int = LIMIT) -> pd.DataFrame:
    lista = requests.get(
        f"https://pokeapi.co/api/v2/pokemon?limit={limit}", timeout=30
    ).json()["results"]

    registros = []
    for i, item in enumerate(lista, start=1):
        det = requests.get(item["url"], timeout=30).json()
        tipos = [t["type"]["name"] for t in det["types"]]
        stats = extrair_stats(det)
        registros.append(
            {
                "id": det["id"],
                "nome": det["name"],
                "altura_dm": det["height"],
                "peso_hg": det["weight"],
                "experiencia_base": det["base_experience"],
                "tipo_principal": tipos[0] if tipos else None,
                "tipo_secundario": tipos[1] if len(tipos) > 1 else None,
                **stats,
                "qtd_habilidades": len(det["abilities"]),
                "qtd_movimentos": len(det["moves"]),
            }
        )
        if i % 25 == 0:
            print(f"  ... {i}/{limit}")
            time.sleep(0.2)
    return pd.DataFrame(registros)


def limpar(df_bruto: pd.DataFrame) -> pd.DataFrame:
    df = df_bruto.copy()
    df["nome"] = df["nome"].str.strip().str.title()
    df["altura_m"] = pd.to_numeric(df["altura_dm"], errors="coerce") / 10
    df["peso_kg"] = pd.to_numeric(df["peso_hg"], errors="coerce") / 10

    numericas = [
        "experiencia_base",
        "hp",
        "ataque",
        "defesa",
        "ataque_especial",
        "defesa_especial",
        "velocidade",
    ]
    for col in numericas:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["total_stats"] = (
        df["hp"]
        + df["ataque"]
        + df["defesa"]
        + df["ataque_especial"]
        + df["defesa_especial"]
        + df["velocidade"]
    )
    df["tipo_secundario"] = df["tipo_secundario"].fillna("nenhum")
    df = df.drop_duplicates(subset=["id"])
    df = df[COLS_FINAIS]
    return df.sort_values("id").reset_index(drop=True)


def salvar_graficos(df: pd.DataFrame) -> None:
    top = df.nlargest(10, "experiencia_base")
    plt.figure(figsize=(10, 5))
    plt.bar(top["nome"], top["experiencia_base"], color="steelblue")
    plt.title("Top 10 Pokémon (1ª geração) por experiência base")
    plt.xlabel("Pokémon")
    plt.ylabel("Experiência base")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(FIG_EXP, dpi=140)
    plt.close()

    media_atk = (
        df.groupby("tipo_principal")["ataque"]
        .mean()
        .sort_values(ascending=False)
        .head(10)
    )
    plt.figure(figsize=(10, 5))
    plt.bar(media_atk.index, media_atk.values, color="tomato")
    plt.title("Média de ataque por tipo principal (Top 10)")
    plt.xlabel("Tipo principal")
    plt.ylabel("Ataque médio")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(FIG_ATK, dpi=140)
    plt.close()


def escrever_documentacao(df: pd.DataFrame, hoje: str) -> None:
    n, cols = df.shape
    tamanho_kb = round(CSV_FINAL.stat().st_size / 1024, 2)
    media_exp = round(df["experiencia_base"].mean(), 1)
    mais_exp = df.loc[df["experiencia_base"].idxmax()]
    mais_forte = df.loc[df["total_stats"].idxmax()]
    mais_pesado = df.loc[df["peso_kg"].idxmax()]
    tipo_mais = df["tipo_principal"].value_counts().idxmax()
    tipo_atk = df.groupby("tipo_principal")["ataque"].mean().idxmax()

    doc = f"""# Documentação do Projeto

## Coleta de dados de Pokémon (PokeAPI) — 1ª geração

**Autor:** Rodrigo Gimenes Rodrigues  
**Matrícula:** CP3071782  
**Data:** {hoje}  
**Disciplina:** Processamento e Coleta de Dados  

---

## 1. OBJETIVO
Coletar os 151 Pokémon da 1ª geração pela PokeAPI, incluindo stats de combate, limpar os dados e gerar um dataset próprio para análise exploratória.

## 2. FONTES DE DADOS
| Fonte | URL | Método | Dados Coletados |
|-------|-----|--------|-----------------|
| PokeAPI | https://pokeapi.co/api/v2/pokemon | API REST | id, nome, altura, peso, experiência, tipos e stats de combate |

## 3. METODOLOGIA
### 3.1 Coleta
Chamei a listagem (`/pokemon?limit=151`) e, para cada item, a URL de detalhe. De cada resposta extraí atributos gerais e os 6 stats base (HP, ataque, defesa, ataque especial, defesa especial e velocidade).

### 3.2 Limpeza
- Converti altura (dm → m) e peso (hg → kg)
- Padronizei nomes com `title()`
- Converti colunas numéricas com `to_numeric`
- Preenchi tipo secundário ausente com `nenhum`
- Criei `total_stats` somando os 6 atributos de combate
- Removi duplicatas por `id`

### 3.3 Processamento
Selecionei as colunas finais, ordenei por `id` e salvei o CSV sem índice.

## 4. DATASET FINAL
- **Total de registros:** {n}
- **Total de colunas:** {cols}
- **Período:** coleta pontual em {hoje}
- **Tamanho do arquivo:** {tamanho_kb} KB

### Colunas:
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | int | Identificador oficial |
| nome | str | Nome do Pokémon |
| altura_m | float | Altura em metros |
| peso_kg | float | Peso em kg |
| experiencia_base | float | Experiência base |
| tipo_principal | str | Tipo principal |
| tipo_secundario | str | Tipo secundário (ou nenhum) |
| hp | int | Pontos de vida |
| ataque | int | Ataque físico |
| defesa | int | Defesa física |
| ataque_especial | int | Ataque especial |
| defesa_especial | int | Defesa especial |
| velocidade | int | Velocidade |
| total_stats | int | Soma dos 6 stats |
| qtd_habilidades | int | Qtd. de habilidades |
| qtd_movimentos | int | Qtd. de movimentos |

## 5. ANÁLISE EXPLORATÓRIA
### 5.1 Estatísticas Descritivas
Média de experiência base: {media_exp}.  
Maior experiência: {mais_exp['nome']} ({mais_exp['experiencia_base']}).  
Maior total de stats: {mais_forte['nome']} ({mais_forte['total_stats']}).  
Mais pesado: {mais_pesado['nome']} ({mais_pesado['peso_kg']} kg).  
Tipo mais comum: {tipo_mais}.  
Tipo com maior ataque médio: {tipo_atk}.

### 5.2 Visualizações
- Top 10 por experiência base (`grafico_experiencia_base.png`)
- Média de ataque por tipo (`grafico_ataque_por_tipo.png`)

## 6. INSIGHTS
1. Na 1ª geração inteira, a experiência base e o total de stats variam bastante entre evoluções finais e formas iniciais.
2. O tipo `{tipo_mais}` é o mais frequente como tipo principal nesta geração.
3. O tipo com maior ataque médio foi `{tipo_atk}` — útil para comparar “estilos” de combate por categoria.

## 7. LIMITAÇÕES
- Só a 1ª geração (151)
- Coleta pontual
- Não inclui formas alternativas / megas

## 8. PRÓXIMOS PASSOS
- Incluir outras gerações
- Cruzar com tabela de efetividade de tipos
- Montar ranking por função (tank, sweeper etc.)

## 9. CÓDIGO
- `projeto_coleta_pokemon.ipynb`
- `pokemon_dataset.csv`
- `pokemon_bruto.csv`

## 10. REFERÊNCIAS
- https://pokeapi.co/
- https://docs.python-requests.org/
- https://pandas.pydata.org/
"""
    DOC.write_text(doc, encoding="utf-8")


def criar_notebook(df: pd.DataFrame, hoje: str) -> None:
    media_exp = round(df["experiencia_base"].mean(), 1)
    mais_exp = df.loc[df["experiencia_base"].idxmax()]
    mais_forte = df.loc[df["total_stats"].idxmax()]
    tipo_mais = df["tipo_principal"].value_counts().idxmax()
    tipo_atk = df.groupby("tipo_principal")["ataque"].mean().idxmax()

    cells = [
        new_markdown_cell(
            f"""# PROJETO DE COLETA DE DADOS
## Pokémon via PokeAPI — 1ª geração + stats

**Autor:** Rodrigo Gimenes Rodrigues  
**Matrícula:** CP3071782  
**Data:** {hoje}  
**Disciplina:** Processamento e Coleta de Dados  

---

## 1. OBJETIVO
Coletar os 151 Pokémon da 1ª geração pela PokeAPI, incluindo stats de combate, limpar os dados e montar um dataset próprio.

## 2. FONTES DE DADOS
| Fonte | URL | Método | Dados Coletados |
|-------|-----|--------|-----------------|
| PokeAPI | https://pokeapi.co/api/v2/pokemon | API REST | atributos gerais + HP, ataque, defesa, sp. atk, sp. def, velocidade |
"""
        ),
        new_markdown_cell(
            """## 3. METODOLOGIA

### 3.1 Coleta
Lista com `limit=151` e, em seguida, uma requisição de detalhe por Pokémon.

### 3.2 Limpeza
Conversão de unidades, padronização de nomes, nulos do tipo secundário, criação de `total_stats` e remoção de duplicatas.

### 3.3 Processamento
DataFrame final ordenado por id e exportado em CSV.
"""
        ),
        new_markdown_cell("## 3.1 Código de coleta"),
        new_code_cell(
            """import time
import requests
import pandas as pd
import matplotlib.pyplot as plt

url_lista = 'https://pokeapi.co/api/v2/pokemon?limit=151'
resposta = requests.get(url_lista, timeout=30)
resposta.raise_for_status()
lista = resposta.json()['results']

registros = []
for i, item in enumerate(lista, start=1):
    det = requests.get(item['url'], timeout=30).json()
    tipos = [t['type']['name'] for t in det['types']]
    stats = {s['stat']['name']: s['base_stat'] for s in det['stats']}

    registros.append({
        'id': det['id'],
        'nome': det['name'],
        'altura_dm': det['height'],
        'peso_hg': det['weight'],
        'experiencia_base': det['base_experience'],
        'tipo_principal': tipos[0] if tipos else None,
        'tipo_secundario': tipos[1] if len(tipos) > 1 else None,
        'hp': stats.get('hp'),
        'ataque': stats.get('attack'),
        'defesa': stats.get('defense'),
        'ataque_especial': stats.get('special-attack'),
        'defesa_especial': stats.get('special-defense'),
        'velocidade': stats.get('speed'),
        'qtd_habilidades': len(det['abilities']),
        'qtd_movimentos': len(det['moves']),
    })

    if i % 25 == 0:
        print(f'Coletados: {i}/{len(lista)}')
        time.sleep(0.2)

df_bruto = pd.DataFrame(registros)
df_bruto.to_csv('pokemon_bruto.csv', index=False, encoding='utf-8')
print('Registros coletados:', len(df_bruto))
df_bruto.head()"""
        ),
        new_markdown_cell("## 3.2 Limpeza e processamento"),
        new_code_cell(
            """df = df_bruto.copy()

df['nome'] = df['nome'].str.strip().str.title()
df['altura_m'] = pd.to_numeric(df['altura_dm'], errors='coerce') / 10
df['peso_kg'] = pd.to_numeric(df['peso_hg'], errors='coerce') / 10

for col in ['experiencia_base', 'hp', 'ataque', 'defesa',
            'ataque_especial', 'defesa_especial', 'velocidade']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

df['total_stats'] = (
    df['hp'] + df['ataque'] + df['defesa']
    + df['ataque_especial'] + df['defesa_especial'] + df['velocidade']
)
df['tipo_secundario'] = df['tipo_secundario'].fillna('nenhum')
df = df.drop_duplicates(subset=['id'])

df = df[['id', 'nome', 'altura_m', 'peso_kg', 'experiencia_base',
         'tipo_principal', 'tipo_secundario', 'hp', 'ataque', 'defesa',
         'ataque_especial', 'defesa_especial', 'velocidade', 'total_stats',
         'qtd_habilidades', 'qtd_movimentos']]
df = df.sort_values('id').reset_index(drop=True)

print('Nulos por coluna:')
print(df.isnull().sum())
df.head()"""
        ),
        new_markdown_cell("## 4. DATASET FINAL"),
        new_code_cell(
            """print('Shape:', df.shape)
print('Colunas:', df.columns.tolist())
print(df.dtypes)
df.to_csv('pokemon_dataset.csv', index=False, encoding='utf-8')
print('CSV salvo: pokemon_dataset.csv')
df.head(10)"""
        ),
        new_markdown_cell("## 5. ANÁLISE EXPLORATÓRIA"),
        new_code_cell(
            """print(df.describe())
print()
print('Tipos principais:')
print(df['tipo_principal'].value_counts())
print()
print('Top 5 por total_stats:')
print(df.nlargest(5, 'total_stats')[['nome', 'tipo_principal', 'total_stats']])"""
        ),
        new_code_cell(
            """top = df.nlargest(10, 'experiencia_base')

plt.figure(figsize=(10, 5))
plt.bar(top['nome'], top['experiencia_base'], color='steelblue')
plt.title('Top 10 Pokémon (1ª geração) por experiência base')
plt.xlabel('Pokémon')
plt.ylabel('Experiência base')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()"""
        ),
        new_code_cell(
            """media_atk = (
    df.groupby('tipo_principal')['ataque']
      .mean()
      .sort_values(ascending=False)
      .head(10)
)

plt.figure(figsize=(10, 5))
plt.bar(media_atk.index, media_atk.values, color='tomato')
plt.title('Média de ataque por tipo principal (Top 10)')
plt.xlabel('Tipo principal')
plt.ylabel('Ataque médio')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()"""
        ),
        new_markdown_cell(
            f"""## 6. INSIGHTS
1. Na 1ª geração, a média de experiência base ficou em torno de **{media_exp}**.
2. Maior experiência nesta coleta: **{mais_exp['nome']}** ({mais_exp['experiencia_base']}).
3. Maior total de stats: **{mais_forte['nome']}** ({mais_forte['total_stats']}).
4. Tipo principal mais comum: **{tipo_mais}**.
5. Tipo com maior ataque médio: **{tipo_atk}**.

## 7. LIMITAÇÕES
- Apenas a 1ª geração (151)
- Coleta pontual
- Sem formas alternativas / megas

## 8. PRÓXIMOS PASSOS
- Incluir outras gerações
- Cruzar com efetividade de tipos
- Criar ranking por função de combate

## 9. ARQUIVOS GERADOS
- `pokemon_bruto.csv`
- `pokemon_dataset.csv`
- `documentacao.md`
- `grafico_experiencia_base.png`
- `grafico_ataque_por_tipo.png`

## 10. REFERÊNCIAS
- https://pokeapi.co/
- https://docs.python-requests.org/
- https://pandas.pydata.org/
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
    nbformat.write(nb, NOTEBOOK)

    client = NotebookClient(
        nb,
        timeout=600,
        kernel_name="python3",
        resources={"metadata": {"path": str(BASE)}},
    )
    client.execute()
    nbformat.write(nb, NOTEBOOK)


def main() -> None:
    hoje = date.today().isoformat()
    print(f"Coletando {LIMIT} Pokémon da 1ª geração...")
    df_bruto = coletar(LIMIT)
    df_bruto.to_csv(CSV_RAW, index=False, encoding="utf-8")

    df = limpar(df_bruto)
    df.to_csv(CSV_FINAL, index=False, encoding="utf-8")
    salvar_graficos(df)
    escrever_documentacao(df, hoje)

    print("Executando notebook (vai coletar de novo dentro dele)...")
    criar_notebook(df, hoje)

    print("OK")
    print("registros:", len(df))
    print("colunas:", list(df.columns))
    print("notebook:", NOTEBOOK)
    print("csv:", CSV_FINAL)
    print("doc:", DOC)


if __name__ == "__main__":
    main()
