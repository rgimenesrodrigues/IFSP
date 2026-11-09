# Documentação do Projeto

## Coleta de dados de Pokémon (PokeAPI) — 1ª geração

**Autor:** Rodrigo Gimenes Rodrigues  
**Matrícula:** CP3071782  
**Data:** 2026-11-08  
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
- **Total de registros:** 151
- **Total de colunas:** 16
- **Período:** coleta pontual em 2026-11-08
- **Tamanho do arquivo:** 9.98 KB

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
Média de experiência base: 135.1.  
Maior experiência: Chansey (395).  
Maior total de stats: Mewtwo (680).  
Mais pesado: Snorlax (460.0 kg).  
Tipo mais comum: water.  
Tipo com maior ataque médio: fighting.

### 5.2 Visualizações
- Top 10 por experiência base (`grafico_experiencia_base.png`)
- Média de ataque por tipo (`grafico_ataque_por_tipo.png`)

## 6. INSIGHTS
1. Na 1ª geração inteira, a experiência base e o total de stats variam bastante entre evoluções finais e formas iniciais.
2. O tipo `water` é o mais frequente como tipo principal nesta geração.
3. O tipo com maior ataque médio foi `fighting` — útil para comparar “estilos” de combate por categoria.

## 7. LIMITAÇÕES
- Só a 1ª geração (151)
- Coleta pontual
- Não inclui formas alternativas / megas

## 8. PRÓXIMOS PASSOS
- Incluir outras gerações
- Cruzar com tabela de efetividade de tipos
- Montar ranking por função (tank, sweeper etc.)

## 9. CÓDIGO / ARQUIVOS
- `projeto_coleta_pokemon.ipynb`
- `pokemon_dataset.csv`
- `pokemon_bruto.csv`
- `pitch.mp4` — apresentação rápida do projeto (≈ 1 minuto)

## 10. PITCH
Vídeo da apresentação: [`pitch.mp4`](./pitch.mp4)

## 11. REFERÊNCIAS
- https://pokeapi.co/
- https://docs.python-requests.org/
- https://pandas.pydata.org/
