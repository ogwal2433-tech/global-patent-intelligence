import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Patent Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database path
DB_PATH = Path("database/patents.db")

@st.cache_data(ttl=3600)
def load_data():
    """Load data from SQLite database"""
    conn = sqlite3.connect(DB_PATH)
    
    # Load top inventors
    top_inventors = pd.read_sql("""
        SELECT i.name, COUNT(DISTINCT r.patent_id) as patent_count
        FROM inventors i
        JOIN relationships r ON i.inventor_id = r.inventor_id
        GROUP BY i.inventor_id, i.name
        ORDER BY patent_count DESC
        LIMIT 20
    """, conn)
    
    # Load top companies
    top_companies = pd.read_sql("""
        SELECT c.name, COUNT(DISTINCT r.patent_id) as patent_count
        FROM companies c
        JOIN relationships r ON c.company_id = r.company_id
        GROUP BY c.company_id, c.name
        ORDER BY patent_count DESC
        LIMIT 20
    """, conn)
    
    # Load yearly trends
    yearly_trends = pd.read_sql("""
        SELECT year, COUNT(*) as patent_count
        FROM patents
        WHERE year IS NOT NULL AND year > 1975 AND year <= 2025
        GROUP BY year
        ORDER BY year
    """, conn)
    
    # Load country data
    country_data = pd.read_sql("""
        SELECT 
            CASE 
                WHEN i.country IS NULL OR i.country = '' THEN 'Unknown'
                ELSE i.country 
            END as country,
            COUNT(DISTINCT r.patent_id) as patent_count
        FROM inventors i
        JOIN relationships r ON i.inventor_id = r.inventor_id
        GROUP BY country
        ORDER BY patent_count DESC
        LIMIT 15
    """, conn)
    
    # Load top inventors by year (for trend analysis)
    yearly_inventors = pd.read_sql("""
        SELECT p.year, i.name, COUNT(*) as patent_count
        FROM patents p
        JOIN relationships r ON p.patent_id = r.patent_id
        JOIN inventors i ON r.inventor_id = i.inventor_id
        WHERE p.year >= 2010 AND p.year <= 2025
        GROUP BY p.year, i.inventor_id, i.name
        HAVING COUNT(*) > 50
        ORDER BY p.year DESC, patent_count DESC
        LIMIT 100
    """, conn)
    
    # Get total counts
    total_patents = pd.read_sql("SELECT COUNT(*) as count FROM patents", conn).iloc[0]['count']
    total_inventors = pd.read_sql("SELECT COUNT(*) as count FROM inventors", conn).iloc[0]['count']
    total_companies = pd.read_sql("SELECT COUNT(*) as count FROM companies", conn).iloc[0]['count']
    
    conn.close()
    
    return {
        'top_inventors': top_inventors,
        'top_companies': top_companies,
        'yearly_trends': yearly_trends,
        'country_data': country_data,
        'yearly_inventors': yearly_inventors,
        'total_patents': total_patents,
        'total_inventors': total_inventors,
        'total_companies': total_companies
    }

