from fastapi import APIRouter, Body, Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch
import re
import os
from dotenv import load_dotenv

router = APIRouter()

# Sicurezza: solo utenti autenticati
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

def safe_text(text):
    # Rimuove caratteri pericolosi e limita la lunghezza
    return re.sub(r'[^\w\s.,;:?!-]', '', str(text))[:300]

def build_messages(user_input, sensors, footprint):
    # Prompt naturale ma con contesto chiaro e vincolante
    system_msg = (
        "Rispondi solo come esperto di agricoltura sostenibile. "
        "Dai consigli pratici e realistici per ottimizzare i consumi e ridurre il carbon footprint aziendale. "
        "Personalizza i suggerimenti in base ai valori attuali dei sensori e del carbon footprint forniti, spiegando sempre il motivo di ogni consiglio rispetto a questi dati. "
        "Non rispondere a domande fuori tema e non inventare dati. "
        "Se la domanda non riguarda la sostenibilità o l'ottimizzazione dei consumi, rispondi in modo gentile che puoi aiutare solo su strategie per ridurre il carbon footprint in agricoltura."
        "Non fornire risposte generiche o vaghe, ma sii specifico e pratico."
        "Rispondi in italiano e non ripettere il testo della domanda dell'utente."
    )
    sensori_str = ""
    if sensors:
        sensori_str = (
            f"I dati attuali del suolo sono: salinità {sensors.get('salinity', '?')} dS/m, "
            f"pH {sensors.get('ph', '?')}, umidità {sensors.get('soil_moisture', '?')}%, "
            f"sostanza organica {sensors.get('organic_matter', '?')}%."
        )
    footprint_str = ""
    if footprint and isinstance(footprint, dict) and 'totale_kgCO2eq' in footprint:
        footprint_str = (
            f"Il carbon footprint stimato dell'azienda è di {footprint['totale_kgCO2eq']} kg CO₂eq. "
            "Dettaglio: " + ", ".join(
                f"{d['parametro']}: {d['co2']} kg CO₂eq" for d in footprint.get('dettaglio', [])
            )
        )
    user_msg = f"{safe_text(user_input)}\n{sensori_str}\n{footprint_str}"
    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_msg}
    ]
    return messages

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
llama_token = os.getenv("HF_TOKEN")

base_model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"  # Modello TinyLlama proposto

model = AutoModelForCausalLM.from_pretrained(
    base_model_id,
    token=llama_token,
    torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
    device_map="auto",
)

tokenizer = AutoTokenizer.from_pretrained(base_model_id, token=llama_token)

llama_pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=512,
    do_sample=True,
    temperature=0.7
)

@router.post('/chat_suggestion')
def chat_suggestion(
    user_input: str = Body(...),
    sensors: dict = Body(...),
    footprint: dict = Body(None),
    token: str = Depends(oauth2_scheme)
):
    messages = build_messages(user_input, sensors, footprint)
    try:
        prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        outputs = llama_pipe(
            prompt,
            max_new_tokens=512,
            do_sample=True,
            temperature=0.7,
            top_k=50,
            top_p=0.85
        )
        result = outputs[0]['generated_text']
        answer = result[len(prompt):].strip()
    except Exception as e:
        print(f"Errore durante la generazione del testo: {e}")
        raise HTTPException(status_code=500, detail="Errore nel sistema di suggerimento.")
    return {"answer": answer}
