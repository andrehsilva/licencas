import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date
import re
import time
import io
import sqlite3
from pathlib import Path

def app():

    today = date.today().strftime('%d-%m-%Y')
    year = date.today().strftime('%Y')

    path_db = 'database.db'

    file = st.file_uploader("Salvar no banco de dados uma planilha manual", type=["XLSX"])
    data_atual = date.today().strftime('%d-%m-%Y')

    if file is not None:
        df = pd.read_excel(file)

        date_columns = ['StartDate', 'EndDate', 'OrderDate', 'date']
        for col in date_columns:
            df[col] = pd.to_datetime(df[col]).dt.strftime('%d/%m/%Y')
        
        def remove_accentuation(cnpj):
            pattern = re.compile('[^A-Za-z0-9]+')
            return re.sub(pattern, '', cnpj)

        # Aplicar a função à coluna 'CNPJ'
        df['CNPJ'] = df['CNPJ'].apply(remove_accentuation)

        st.dataframe(df)
        conn = sqlite3.connect(path_db)
        df.to_sql('licencas', conn, index=False, if_exists='append')
        conn.close()
        
    
    with st.spinner('Aguarde...'):
        time.sleep(2)


    st.divider()

    
    if Path(path_db).is_file():
        st.subheader('Baixar dados!')
        conn = sqlite3.connect(path_db)
        licenca = 'SELECT * FROM licencas'
        dado = pd.read_sql_query(licenca, conn)
        dado = dado.drop_duplicates()
        conn.close()
        col1, col2, col3 = st.columns(3)
        with col1:
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                dado.to_excel(writer, index=False)
                # Configurar os parâmetros para o botão de download
            st.download_button(
                    label="Download do banco de dados",
                data=output.getvalue(),
                file_name=f'{today}-db.xlsx',
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        st.divider()

        df_error = dado.query('School.isna()')
        if df_error.__len__():
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_error.to_excel(writer, index=False)
     
            st.download_button(
                label="Download de erros",
                data=output.getvalue(),
                file_name=f'{today}{today}-erros.xlsx',
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",               
            )
            st.dataframe(df_error)
    
        
        


    else:
        st.info('Não há dados disponíveis', icon="😒")


    