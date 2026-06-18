import streamlit as st
from data import ARTIGOS_ESTATUTO, RUAS_BOM_RETIRO, NOTAS_FIM_CAPITULO
import os
import difflib
# pyrefly: ignore [missing-import]
from libsql_client import create_client_sync
# pyrefly: ignore [missing-import]
from streamlit_mic_recorder import mic_recorder
# pyrefly: ignore [missing-import]
from supabase import create_client

# Configurações Iniciais da Página
st.set_page_config(page_title="Revisão Estatuto AMABRE", page_icon="📜", layout="centered")

# --- CONEXÃO COM O TURSO ---
# Configurar os segredos no .streamlit/secrets.toml ou nas variáveis de ambiente do deployment
TURSO_URL = st.secrets.get("TURSO_URL", "")
TURSO_AUTH_TOKEN = st.secrets.get("TURSO_AUTH_TOKEN", "")

def get_turso_client():
    if not TURSO_URL or not TURSO_AUTH_TOKEN:
        st.error("⚠️ Erro: Configurações do banco de dados Turso não encontradas nos segredos (.streamlit/secrets.toml).")
        raise ValueError("Turso credentials missing.")
    return create_client_sync(url=TURSO_URL, auth_token=TURSO_AUTH_TOKEN)

# --- CONEXÃO COM O SUPABASE ---
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")

def get_supabase_client():
    if not SUPABASE_URL or not SUPABASE_KEY or SUPABASE_KEY == "INSIRA_AQUI_A_SUA_SUPABASE_KEY_ANON_OU_SERVICE_ROLE":
        return None
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"Erro ao inicializar cliente Supabase: {e}")
        return None


# --- FUNÇÃO PARA SALVAR ÁUDIO NA NUVEM ---
def upload_audio_to_cloud(audio_bytes):
    """
    Envia o áudio gravado em bytes para o Supabase Storage Bucket 'audios'.
    Retorna a URL pública do arquivo enviado ou uma URL mock caso o Supabase não esteja configurado.
    """
    if audio_bytes is None:
        return None
    
    supabase = get_supabase_client()
    if supabase is None:
        st.warning("⚠️ Supabase não configurado. Usando link simulado para desenvolvimento local.")
        url_publica = f"https://armazenamento-nuvem.com/amabre/audio_{os.urandom(4).hex()}.wav"
        return url_publica
        
    try:
        filename = f"audio_{os.urandom(8).hex()}.wav"
        bucket_name = "audios"
        
        # Upload do áudio
        supabase.storage.from_(bucket_name).upload(
            filename,
            audio_bytes,
            file_options={"content-type": "audio/wav"}
        )
        
        # URL pública do arquivo
        public_url = supabase.storage.from_(bucket_name).get_public_url(filename)
        return public_url
    except Exception as e:
        st.error(f"Erro ao enviar áudio para o Supabase: {e}")
        return f"https://armazenamento-nuvem.com/amabre/error_{os.urandom(4).hex()}.wav"

# --- FUNÇÃO PARA PROCESSAR AVANÇO E FIM DE CAPÍTULO ---
def processar_avanco(indice, artigo, total_artigos, total_no_capitulo, posicao_no_capitulo):
    tem_notas = artigo['capitulo'] in NOTAS_FIM_CAPITULO
    if posicao_no_capitulo == total_no_capitulo and tem_notas:
        st.session_state.capitulo_concluido = artigo['capitulo']
        st.session_state.proximo_artigo_indice = indice + 1 if indice + 1 < total_artigos else None
        st.session_state.passo = "fim_capitulo"
    else:
        if indice + 1 < total_artigos:
            st.session_state.artigo_atual = indice + 1
            st.session_state.passo = "revisao"
        else:
            st.session_state.artigo_atual = 0
            st.session_state.passo = "obrigado"

