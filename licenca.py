import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date
import re

def app():
    st.subheader('Script de cadastro de licenças!')
    file = st.file_uploader("Selecione o relatório de itens em formato .csv", type=["XLSX"])
    data_atual = date.today().strftime('%d-%m-%Y')
    print(data_atual)

    if file is not None:
        df = pd.read_excel(file)
        #st.dataframe(df)

        #### IMPORTS DE BASES ##############
        combos = pd.read_excel('input/combos.xlsx', sheet_name='COMBOS')
        #combos = combos[~combos['CÓDIGO DO COMBO NA LEX'].str.contains('Não se aplica| ')]
        #st.dataframe(combos)
    
        escolas = pd.read_excel('input/base.xlsx', sheet_name='escolas')
        #st.dataframe(df_escolas)
    
        seg = pd.read_excel('input/base.xlsx', sheet_name='segmentos')
        #st.dataframe(seg)
    
        grade_bilingue = pd.read_excel('input/base.xlsx', sheet_name='grade_bilingue')
        #st.dataframe(grade_bilingue)
    
        grade_itinerario = pd.read_excel('input/base.xlsx', sheet_name='grade_itinerario')
        #st.dataframe(grade_itinerario)
        ############END IMPORT######################
    
        df_relatorio = df.copy()
        df_relatorio = df_relatorio.drop(columns=['Nome da loja', 'N pedido pai','Rua (endereco de cadastro)','Status da integração',
                                              'Nome Sobrenome/razao social nome fantasia','CPF','ID Usuário LEX','Rua (endereco de cadastro)',
                                              'Numero (endereco de cadastro)','Complemento (endereco de cadastro)','Bairro (endereco de cadastro)',
                                              'Cidade (endereco de cadastro)','Estado (endereco de cadastro)','Cep (endereco de cadastro)',
                                              'Valor unitario','Valor total itens','MARCA','Telefone (endereco de cadastro)','Email',
                                              'Celular (endereco de cadastro)','Rua (endereco de entrega)','Numero (endereco de entrega)',
                                              'Complemento (endereco de entrega)','Bairro (endereco de entrega)','Cidade (endereco de entrega)',
                                              'Estado (endereco de entrega)','Cep (endereco de entrega)','Telefone (endereco de entrega)',
                                              'Celular (endereco de entrega)','Total de itens do pedido','Codigo cupom',
                                              'Valor total Solução','Porcentagem de desconto do cliente','Método de pagamento','Valor do desconto','Valor liquido',
                                              'Bandeira do cartão','Frete do Marketplace','CLIENTE','TIPO DE FATURAMENTO','Parcelamento','Comissão','UTILIZAÇÃO'])
        #'TIPO DE PRODUTO',
        #st.dataframe(df_relatorio)
        df_relatorio = df_relatorio.loc[df_relatorio['Tipo pessoa'] == 'Pessoa jurídica']
        #df_relatorio = df_relatorio.dropna(subset=['Ean do produto'])
        df_relatorio = df_relatorio.loc[df['ANO PRODUTO'] == 2024]
        df_relatorio['ANO PRODUTO'] = df_relatorio['ANO PRODUTO'].astype('int64')
        df_relatorio['CNPJ'] = pd.to_numeric(df_relatorio['CNPJ'], downcast='integer')
        df_relatorio['Ean do produto'] = pd.to_numeric(df_relatorio['Ean do produto'], downcast='integer')
        #df_relatorio['Ean do produto'] = df_relatorio['Ean do produto'].astype('int64')
        df_relatorio['Data do pedido'] = df_relatorio['Data do pedido'].astype('datetime64[ns]')
        df_relatorio['Data do pedido'] = df_relatorio['Data do pedido'].dt.strftime('%d/%m/%Y')
        df_relatorio = df_relatorio[df_relatorio['Status do pedido'].isin(['Processando','Aprovado','Parcialmente Entregue','Entregue','Faturado','Parcialmente Faturado','Enviado'])] #Faturado
        df_relatorio = df_relatorio.loc[df_relatorio['Data do pedido'] > '2023-10-01 00:00:00']
        df_relatorio = df_relatorio.drop_duplicates()
        df_relatorio['CNPJ'] = df_relatorio['CNPJ'].astype('int64')
        
        #st.stop()

        df_escolas = escolas
        df_escolas = df_escolas.drop(columns=['TenantName','CorporationName'])
        df_escolas = df_escolas.drop_duplicates()
        df_escolas = df_escolas[['SchoolCNPJ','TenantId','SchoolId','SchoolName']]
        df_escolas = df_escolas.dropna()
        df_escolas = df_escolas.rename(columns={'SchoolCNPJ':'CNPJ'})
        df_escolas = df_escolas[~df_escolas['SchoolName'].str.contains('Concurso de Bolsa')]
        #Regex ajuste de cnpj
        #p = re.compile(r'[../-]')
        #df_escolas['CNPJ'] = [p.sub('', x) for x in df_escolas['CNPJ']]
        #df_escolas['CNPJ'] = df_escolas['CNPJ'].astype('int64')
    
        df_combos = combos.copy()
        df_combos = df_combos[['SKU','NOME DA LICENÇA','MARCA','CÓDIGO DO COMBO NA LEX']]
        df_combos = df_combos.rename(columns={'SKU':'Ean do produto','CÓDIGO DO COMBO NA LEX':'ComboCode','NOME NO MAGENTO':'LicenseName','Data do pedido':'OrderDate'})
    
        df_relatorio_combos = pd.merge(df_relatorio, df_combos, on=['Ean do produto'], how='inner')
        df_relatorio_combos = df_relatorio_combos.rename(columns={'LicenseName_x':'LicenseName'})
        df_relatorio_combos = df_relatorio_combos.drop_duplicates()
        df_relatorio_combos = df_relatorio_combos.rename(columns={'SÉRIE':'Grade'})

        df_relatorio_combos = pd.merge(df_relatorio_combos, seg, how='left', on='Grade')
        df_relatorio_combos = df_relatorio_combos.drop(columns=['Grade'])
        df_relatorio_combos = df_relatorio_combos.rename(columns={'Grade_tag':'Grade'})
       
        df_relatorio_combos_escolas = pd.merge(df_relatorio_combos, df_escolas,  on=['CNPJ'], how='left')
        df_relatorio_combos_escolas = df_relatorio_combos_escolas.drop_duplicates()
        
        df = df_relatorio_combos_escolas.copy()

        df = df.assign(StartDate='01/01/2024',EndDate='31/12/2024',Coordinator='1',Manager='1', Operator='1',Teacher='1',Sponsor='1', Secretary='1',Reviewer='1')
        df = df.rename(columns={'SchoolId':'School','TenantId':'Tenant', 'N pedido':'OrderNumber', 'Quantidade do produto':'Student', 'SÉRIE_x':'Grade','Data do pedido':'OrderDate', 'NOME DA LICENÇA':'LicenseName' })
        df = df.drop(columns=['Sku do produto'])
        df = df[['Tenant','School','ComboCode','LicenseName','StartDate','EndDate','Grade','OrderNumber','OrderDate','Student','Coordinator','Manager','Operator','Teacher','Sponsor','Secretary','Reviewer','SchoolName','CNPJ','Ean do produto']]
        df[['OrderNumber','Student','Coordinator','Manager','Operator','Teacher','Sponsor','Secretary','Reviewer']] = df[['OrderNumber','Student','Coordinator','Manager','Operator','Teacher','Sponsor','Secretary','Reviewer']]. astype('int64')
        df = df.sort_values('Student', ascending=False)

        df['Teacher'] = df['Student'].apply(lambda x: 1 if x < 21 else x//20)
        
    
        st.dataframe(df)
    
        
    
        #df_relatorio.to_excel('output/df_relatorio.xlsx')