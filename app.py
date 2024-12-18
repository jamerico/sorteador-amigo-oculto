import streamlit as st
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
import os
from dotenv import load_dotenv

# Carrega as variáveis do .env
load_dotenv()

# Configuração da página
st.set_page_config(
    page_title="🎁 Sorteador de Amigo Oculto",
    page_icon="🎁",
    layout="centered"
)

# Estilo CSS personalizado
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #ff4b4b;
        color: white;
    }
    .stButton>button:hover {
        background-color: #ff3333;
    }
    </style>
""", unsafe_allow_html=True)

SENDER_EMAIL = "uilidades@gmail.com"

# Título principal com emoji
st.title("🎁 Sorteador de Amigo Oculto")

# Função para realizar o sorteio
def sortear_amigo_oculto(participantes):
    sorteio = participantes.copy()
    resultado = {}
    
    while True:
        shuffled = participantes.copy()
        random.shuffle(shuffled)
        valid = True
        
        for i in range(len(participantes)):
            if participantes[i] == shuffled[i]:
                valid = False
                break
                
        if valid:
            for i in range(len(participantes)):
                resultado[participantes[i]] = shuffled[i]
            break
            
    return resultado

# Função para enviar emails
def enviar_email(remetente_email, remetente_senha, usuario_remetente,destinatario, amigo_sorteado):
    try:
        # Configuração do servidor SMTP do Gmail
        smtp_server = "smtp.gmail.com"
        port = 587
        
        # Criar mensagem
        msg = MIMEMultipart()
        msg['From'] = remetente_email
        msg['To'] = destinatario
        msg['Subject'] = "🎁 Seu Amigo Oculto foi Sorteado!"
        
        body = f"""
        Olá!
        
        O sorteio do amigo oculto foi realizado! A pessoa que enviou esse email para você é: {usuario_remetente}
        
        Você tirou: {amigo_sorteado}
        
        Mantenha em segredo e prepare um presente especial! 🎁
        
        Boas festas! 🎄
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Criar conexão segura
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()
        
        # Login
        server.login(remetente_email, remetente_senha)
        
        # Enviar email
        text = msg.as_string()
        server.sendmail(remetente_email, destinatario, text)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Erro ao enviar email: {str(e)}")
        return False

# Interface principal
with st.form("formulario_amigo_oculto"):
    st.subheader("📧 Adicione os participantes")
    
    # Aviso sobre o email de envio
    st.info("📫 Os emails serão enviados através do endereço: " + SENDER_EMAIL)
    
    # Campo para nome do organizador
    nome_organizador = st.text_input(
        "👤 Seu nome (organizador)",
        placeholder="Digite seu nome aqui"
    )
    
    # Checkbox para modo de teste
    modo_teste = st.checkbox("🔍 Modo Teste (não envia emails)")
    
    
#     # Botão para usar emails de teste
#     if st.form_submit_button("📝 Usar emails de teste"):
#         emails_teste = """alice@teste.com
# bob@teste.com
# carol@teste.com
# david@teste.com
# eva@teste.com"""
#         st.session_state['emails_teste'] = emails_teste

    # Campo para adicionar emails
    emails_text = st.text_area(
        "Emails dos participantes (um por linha)",
        placeholder="participante1@email.com\nparticipante2@email.com\n..."
    )
        
    if 'emails_teste' in st.session_state:
        emails_text = st.session_state['emails_teste']
    
    # Botão de envio
    submitted = st.form_submit_button("🎲 Realizar Sorteio")
if submitted:
    if not nome_organizador:
        st.error("Por favor, digite seu nome!")
    elif not emails_text:
        st.error("Por favor, adicione os emails dos participantes!")
    else:
        # Processar lista de emails
        emails = [email.strip() for email in emails_text.split('\n') if email.strip()]
        
        if len(emails) < 3:
            st.error("É necessário pelo menos 3 participantes!")
        else:
            # Realizar sorteio
            if modo_teste:
                resultado_sorteio = sortear_amigo_oculto(emails)
                st.success("🎉 Sorteio realizado com sucesso!")
                st.balloons()
                
                # Mostrar resultado em uma tabela bonita
                st.subheader("📋 Resultado do Sorteio (Modo Teste)")
                resultado_df = pd.DataFrame(
                    {
                        "Participante": resultado_sorteio.keys(),
                        "Tirou": resultado_sorteio.values()
                    }
                )
                st.table(resultado_df)
                
                # Adicionar verificação de que ninguém tirou a si mesmo
                if any(k == v for k, v in resultado_sorteio.items()):
                    st.error("ERRO: Alguém tirou a si mesmo!")
                else:
                    st.success("✅ Verificação: Ninguém tirou a si mesmo!")
                
            else:
                with st.spinner('Realizando sorteio e enviando emails...'):
                    resultado_sorteio = sortear_amigo_oculto(emails)
                    
                    # Enviar emails usando as credenciais do ambiente
                    sucesso = True
                    for participante, amigo in resultado_sorteio.items():
                        if not enviar_email(SENDER_EMAIL, 
                                          os.getenv('GMAIL_APP_PASSWORD'),
                                          nome_organizador,
                                          participante, amigo):
                            sucesso = False
                            break
                    
                    if sucesso:
                        st.success("🎉 Sorteio realizado e emails enviados com sucesso!")
                        st.balloons()
                    else:
                        st.error("Houve um erro ao enviar os emails. Por favor, tente novamente mais tarde.")

# Instruções
with st.expander("ℹ️ Como usar"):
    st.markdown("""
    1. Adicione os emails dos participantes (um por linha)
    2. Clique em "Realizar Sorteio"
    3. Cada participante receberá um email com o nome da pessoa que deve presentear
    
    **Modo Teste**: Ative esta opção para ver o resultado do sorteio na tela sem enviar emails.
    """)

# Footer
st.markdown("---")
st.markdown(
    "Feito com ❤️ para tornar seu amigo oculto mais divertido!"
)