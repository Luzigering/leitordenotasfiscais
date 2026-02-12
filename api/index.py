
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai import types
import PIL.Image
import io
import os

app = FastAPI();
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],
)

API_KEY = os.environ.get("GEMINI_API_KEY")

@app.get("/")
def home():
    return {"status": "Online", "msg": "API de Notas Fiscais rodando!"}

@app.post("/analisar-nota")
async def analisar_nota(file: UploadFile = File(...)):
    if not API_KEY:
        raise HTTPException(status_code=500, detail="API Key não configurada no Vercel")

    # 1. Lê a imagem da memória (sem salvar no disco)
    try:
        contents = await file.read()
        image = PIL.Image.open(io.BytesIO(contents))
    except Exception:
        raise HTTPException(status_code=400, detail="Arquivo inválido. Envie uma imagem.")

    # 2. Configura o Cliente
    client = genai.Client(api_key=API_KEY)

    prompt = """
    Analise esta nota fiscal. Extraia: Estabelecimento, CNPJ, Data, Valor Total e Itens.
    Retorne APENAS um JSON válido.
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=[prompt, image],
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        # Retorna o JSON direto
        return {"sucesso": True, "dados": response.text}
        
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}