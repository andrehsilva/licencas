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
    st.subheader('Consulte as escolas de cada produto.')

    file = st.file_uploader("Selecione o relatório de itens em formato xlsx", type=["XLSX"])

    if file is not None:
        df = pd.read_excel(file)

        produto = st.text_input('Pesquise as escolas que tem pedido do produto:')
        produto = produto.upper()

        escolas = pd.read_excel('input/escolas_lex.xlsx')

        #Regex ajuste de cnpj
        p = re.compile(r'[../-]')
        escolas['CNPJ'] = [p.sub('', x) for x in escolas['CNPJ']]
        escolas['CNPJ'] = escolas['CNPJ'].astype('int64')
        #st.dataframe(df)
        df = df[['Data do pedido','Status do pedido','Nome do produto','Grupo de cliente','Quantidade do produto']]


        df = df.loc[df['Nome do produto'].str.contains(produto)]

        df = pd.merge(df, escolas, on='Grupo de cliente', how='inner')
       
        df['PRODUTO'] = produto
        df = df.rename(columns={'Nome do produto':'NOME PRODUTO','Quantidade do produto':'QUANTIDADE LICENÇAS'})
        df = df[['PRODUTO','NOME PRODUTO','QUANTIDADE LICENÇAS','CNPJ','TENANT_ID','TENANT_NAME','SCHOOL_ID','SCHOOL_NAME']]
        df = df.drop_duplicates()

        df_escolas = df.copy()
        df_escolas = df_escolas[['PRODUTO','CNPJ','TENANT_ID','TENANT_NAME','SCHOOL_ID','SCHOOL_NAME']]
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
        filter = df[['PRODUTO','NOME PRODUTO','QUANTIDADE LICENÇAS','CNPJ','TENANT_ID','TENANT_NAME','SCHOOL_ID','SCHOOL_NAME']]
        selected = st.selectbox('Selecione a escola:', ['',*filter['SCHOOL_NAME'].unique()])
        if selected:
            selected_school = filter[filter['SCHOOL_NAME'] == selected]
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