# --- FUNÇÃO PARA COMPARAÇÃO TEXTUAL (TRACK CHANGES) ---
def gerar_track_changes(texto_antigo, texto_novo):
    texto_antigo = (texto_antigo or "").strip()
    texto_novo = (texto_novo or "").strip()
    
    if not texto_antigo:
        return f"<span style='color: #155724; background-color: #d4edda; padding: 2px 6px; border-radius: 4px; font-weight: bold;'>[Novo Artigo Inédito]</span><br><br>{texto_novo}"
        
    palavras_antigas = texto_antigo.split()
    palavras_novas = texto_novo.split()
    
    matcher = difflib.SequenceMatcher(None, palavras_antigas, palavras_novas)
    html_out = []
    
    for op, i1, i2, j1, j2 in matcher.get_opcodes():
        if op == 'equal':
            html_out.append(" ".join(palavras_antigas[i1:i2]))
        elif op == 'replace':
            removido = " ".join(palavras_antigas[i1:i2])
            adicionado = " ".join(palavras_novas[j1:j2])
            html_out.append(f"<span style='background-color: #f8d7da; color: #721c24; text-decoration: line-through; padding: 1px 3px; border-radius: 2px;'>{removido}</span>")
            html_out.append(f"<span style='background-color: #d4edda; color: #155724; padding: 1px 3px; border-radius: 2px;'>{adicionado}</span>")
        elif op == 'delete':
            removido = " ".join(palavras_antigas[i1:i2])
            html_out.append(f"<span style='background-color: #f8d7da; color: #721c24; text-decoration: line-through; padding: 1px 3px; border-radius: 2px;'>{removido}</span>")
        elif op == 'insert':
            adicionado = " ".join(palavras_novas[j1:j2])
            html_out.append(f"<span style='background-color: #d4edda; color: #155724; padding: 1px 3px; border-radius: 2px;'>{adicionado}</span>")
            
    return " ".join(html_out).replace("\n", "<br>")

# --- INICIALIZAÇÃO DO ESTADO DE SESSÃO ---
if "passo" not in st.session_state:
    st.session_state.passo = "cadastro"
if "artigo_atual" not in st.session_state:
    st.session_state.artigo_atual = 0
if "usuario_id" not in st.session_state:
    st.session_state.usuario_id = None
if "usuario_nome" not in st.session_state:
    st.session_state.usuario_nome = ""
if "fonte_grande" not in st.session_state:
    st.session_state.fonte_grande = False
if "capitulo_concluido" not in st.session_state:
    st.session_state.capitulo_concluido = None
if "proximo_artigo_indice" not in st.session_state:
    st.session_state.proximo_artigo_indice = None

# --- DADOS DO ESTATUTO IMPORTADOS DE DATA.PY ---
# ARTIGOS_ESTATUTO e RUAS_BOM_RETIRO são carregados dinamicamente do data.py


# --- CONTROLE DE ACESSIBILIDADE ---
tamanho_texto = "22px" if st.session_state.fonte_grande else "17px"
tamanho_titulo = "28px" if st.session_state.fonte_grande else "22px"

st.markdown(f"""
    <style>
    .texto-estatuto {{ font-size: {tamanho_texto} !important; line-height: 1.6; color: #1E1E1E; }}
    .titulo-artigo {{ font-size: {tamanho_titulo} !important; font-weight: bold; color: #0C2340; }}
    </style>
""", unsafe_allow_html=True)

# Botão de Aumentar Letra
_, col_t2 = st.columns([3, 1])
with col_t2:
    if st.button("🔎 Aumentar Letra" if not st.session_state.fonte_grande else "🔍 Letra Normal", use_container_width=True):
        st.session_state.fonte_grande = not st.session_state.fonte_grande
        st.rerun()

# --- TELA 1: CADASTRO NO TURSO ---
if st.session_state.passo == "cadastro":
    st.title("📜 Consulta Pública: Estatuto AMABRE")
    st.write("Olá, vizinho(a)! Identifique-se para começarmos a votar item por item.")
    
    nome = st.text_input("Seu Nome Completo:")
    rua = st.selectbox("Sua Rua no Bom Retiro:", ["Selecione sua rua..."] + RUAS_BOM_RETIRO)
    whatsapp = st.text_input("Seu WhatsApp (Opcional):")
    
    if st.button("Iniciar Avaliação ➡️", use_container_width=True, type="primary"):
        if nome and rua != "Selecione sua rua...":
            try:
                client = get_turso_client()
                
                # Verifica se o usuário com este nome e rua já existe no banco
                existing_user = client.execute("SELECT id FROM usuarios WHERE nome = ? AND rua = ?", (nome, rua))
                
                if existing_user.rows:
                    # Usuário existente: restaura o estado anterior
                    usuario_id = existing_user.rows[0][0]
                    st.session_state.usuario_id = usuario_id
                    st.session_state.usuario_nome = nome
                    
                    # Busca quais artigos este usuário já votou
                    voted_res = client.execute("SELECT artigo_id FROM respostas WHERE usuario_id = ?", (usuario_id,))
                    voted_ids = {row[0] for row in voted_res.rows}
                    
                    # Encontra o primeiro artigo que ainda não foi votado
                    proximo_indice = 0
                    for idx, artigo in enumerate(ARTIGOS_ESTATUTO):
                        if artigo['id'] not in voted_ids:
                            proximo_indice = idx
                            break
                    else:
                        # Se já respondeu a tudo, vai para a tela de agradecimento
                        st.session_state.passo = "obrigado"
                        st.session_state.artigo_atual = 0
                        st.rerun()
                        
                    st.session_state.artigo_atual = proximo_indice
                    st.session_state.passo = "revisao"
                    st.rerun()
                else:
                    # Novo usuário: insere no banco
                    res = client.execute("INSERT INTO usuarios (nome, rua, whatsapp) VALUES (?, ?, ?) RETURNING id", (nome, rua, whatsapp))
                    st.session_state.usuario_id = res.rows[0][0]
                    st.session_state.usuario_nome = nome
                    st.session_state.artigo_atual = 0
                    st.session_state.passo = "revisao"
                    st.rerun()
            except Exception as e:
                st.error(f"Erro ao conectar ao banco de dados Turso: {e}")
        else:
            st.error("⚠️ Por favor, preencha seu Nome e escolha sua Rua.")