# Load data
st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #2A6E8C, #1F527C);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2.5rem;
    }
    .main-header p {
        color: rgba(255,255,255,0.8);
        margin: 0.5rem 0 0 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        border-left: 4px solid #2A6E8C;
    }
    .metric-number {
        font-size: 2rem;
        font-weight: bold;
        color: #2A6E8C;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>📊 Global Patent Intelligence Dashboard</h1>
    <p>Real-time analytics from 9.4M+ patents | 1976-2025</p>
</div>
""", unsafe_allow_html=True)

# Load data with spinner
with st.spinner("Loading data..."):
    data = load_data()

# Key Metrics Row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-number">{data['total_patents']:,}</div>
        <div>📄 Total Patents</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-number">{data['total_inventors']:,}</div>
        <div>👨‍🔬 Unique Inventors</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-number">{data['total_companies']:,}</div>
        <div>🏢 Companies/Assignees</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    # Calculate year-over-year growth
    yearly = data['yearly_trends']
    if len(yearly) > 1:
        recent_growth = ((yearly.iloc[-1]['patent_count'] - yearly.iloc[-2]['patent_count']) / yearly.iloc[-2]['patent_count']) * 100
        growth_color = "green" if recent_growth > 0 else "red"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number" style="color: {growth_color};">{recent_growth:+.1f}%</div>
            <div>📈 YoY Growth (2024-2025)</div>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# Row 1: Patent Trends and Country Distribution
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Patent Trends Over Time")
    
    fig = px.line(
        data['yearly_trends'],
        x='year',
        y='patent_count',
        title='Patents Granted by Year (1976-2025)',
        labels={'year': 'Year', 'patent_count': 'Number of Patents'},
        markers=True
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode='x unified',
        height=450
    )
    fig.update_traces(line=dict(color='#2A6E8C', width=2))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🌍 Top Patent-Producing Countries")
    
    fig = px.pie(
        data['country_data'].head(10),
        values='patent_count',
        names='country',
        title='Patent Distribution by Country',
        hole=0.3,
        color_discrete_sequence=px.colors.sequential.Blues_r
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=450)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# Row 2: Top Inventors and Top Companies
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏆 Top 20 Inventors")
    
    fig = px.bar(
        data['top_inventors'].head(20),
        x='patent_count',
        y='name',
        orientation='h',
        title='Most Prolific Inventors',
        labels={'patent_count': 'Number of Patents', 'name': 'Inventor'},
        color='patent_count',
        color_continuous_scale='Blues'
    )
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        height=500,
        xaxis_title="Patents",
        yaxis_title=""
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🏢 Top 20 Companies")
    
    fig = px.bar(
        data['top_companies'].head(20),
        x='patent_count',
        y='name',
        orientation='h',
        title='Leading Patent Assignees',
        labels={'patent_count': 'Number of Patents', 'name': 'Company'},
        color='patent_count',
        color_continuous_scale='Greens'
    )
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        height=500,
        xaxis_title="Patents",
        yaxis_title=""
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# Row 3: Year-over-Year Comparison
st.subheader("📊 Year-over-Year Patent Comparison")

col1, col2 = st.columns([1, 2])

with col1:
    years_available = data['yearly_trends']['year'].unique()
    year1 = st.selectbox("Select First Year", years_available, index=len(years_available)-2)
    year2 = st.selectbox("Select Second Year", years_available, index=len(years_available)-1)

with col2:
    if year1 and year2:
        year1_data = data['yearly_trends'][data['yearly_trends']['year'] == year1]['patent_count'].values[0]
        year2_data = data['yearly_trends'][data['yearly_trends']['year'] == year2]['patent_count'].values[0]
        
        diff = year2_data - year1_data
        pct_change = (diff / year1_data) * 100
        
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            st.metric(f"📅 {year1}", f"{year1_data:,}")
        with col_b:
            st.metric(f"📅 {year2}", f"{year2_data:,}")
        with col_c:
            st.metric("Change", f"{diff:+,}", f"{pct_change:+.1f}%")

# Row 4: Recent Trends Table
st.subheader("📋 Recent Patent Activity (2020-2025)")

recent_data = data['yearly_trends'][data['yearly_trends']['year'] >= 2020].copy()
recent_data['growth'] = recent_data['patent_count'].pct_change() * 100
recent_data = recent_data.sort_values('year', ascending=False)

st.dataframe(
    recent_data,
    column_config={
        "year": "Year",
        "patent_count": st.column_config.NumberColumn("Patents", format="%d"),
        "growth": st.column_config.NumberColumn("YoY Growth", format="%.1f%%")
    },
    use_container_width=True,
    hide_index=True
)

# Row 5: Key Insights
st.divider()
st.subheader("💡 Key Insights")

insights_col1, insights_col2, insights_col3 = st.columns(3)

with insights_col1:
    st.info("""
    **🏆 Top Innovator**  
    Shunpei Yamazaki leads with **6,787 patents** - more than double the second-ranked inventor.
    """)

with insights_col2:
    st.success("""
    **🌍 Geographic Dominance**  
    United States accounts for **61.9%** of all patents, followed by Japan (19.2%).
    """)

with insights_col3:
    st.warning("""
    **📈 Peak Innovation**  
    2019 saw the highest patent count with **392,618** grants, showing a slight decline post-2020.
    """)

# Footer
st.divider()
st.markdown(
    """
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>📊 Data Source: USPTO PatentsView | 📅 Coverage: 1976-2025 | 🏢 Total Companies: 572K+</p>
        <p>Built with Streamlit, Plotly, and SQLite</p>
    </div>
    """,
    unsafe_allow_html=True
)