# Projeto: Plataforma Interativa de Revisão do Estatuto - AMABRE (Com Turso)

Este documento contém a especificação técnica e o código-fonte em Streamlit integrado ao banco de dados **Turso** para persistência e armazenamento das avaliações do Estatuto da AMABRE.

---

## 1. Estrutura do Banco de Dados (Turso / SQLite)

O `antigravity` deve rodar os seguintes comandos SQL no painel do Turso ou via CLI para criar as tabelas necessárias:

```sql
-- Tabela de Usuários (Moradores)
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    rua TEXT NOT NULL,
    whatsapp TEXT,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Respostas / Feedbacks do Estatuto
CREATE TABLE IF NOT EXISTS respostas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER,
    artigo_id INTEGER NOT NULL,
    titulo_artigo TEXT NOT NULL,
    voto TEXT NOT NULL,
    comentario TEXT,
    audio_url TEXT, -- Link do áudio armazenado na nuvem (Supabase/S3/Firebase)
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
);

```python
ARTIGOS_ESTATUTO = [
    {
        "id": 1,
        "capitulo": "CAPÍTULO 1º - DA DENOMINAÇÃO, SEDE, DURAÇÃO, FINALIDADE E EXTINÇÃO",
        "titulo": "Artigo 1º - Da Denominação, Sede e Caráter",
        "texto": "A Associação de Moradores e Amigos do Bairro Bom Retiro, conhecida como AMABRE, tem sua sede na Rua Recife, 480 Fds, no Bairro Bom Retiro, Município de Blumenau, Estado de Santa Catarina.\n\nÉ uma organização da sociedade civil, de duração indeterminada, de caráter representativo, reivindicatório, educativo, beneficente, sem fins lucrativos, político-partidários ou religiosos."
    },
    {
        "id": 2,
        "capitulo": "CAPÍTULO 1º - DA DENOMINAÇÃO, SEDE, DURAÇÃO, FINALIDADE E EXTINÇÃO",
        "titulo": "Artigo 2º - Da Finalidade",
        "texto": "A Associação tem por finalidade congregar todos os moradores e demais interessados no bairro, promover e lutar pelo bem comum, reivindicar melhorias e promover o desenvolvimento da comunidade."
    },
    {
        "id": 3,
        "capitulo": "CAPÍTULO 1º - DA DENOMINAÇÃO, SEDE, DURAÇÃO, FINALIDADE E EXTINÇÃO",
        "titulo": "Artigo 3º - Da Extinção e Destino do Patrimônio",
        "texto": "A Associação poderá ser extinta por decisão tomada em Assembleia Geral, previamente convocada com 30 (trinta) dias de antecedência e sob aprovação de 2/3 (dois terços) dos membros presentes na Assembleia Geral.\n\nParágrafo Único: Na extinção, o seu patrimônio será destinado a favor da comunidade que abrange esta Associação, sendo vedada a distribuição do patrimônio entre os associados."
    },
    {
        "id": 4,
        "capitulo": "CAPÍTULO 1º - DA DENOMINAÇÃO, SEDE, DURAÇÃO, FINALIDADE E EXTINÇÃO",
        "titulo": "Artigo 4º - Dos Associados: Admissão e Categorias",
        "texto": "A condição de associado não será automática. Para ser membro da AMABRE, a pessoa ou entidade precisa manifestar voluntariamente seu desejo de se associar e cumprir os requisitos definidos neste Estatuto.\n\nParágrafo Primeiro - Categorias de Associados:\n- Associado Morador: Pessoas físicas que residam nas ruas oficiais do bairro Bom Retiro.\n- Associado Empresarial/Institucional: Pessoas jurídicas com sede ou estabelecimento no bairro, representadas por seus sócios ou representantes legais.\n\nParágrafo Segundo - Processo de Admissão: Feita mediante preenchimento de ficha de inscrição e aprovação da Diretoria.\n\nParágrafo Terceiro - Direito a Voto: Terão direito a voto os associados em dia com suas obrigações e com idade superior a 16 (dezesseis) anos."
    },
    {
        "id": 5,
        "capitulo": "CAPÍTULO 1º - DA DENOMINAÇÃO, SEDE, DURAÇÃO, FINALIDADE E EXTINÇÃO",
        "titulo": "Artigo 5º - Da Não Responsabilidade dos Associados",
        "texto": "Os associados não respondem subsidiariamente pelas obrigações assumidas pela Associação."
    },
    {
        "id": 6,
        "capitulo": "CAPÍTULO 1º - DA DENOMINAÇÃO, SEDE, DURAÇÃO, FINALIDADE E EXTINÇÃO",
        "titulo": "Artigo 6º - Da Perda da Condição de Associado por Mudança",
        "texto": "O associado morador que mudar de residência ou o associado empresarial que mudar sua sede para fora do bairro perderá automaticamente os direitos de associado. Não haverá obrigação de ressarcimento ou devolução de valores por parte da Associação."
    },
    {
        "id": 7,
        "capitulo": "CAPÍTULO 1º - DA DENOMINAÇÃO, SEDE, DURAÇÃO, FINALIDADE E EXTINÇÃO",
        "titulo": "Artigo 7º - Das Vedações aos Associados",
        "texto": "É vedado aos associados a utilização do nome da Associação para fins pessoais, bem como campanha ou promoção que não sejam de interesse da comunidade representada."
    },
    {
        "id": 8,
        "capitulo": "CAPÍTULO 1º - DA DENOMINAÇÃO, SEDE, DURAÇÃO, FINALIDADE E EXTINÇÃO",
        "titulo": "Artigo 8º - Das Penalidades e Exclusão (Com Ampla Defesa)",
        "texto": "O associado que infringir disposições estatutárias, desabonar o nome da Associação ou perturbar a ordem será passível de: a) Advertência por escrito; b) Suspensão temporária; c) Exclusão.\n\nParágrafo Único - Processo de Exclusão: É obrigatório garantir o direito à ampla defesa e ao contraditório, incluindo notificação por escrito, prazo para defesa e direito de recurso para a Assembleia Geral."
    },
    {
        "id": 9,
        "capitulo": "CAPÍTULO 2º - DA ADMINISTRAÇÃO GERAL",
        "titulo": "Artigo 9º - Dos Órgãos de Administração e Mandato",
        "texto": "A Associação será administrada por: Diretoria, Conselho Fiscal e Assembleia de Associados.\n\nParágrafo Primeiro - Mandato: O mandato da Diretoria e do Conselho Fiscal é de 2 (dois) anos, sendo permitida a reeleição por mais um mandato na mesma função.\n\nParágrafo Segundo - Não Remuneração: Os membros da administração não receberão qualquer remuneração pelos cargos exercidos."
    },
    {
        "id": 10,
        "capitulo": "CAPÍTULO 2º - DA ADMINISTRAÇÃO GERAL",
        "titulo": "Artigo 10º a 18º - Atribuições e Composição da Diretoria",
        "texto": "A Diretoria é composta por Presidente, Vice-Presidente, 1º e 2º Secretários, 1º e 2º Tesoureiros (eleitos), e Diretores de Departamentos (nomeados). Todos têm direito a voz e voto.\n\nPrincipais deveres:\n- Presidente: Convocar/presidir reuniões e assinar documentos com tesoureiros/secretários.\n- 1º Tesoureiro: Responsável pelo controle financeiro, movimentação bancária e apresentação de 3 orçamentos para compras.\n- Perda de Mandato: O membro que faltar sem justa causa a 2 sessões consecutivas ou 4 alternadas perderá o mandato."
    },
    {
        "id": 19,
        "capitulo": "CAPÍTULO 2º - DA ADMINISTRAÇÃO GERAL",
        "titulo": "Artigo 19º e 20º - Do Conselho Fiscal",
        "texto": "Órgão autônomo composto por 3 membros efetivos e 3 suplentes eleitos.\n\nCompete ao Conselho examinar e dar parecer semestral sobre as contas da Diretoria, fiscalizar e solicitar a convocação de Assembleias Gerais Extraordinárias quando necessário."
    },
    {
        "id": 21,
        "capitulo": "CAPÍTULO 3º - DAS ASSEMBLEIAS GERAIS",
        "titulo": "Artigo 21º a 27º - Funcionamento e Quóruns da Assembleia",
        "texto": "A Assembleia é soberana. Reúne-se ordinariamente uma vez por ano e extraordinariamente quando necessário.\n\nQuóruns de Instalação:\n- 1ª Convocação: Metade mais um dos associados votantes.\n- 2ª Convocação (15 min após): Mínimo de 1/3 dos associados.\n- Última convocação: Qualquer número de presentes.\n\nQuóruns Especiais (Alteração do Estatuto, Destituição e Dissolução):\nAprovação exige 2/3 dos votos dos presentes. Na primeira convocação, exige-se no mínimo 1/5 do total de associados."
    },
    {
        "id": 28,
        "capitulo": "CAPÍTULO 4º - DO PROCESSO ELEITORAL",
        "titulo": "Artigo 28º a 34º - Regras de Eleição e Votação",
        "texto": "As eleições ocorrem em Assembleia Geral realizada no mínimo 30 dias antes do fim do mandato, sob voto direto e secreto.\n\nRegras básicas:\n- Dirigida por Comissão Eleitoral de 3 membros isentos.\n- Inscrição de chapas com antecedência mínima de 72 horas.\n- Em caso de empate, haverá 2º turno após 15 dias.\n- Direito a voto garantido aos associados com idade superior a 16 anos inscritos até o dia do pleito."
    },
    {
        "id": 35,
        "capitulo": "CAPÍTULO 5º - DAS DISPOSIÇÕES GERAIS",
        "titulo": "Artigo 35º a 38º - Convocações e Vigência",
        "texto": "Assembleia Geral Ordinária (AGO): Convocada por escrito com 15 dias de antecedência.\nAssembleia Geral Extraordinária (AGE): Convocada por editais públicos com 5 dias de antecedência.\nAmbas as convocações podem ser complementadas por e-mail, redes sociais e grupos oficiais do bairro.\nOs casos omissos são resolvidos pela Diretoria com ratificação da Assembleia."
    },
    {
        "id": 39,
        "capitulo": "CAPÍTULO 6º - DAS FONTES DE RECURSOS E GESTÃO FINANCEIRA",
        "titulo": "Artigo 39º a 41º - Finanças, Orçamentos e Auditoria",
        "texto": "Recursos provêm de doações, convênios, subvenções, eventos, mensalidades ou taxas.\n\nRegras de Transparência:\n- Uso obrigatório de sistema de gestão financeira e movimentação exclusiva em conta bancária.\n- Apresentação obrigatória e rigorosa de no mínimo 3 orçamentos para compras.\n- Disponibilização de balancetes à comunidade e possibilidade de contratação de auditoria independente."
    },
    {
        "id": 42,
        "capitulo": "CAPÍTULO 7º - DA GOVERNANÇA E ÉTICA",
        "titulo": "Artigo 42º a 44º - Conduta, Conflito de Interesses e Divulgação",
        "texto": "Criação de um Código de Conduta e Ética contra fraudes, assédio e nepotismo.\n\nPolítica de Conflito de Interesses: Qualquer membro com interesse pessoal em uma deliberação deve abster-se de votar.\n\nPolítica de Divulgação: Publicação transparente de relatórios financeiros, atas e contratos no site institucional ou murais da sede."
    }
]

RUAS_BOM_RETIRO = [
    "Rua Hermann Hering", "Rua Recife", "Rua Carijós", "Rua Palhoça", 
    "Rua Augusto Otte", "Rua Porto Alegre", "Rua Ernesto Emmendoefer", 
    "Rua Tiradentes", "Rua Gertrud G. Hering", "Rua Klara Hering", 
    "Rua Vitor Hering", "Rua Cuiabá", "Rua Richardt Holetz", 
    "Rua Dr. Francisco Knoch", "Rua Teresina", "Rua Belém", 
    "Rua Oswaldo Berndt", "Rua Voluntários da Pátria", 
    "Rua Alexandre Flemming", "Rua Sebaster Fischer", "Outra / Não morador"
]