# --- TELA 2: VOTAÇÃO E CAPTURA DE ÁUDIO ---
elif st.session_state.passo == "revisao":
    total_artigos = len(ARTIGOS_ESTATUTO)
    indice = st.session_state.artigo_atual
    artigo = ARTIGOS_ESTATUTO[indice]
    
    # Filtra os artigos do capítulo atual e calcula progresso interno
    artigos_do_capitulo = [a for a in ARTIGOS_ESTATUTO if a['capitulo'] == artigo['capitulo']]
    total_no_capitulo = len(artigos_do_capitulo)
    posicao_no_capitulo = artigos_do_capitulo.index(artigo) + 1
    
    st.progress(indice / total_artigos)
    st.caption(f"Artigo {posicao_no_capitulo} de {total_no_capitulo} do {artigo['capitulo']} | Progresso Geral: {indice + 1} de {total_artigos}")
    
    st.markdown(f"<div class='titulo-artigo'>{artigo['titulo']}</div>", unsafe_allow_html=True)
    st.markdown(f"""
        <div style="background-color: #F0F4F8; padding: 20px; border-left: 5px solid #0C2340; border-radius: 4px; margin-bottom: 20px;">
            <p class="texto-estatuto">{artigo['texto']}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Painel comparativo (Track Changes)
    texto_ant = artigo.get("texto_antigo", "").strip()
    with st.expander("🔍 Mostrar Comparativo (Track Changes / O que mudou)"):
        diff_html = gerar_track_changes(texto_ant, artigo['texto'])
        st.markdown(f"""
            <div style="background-color: #FFFFFF; border: 1px solid #E0E0E0; padding: 15px; border-radius: 4px; font-size: 16px; line-height: 1.6; color: #333333; overflow-x: auto;">
                {diff_html}
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### O que você acha desta regra?")
    col_b1, col_b2, col_b3 = st.columns(3)
    voto_selecionado = None
    
    with col_b1:
        if st.button("👍 Concordo", key=f"ok_{indice}", use_container_width=True):
            voto_selecionado = "Concordo"
    with col_b2:
        if st.button("👎 Mudar algo", key=f"nok_{indice}", use_container_width=True):
            voto_selecionado = "Sugerir Alteração"
    with col_b3:
        if st.button("⏭️ Pular Item", key=f"jmp_{indice}", use_container_width=True):
            voto_selecionado = "Pulei"

    # Botão para voltar ao artigo anterior (exibido a partir do segundo artigo)
    if indice > 0:
        st.write("")
        if st.button("⬅️ Voltar ao Artigo Anterior", key=f"back_{indice}", use_container_width=True):
            st.session_state.artigo_atual -= 1
            if "sugestao_ativa" in st.session_state:
                del st.session_state.sugestao_ativa
            st.rerun()

    # Se clicar em Mudar Algo, abre painel de feedback detalhado
    if voto_selecionado == "Sugerir Alteração" or "sugestao_ativa" in st.session_state:
        st.session_state.sugestao_ativa = True
        
        st.warning("Você prefere escrever ou falar sua sugestão?")
        comentario_texto = st.text_area("Deixe sua sugestão por escrito (se preferir):", key=f"txt_{indice}")
        
        st.write("🎙️ **Prefere falar? Clique no botão abaixo para gravar seu áudio:**")
        audio_gravado = mic_recorder(start_prompt="🔴 Iniciar Gravação", stop_prompt="⏹️ Parar e Enviar", key=f"audio_{indice}")
        
        if audio_gravado:
            # Processa o áudio binário gravado e joga na nuvem
            audio_url = upload_audio_to_cloud(audio_gravado['bytes'])
            
            # Remove voto anterior do mesmo artigo para evitar duplicatas
            client = get_turso_client()
            client.execute("DELETE FROM respostas WHERE usuario_id = ? AND artigo_id = ?", (st.session_state.usuario_id, artigo['id']))
            
            # Envia o novo voto para o Turso
            client.execute(
                "INSERT INTO respostas (usuario_id, artigo_id, titulo_artigo, voto, comentario, audio_url) VALUES (?, ?, ?, ?, ?, ?)",
                (st.session_state.usuario_id, artigo['id'], artigo['titulo'], "Rejeitado/Alterar", "Enviado por Áudio", audio_url)
            )
            
            del st.session_state.sugestao_ativa
            st.success("Áudio gravado e enviado com sucesso!")
            processar_avanco(indice, artigo, total_artigos, total_no_capitulo, posicao_no_capitulo)
            st.rerun()
            
        if st.button("Enviar Sugestão por Texto ➡️", key=f"env_txt_{indice}", type="primary"):
            client = get_turso_client()
            # Remove voto anterior do mesmo artigo para evitar duplicatas
            client.execute("DELETE FROM respostas WHERE usuario_id = ? AND artigo_id = ?", (st.session_state.usuario_id, artigo['id']))
            
            # Envia o novo voto para o Turso
            client.execute(
                "INSERT INTO respostas (usuario_id, artigo_id, titulo_artigo, voto, comentario, audio_url) VALUES (?, ?, ?, ?, ?, ?)",
                (st.session_state.usuario_id, artigo['id'], artigo['titulo'], "Rejeitado/Alterar", comentario_texto, None)
            )
            del st.session_state.sugestao_ativa
            processar_avanco(indice, artigo, total_artigos, total_no_capitulo, posicao_no_capitulo)
            st.rerun()

    elif voto_selecionado in ["Concordo", "Pulei"]:
        client = get_turso_client()
        # Remove voto anterior do mesmo artigo para evitar duplicatas
        client.execute("DELETE FROM respostas WHERE usuario_id = ? AND artigo_id = ?", (st.session_state.usuario_id, artigo['id']))
        
        # Envia o novo voto para o Turso
        client.execute(
            "INSERT INTO respostas (usuario_id, artigo_id, titulo_artigo, voto, comentario, audio_url) VALUES (?, ?, ?, ?, ?, ?)",
            (st.session_state.usuario_id, artigo['id'], artigo['titulo'], voto_selecionado, "", None)
        )
        processar_avanco(indice, artigo, total_artigos, total_no_capitulo, posicao_no_capitulo)
        st.rerun()

    # Exibe o texto antigo de referência em cinza no final do card
    st.write("---")
    st.markdown("### 📜 Referência: Texto do Estatuto Anterior")
    texto_ant = artigo.get("texto_antigo", "").strip()
    if not texto_ant:
        texto_ant = "Sem correspondência direta com o estatuto anterior"
    st.markdown(f"""
        <div style="color: #7A7A7A; background-color: #F9F9F9; padding: 15px; border-left: 5px solid #CCCCCC; border-radius: 4px; font-size: 15px; line-height: 1.5;">
            <i>{texto_ant.replace('\n', '<br>')}</i>
        </div>
    """, unsafe_allow_html=True)

# --- TELA: TRANSICAO / FIM DE CAPITULO ---
elif st.session_state.passo == "fim_capitulo":
    st.balloons()
    st.title("✨ Capítulo Concluído!")
    cap = st.session_state.capitulo_concluido
    st.markdown(f"Você concluiu a análise do **{cap}**!")
    
    # Exibe as notas do capítulo
    notas = NOTAS_FIM_CAPITULO.get(cap, [])
    if notas:
        st.markdown("### 💡 Resumo das principais alterações deste capítulo:")
        for nota in notas:
            st.info(nota)
    
    st.write("---")
    
    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        if st.button("⬅️ Voltar e Corrigir Último Artigo", use_container_width=True):
            # Volta para a revisão do último artigo analisado
            st.session_state.passo = "revisao"
            st.rerun()
            
    with col_nav2:
        btn_label = "Avançar para o Próximo Capítulo ➡️" if st.session_state.proximo_artigo_indice is not None else "Concluir Revisão e Finalizar ➡️"
        if st.button(btn_label, use_container_width=True, type="primary"):
            if st.session_state.proximo_artigo_indice is not None:
                st.session_state.artigo_atual = st.session_state.proximo_artigo_indice
                st.session_state.passo = "revisao"
            else:
                st.session_state.artigo_atual = 0
                st.session_state.passo = "obrigado"
            st.session_state.capitulo_concluido = None
            st.session_state.proximo_artigo_indice = None
            st.rerun()

# --- TELA 3: AGRADECIMENTO ---
elif st.session_state.passo == "obrigado":
    st.balloons()
    st.title("🎉 Muito Obrigado!")
    st.markdown(f"Obrigado **{st.session_state.usuario_nome}**, todas as suas respostas foram salvas com segurança no nosso banco de dados na nuvem!")
    if st.button("Revisar Novamente 🔄"):
        st.session_state.passo = "cadastro"
        st.rerun()