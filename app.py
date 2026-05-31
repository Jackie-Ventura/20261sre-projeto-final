import streamlit as st
import pandas as pd
import clickhouse_connect
import os
from dotenv import load_dotenv
import plotly.express as px

load_dotenv()

st.set_page_config(page_title="Northwind Sales Dashboard", layout="wide")

def get_client():
    return clickhouse_connect.get_client(
        host=os.getenv("CLICKHOUSE_HOST"),
        port=int(os.getenv("CLICKHOUSE_PORT")),
        username=os.getenv("CLICKHOUSE_USER"),
        password=os.getenv("CLICKHOUSE_PASSWORD"),
        database=os.getenv("CLICKHOUSE_DB")
    )

st.title("📊 Northwind Strategic Dashboard")
st.markdown("KPIs de Vendas baseados na arquitetura Medallion (Bronze -> Silver -> Gold)")

try:
    client = get_client()
    
    # Query Gold Layer
    df = client.query_df("SELECT * FROM fct_sales")
    df['order_date'] = pd.to_datetime(df['order_date'])
    df['month'] = df['order_date'].dt.to_period('M').astype(str)

    # 1. KPIs superiores (baseados em pedidos únicos)
    unique_orders = df.drop_duplicates('order_id')
    total_sales = df['line_total_price'].sum()
    total_orders = unique_orders['order_id'].nunique()
    avg_order_value = total_sales / total_orders if total_orders > 0 else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Faturamento Total", f"$ {total_sales:,.2f}")
    col2.metric("Total de Pedidos", f"{total_orders}")
    col3.metric("Ticket Médio", f"$ {avg_order_value:,.2f}")

    st.divider()

    # 2. Pergunta Específica: Top 10 Produtos com maior receita líquida
    st.header("🎯 Análise de Performance de Produtos")
    
    # Agregação por Produto
    product_revenue = df.groupby('product_id')['line_total_price'].sum().reset_index()
    product_revenue = product_revenue.sort_values('line_total_price', ascending=False).head(10)
    
    # Agregação Mensal para os Top 10
    top_10_ids = product_revenue['product_id'].tolist()
    df_top_10 = df[df['product_id'].isin(top_10_ids)]
    monthly_top_10 = df_top_10.groupby(['month', 'product_id'])['line_total_price'].sum().reset_index()
    monthly_top_10 = monthly_top_10.sort_values(['month', 'product_id'])

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Top 10 Produtos (Ranking de Receita)")
        
        # Formatação para a tabela
        display_df = product_revenue.copy()
        display_df.columns = ["ID do Produto", "Receita Líquida"]
        
        # Aplicando estilo gradiente (Vermelho para Verde)
        st.dataframe(
            display_df.style.background_gradient(cmap='RdYlGn', subset=['Receita Líquida'])
            .format({"Receita Líquida": "$ {:,.2f}"}),
            use_container_width=True,
            hide_index=True
        )

    with c2:
        st.subheader("Evolução Mensal (Top 10)")
        fig_line_top = px.line(
            monthly_top_10, 
            x='month', 
            y='line_total_price', 
            color='product_id',
            labels={'month': 'Mês', 'line_total_price': 'Receita Líquida', 'product_id': 'Produto'},
            markers=True
        )
        st.plotly_chart(fig_line_top, use_container_width=True)

    st.divider()

    # 3. Visões Gerais Originais
    c3, c4 = st.columns(2)

    with c3:
        st.subheader("Vendas por País")
        country_sales = df.groupby('ship_country')['line_total_price'].sum().reset_index()
        fig_country = px.pie(country_sales, values='line_total_price', names='ship_country', hole=.3)
        st.plotly_chart(fig_country, use_container_width=True)

    with c4:
        st.subheader("Evolução de Vendas Global (Mensal)")
        monthly_sales = df.groupby('month')['line_total_price'].sum().reset_index()
        fig_trend = px.line(monthly_sales, x='month', y='line_total_price', markers=True)
        st.plotly_chart(fig_trend, use_container_width=True)

    st.subheader("Detalhes dos Pedidos (Amostra)")
    st.dataframe(df.sort_values('order_date', ascending=False).head(100), use_container_width=True)

except Exception as e:
    st.error(f"Erro ao conectar ou buscar dados: {e}")
    st.info("Certifique-se de que o dbt run foi executado com sucesso.")
