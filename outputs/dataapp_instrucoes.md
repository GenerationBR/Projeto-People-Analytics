# Como Executar o Data App

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar o app
streamlit run app/calculadora.py

# O app abrirá em http://localhost:8501
```

## Pré-requisitos
- `data/analytics.duckdb` populado via `python main.py` (pipeline ETL + Modelagem)
- Python >= 3.11

## Deploy (opcional)
- Streamlit Community Cloud: https://streamlit.io/cloud
- Docker: `docker build -t people-analytics . && docker run -p 8501:8501 people-analytics`
