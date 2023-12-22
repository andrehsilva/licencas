import streamlit as st
import pandas as pd
from datetime import date
import time
import io
import numpy as np
import re
import unicodedata


today = date.today().strftime('%d-%m-%Y')
year = date.today().strftime('%Y')




def app():
    st.subheader('Relação de escolas para cada produto.')

    file = st.file_uploader("Selecione o relatório de itens em formato xlsx", type=["XLSX"])

    if file is not None:
        df = pd.read_excel(file)

        produto = st.text_input('Pesquise as escolas que tem pedido do produto:')
        produto = produto.upper()

        escolas = pd.read_excel('input/escolas_lex.xlsx')

        #Regex ajuste de cnpj
        
        escolas['CNPJ'] = escolas['CNPJ'].astype('int64')
        #st.dataframe(df)
        df = df[['Data do pedido','Status do pedido','Nome do produto','Grupo de cliente','Quantidade do produto']]


        df = df.loc[df['Nome do produto'].str.contains(produto)]

        df = pd.merge(df, escolas, on='Grupo de cliente', how='inner')
       
        df['PRODUTO'] = produto
        df = df.rename(columns={'PRODUTO':'Produto','Nome do produto':'Nome do produto','Quantidade do produto':'Quantidade de Licenças'})
        df = df[['Produto','Nome do produto','Quantidade de Licenças','CNPJ','TenantId','TenantName','SchoolId','SchoolName']]
        df = df.drop_duplicates()

        df_escolas = df.copy()
        df_escolas = df_escolas[['Produto','CNPJ','TenantId','TenantName','SchoolId','SchoolName']]
        df_escolas = df_escolas.drop_duplicates()



        st.divider()
        with st.spinner('Aguarde...'):
            time.sleep(3)
        st.success('Concluído com sucesso!', icon="✅")
        def convert_df(df):
            # IMPORTANT: Cache the conversion to prevent computation on every rerun
            return df.to_csv(index=False).encode('UTF-8')


        col1, col2= st.columns(2)
        with col1:
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
                # Configurar os parâmetros para o botão de download
            st.download_button(
                    label="Download detalhado do produto",
                data=output.getvalue(),
                file_name=f'{today}full-{produto}.xlsx',
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        with col2:
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_escolas.to_excel(writer, index=False)
                # Configurar os parâmetros para o botão de download
            st.download_button(
                    label="Download das escolas que compraram o produto",
                data=output.getvalue(),
                file_name=f'{today}{produto}.xlsx',
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        

        ###### DEBUG COM FILTRO
        st.divider()
        st.write('Resultado:')
        filter = df[['Produto','Nome do produto','Quantidade de Licenças','CNPJ','TenantId','TenantName','SchoolId','SchoolName']]
        selected = st.selectbox('Selecione a escola:', ['',*filter['SchoolName'].unique()])
        if selected:
            selected_school = filter[filter['SchoolName'] == selected]
            st.dataframe(selected_school)

            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                selected_school.to_excel(writer, index=False)
                # Configurar os parâmetros para o botão de download
            st.download_button(
                    label="Download da seleção",
                data=output.getvalue(),
                file_name=f'{selected}{produto}.xlsx',
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.dataframe(filter)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                filter.to_excel(writer, index=False)
                # Configurar os parâmetros para o botão de download
            st.download_button(
                    label="Download",
                data=output.getvalue(),
                file_name=f'Escolas_{produto}.xlsx',
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        ##################