import streamlit as st
import pandas as pd
from datetime import date
import time
import io




def excel_csv():
    col1, col2 = st.columns(2)
    with col1:

        nome = st.text_input('Informe um nome para salvar o arquivo', 'Nome do arquivo')
    with col2:  
        file = st.file_uploader("Selecione um arquivo Excel para converter: ", type=["xlsx"])
    if file:
        df = pd.read_excel(file)
        with st.spinner('Aguarde...'):
            time.sleep(1)
            st.success('Concluído com sucesso!', icon="✅")

        csv = df.to_csv(index=False).encode('UTF-8')
        st.download_button(
        label="Download do CSV",
                    data=csv,
                    file_name=f'{nome}.csv',
                    mime='text/csv'
            )
    return True



def csv_excel():
    col1, col2 = st.columns(2)
    with col1:
        nome = st.text_input('Informe um nome para salvar o arquivo', 'Nome do arquivo')
    with col2:  
        file = st.file_uploader("Selecione um arquivo em csv para converter: ", type=["csv"])
    if file:
        df = pd.read_csv(file)
        with st.spinner('Aguarde...'):
            time.sleep(1)
            st.success('Concluído com sucesso!', icon="✅")

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        # Configurar os parâmetros para o botão de download
        st.download_button(
            label="Download Excel",
            data=output.getvalue(),
            file_name=f'{nome}.xlsx',
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    return True

def app():
    st.info('Conversor de formatos de arquivos')
    option = st.radio("Converter",
                         ["XLSX para CSV", "CSV para XLSX"],
    )
    
    if option == 'XLSX para CSV':
        if option is not None:
            excel_csv()
    else:
        if option is not None:
            csv_excel()

        
