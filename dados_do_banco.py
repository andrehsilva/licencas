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
    

    path_db = 'database.db'
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
                file_name=f'db.xlsx',
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.info('Não há dados disponíveis', icon="😒")