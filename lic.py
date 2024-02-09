import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date
import re
import time
import io
import sqlite3
from pathlib import Path


today = date.today().strftime('%d-%m-%Y')
year = date.today().strftime('%Y')


def app():
    st.subheader('Gerador de planilha de importação de licenças Lex!')

    file = st.file_uploader("Importe o relatório de itens em formato .xlsx", type=["XLSX"])
    data_atual = date.today().strftime('%d-%m-%Y')
    data_2 = date.today().strftime('%d/%m/%Y')
    print(data_atual)
    

    if file is not None:
        df = pd.read_excel(file)
        #file = None
        #st.dataframe(df)

        #### IMPORTS DE BASES ##############
        combos = pd.read_excel('input/combos.xlsx')
        combos = combos[['MARCA','SKU','DESCRIÇÃO MAGENTO (B2C e B2B)','PRODUTO','CÓDIGO DO COMBO','TAG REGULAR','TAG BILINGUE','TAG PREMIUM','SÉRIE']]
        combos = combos[~combos['PRODUTO'].str.contains('NÃO SE APLICA')]
       
        escolas = pd.read_excel('input/escolas_lex.xlsx')
        #st.dataframe(escolas)
    
        df_relatorio = df.copy()
        
        df_relatorio = df_relatorio.loc[df_relatorio['Tipo pessoa'] == 'Pessoa jurídica']
        df_relatorio = df_relatorio.query('(`Codigo cupom` != "AMOST_100%_2022") and (`Codigo cupom` != "AMOST_100%")')


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
        ### planilha de soluções ####

        df_relatorio = df_relatorio.loc[~(df_relatorio['Ean do produto'].isnull())] 
        #df_relatorio = df_relatorio.loc[df['ANO PRODUTO'] == 2024]
        df_relatorio['CNPJ'] = pd.to_numeric(df_relatorio['CNPJ'], downcast='integer')
        df_relatorio['Ean do produto'] = pd.to_numeric(df_relatorio['Ean do produto'], downcast='integer')
        df_relatorio['Ean do produto'] = df_relatorio['Ean do produto'].astype('int64')
        df_relatorio['Data do pedido'] = df_relatorio['Data do pedido'].astype('datetime64[ns]')
        df_relatorio['Data do pedido'] = df_relatorio['Data do pedido'].dt.strftime('%d/%m/%Y')
        df_relatorio = df_relatorio[df_relatorio['Status do pedido'].isin(['Processando','Aprovado','Parcialmente Entregue','Entregue','Faturado','Parcialmente Faturado','Enviado'])] #Faturado #Boleto Emitido #Estornado #Cancelado
        #df_relatorio = df_relatorio.loc[df_relatorio['Data do pedido'] > '2023-10-01 00:00:00']
        df_relatorio = df_relatorio.drop_duplicates()
        df_relatorio['CNPJ'] = df_relatorio['CNPJ'].astype('int64')
        #st.dataframe(df_relatorio)
        #df_relatorio.to_excel('output/df_relatorio.xlsx')
        #st.stop()

        df_escolas = escolas.copy()
        df_escolas = df_escolas.drop(columns=['TenantName'])
        df_escolas = df_escolas.drop_duplicates()
        
        df_escolas['CNPJ'] = df_escolas['CNPJ'].astype('int64')
        df_escolas = df_escolas[['CNPJ','TenantId','SchoolId','SchoolName']]
        df_escolas = df_escolas.dropna()
        df_escolas = df_escolas[~df_escolas['SchoolName'].str.contains('Concurso de Bolsa')]
        #st.dataframe(df_escolas)
    
        df_combos = combos.copy()
        df_combos = df_combos.rename(columns={'SKU':'Ean do produto','CÓDIGO DO COMBO':'ComboCode','PRODUTO':'LicenseName','Data do pedido':'OrderDate'})
    
        df_relatorio_combos = pd.merge(df_relatorio, df_combos, on=['Ean do produto'], how='inner')
        df_relatorio_combos = df_relatorio_combos.rename(columns={'LicenseName_x':'LicenseName'})
        df_relatorio_combos = df_relatorio_combos.drop_duplicates()
        df_relatorio_combos = df_relatorio_combos.rename(columns={'SÉRIE':'Grade'})
        #df_relatorio_combos.to_excel('output/df_relatorio_combos.xlsx')
        #st.dataframe(df_relatorio_combos)

        df_relatorio_combos_escolas = pd.merge(df_relatorio_combos, df_escolas,  on=['CNPJ'], how='left')
        df_relatorio_combos_escolas = df_relatorio_combos_escolas.drop_duplicates()
        #st.dataframe(df_relatorio_combos_escolas)
        #df_relatorio_combos_escolas.to_excel('output/df_relatorio_combos_escolas.xlsx')
        
        df = df_relatorio_combos_escolas.copy()
        
        df = df.assign(StartDate='01/01/2024',EndDate='31/12/2024',Coordinator='1',Manager='1', Operator='1',Teacher='1',Sponsor='1', Secretary='1',Reviewer='1',date = data_2, type = 'script')
        df = df.drop(columns=['Sku do produto'])
        df = df.rename(columns={'SchoolId':'School','TenantId':'Tenant', 'N pedido':'OrderNumber', 'Quantidade do produto':'Student', 'TAG REGULAR':'Grade','Data do pedido':'OrderDate', 'PRODUTO':'LicenseName' })
        
        #st.dataframe(df)
        #df.to_excel('output/df.xlsx')

        ###Premium###############################
        ##########################################

        df_premium = df.query('CNPJ == 56012628004078 or CNPJ == 56012628003349 or CNPJ == 56012628005716 or CNPJ == 56012628003187 or CNPJ == 7549613000121 or CNPJ == 7549613000202 or CNPJ == 7549613000474 or CNPJ == 30298376000276 or CNPJ == 30298376000195 or CNPJ == 23141033000238 or CNPJ == 56012628006011')
        #st.dataframe(df_premium)
        df_premium = df_premium[['Tenant','School','ComboCode','LicenseName','StartDate','EndDate','TAG BILINGUE','OrderNumber','OrderDate','Student','Coordinator','Manager','Operator','Teacher','Sponsor','Secretary','Reviewer','SchoolName','CNPJ','Ean do produto','date','type']]
        df_premium = df_premium.rename(columns={'TAG BILINGUE':'Grade'})
        df_premium[['OrderNumber','Coordinator','Manager','Operator','Teacher','Sponsor','Secretary','Reviewer']] = df_premium[['OrderNumber','Coordinator','Manager','Operator','Teacher','Sponsor','Secretary','Reviewer']]. astype('int64')
        df_premium = df_premium.sort_values('Student', ascending=False)
        df_premium['Student'] = 1     
        df_premium['Teacher'] = 1                  

        
        ###BILINGUE###############################
        ##########################################
        df_bilingue = df.loc[df['Nome do produto'].str.contains('HIGH FIVE')]
        #st.dataframe(df_bilingue)
        df_bilingue = df_bilingue[['Tenant','School','ComboCode','LicenseName','StartDate','EndDate','TAG BILINGUE','OrderNumber','OrderDate','Student','Coordinator','Manager','Operator','Teacher','Sponsor','Secretary','Reviewer','SchoolName','CNPJ','Ean do produto','date','type']]
        df_bilingue = df_bilingue.rename(columns={'TAG BILINGUE':'Grade'})
        df_bilingue[['OrderNumber','Coordinator','Manager','Operator','Teacher','Sponsor','Secretary','Reviewer']] = df_bilingue[['OrderNumber','Coordinator','Manager','Operator','Teacher','Sponsor','Secretary','Reviewer']]. astype('int64')
        df_bilingue = df_bilingue.sort_values('Student', ascending=False)
        df_bilingue['Student'] = 1
        df_bilingue['Teacher'] = 1
        #st.dataframe(df_bilingue)
        
        ###END BILINGUE###########################
        ##########################################


        df = df[['Tenant','School','ComboCode','LicenseName','StartDate','EndDate','Grade','OrderNumber','OrderDate','Student','Coordinator','Manager','Operator','Teacher','Sponsor','Secretary','Reviewer','SchoolName','CNPJ','Ean do produto','date','type']]
        df[['OrderNumber','Student','Coordinator','Manager','Operator','Teacher','Sponsor','Secretary','Reviewer']] = df[['OrderNumber','Student','Coordinator','Manager','Operator','Teacher','Sponsor','Secretary','Reviewer']]. astype('int64')
        df = df.sort_values('Student', ascending=False)

        df['Teacher'] = df['Student'].apply(lambda x: 1 if x < 21 else x//20)
     
        ### CONCAT ###############################
        ##########################################
        df_concat = pd.concat([df_bilingue,df_premium,df])
        df_concat = df_concat.sort_values(['School','ComboCode'])
        #df_concat.to_excel('output/df_concat.xlsx')
        #st.dataframe(df_concat)

        ###Groupby Somar Students####
        df_agrupado = df.groupby(['Tenant','School','ComboCode','LicenseName','StartDate','EndDate','Grade','OrderNumber','OrderDate','Coordinator','Manager','Operator','Teacher','Sponsor','Secretary','Reviewer','SchoolName','CNPJ','Ean do produto','date','type'])['Student'].sum().reset_index()
        df_concat = df_agrupado[['Tenant','School','ComboCode','LicenseName','StartDate','EndDate','Grade','OrderNumber','OrderDate','Student','Coordinator','Manager','Operator','Teacher','Sponsor','Secretary','Reviewer','SchoolName','CNPJ','Ean do produto','date','type']]
        st.dataframe(df_concat)

        
        st.divider()
        with st.spinner('Aguarde...'):
            time.sleep(3)
            st.success('Concluído com sucesso!', icon="😀")
            
            col1, col2= st.columns(2)
            with col1:
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_concat.to_excel(writer, index=False)
                    
                st.download_button(
                    label="Download",
                    data=output.getvalue(),
                    file_name=f'{today}-import.xlsx',
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",              
                )


          
        


       

        


     


