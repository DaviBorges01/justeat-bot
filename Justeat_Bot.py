import time
import psycopg2
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fastapi import FastAPI
import uvicorn
import os

# Configuração do Selenium (modo headless para rodar sem abrir o navegador)
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Executa sem abrir o navegador
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=options)

# Conectar ao Supabase
DATABASE_URL = os.getenv("SUPABASE_DB_URL")  # Pegar do ambiente

# Função para obter conexão com o banco de dados
def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

# Função para buscar credenciais do usuário no Supabase
def get_user_credentials(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT justeat_email, justeat_password FROM bot_settings WHERE user_id = %s", (user_id,))
    user_data = cursor.fetchone()
    conn.close()  # Fecha a conexão corretamente
    return user_data if user_data else None

# Função para logar na nova URL do Just Eat
def login_to_justeat(user_id):
    user_data = get_user_credentials(user_id)
    if not user_data:
        return {"error": "Usuário não encontrado"}

    email, password = user_data

    driver.get("https://api-produk.skipthedishes.com/auth/realms/Courier/protocol/openid-connect/auth?client_id=courier_portal_jet_uk&redirect_uri=https%3A%2F%2Fcouriers.produk.skipthedishes.com%2Fapp%2F&response_type=code&scope=openid&state=7376c76d9039482daac8d09c2d37f095&code_challenge=xT8q5468VRqoUn8u_6WvdI6w5hVha_9iszdWSAPS0FM&code_challenge_method=S256")
    
    time.sleep(5)  # Espera carregar a página

    try:
        # Encontrar campo de login
        email_field = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        password_field = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "password"))
        )

        email_field.send_keys(email)
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)

        time.sleep(5)  # Espera login

        # Verificar se o login foi bem-sucedido
        if "dashboard" in driver.current_url or "app" in driver.current_url:
            return {"status": "Login bem-sucedido!"}
        else:
            return {"status": "Falha no login"}

    except Exception as e:
        return {"error": str(e)}

# Criar API com FastAPI
app = FastAPI()

@app.get("/login/{user_id}")
def login(user_id: str):
    return login_to_justeat(user_id)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
