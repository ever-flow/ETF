import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.real_etf_recommender import RealETFRecommender
from utils.ui_helpers import display_metric_with_help, display_large_metric_row, display_correlation_with_help

st.set_page_config(
    page_title="포트폴리오 구성",
    page_icon="💼",
    layout="wide"
)

# 사이드바 - 전문적이고 간결한 디자인 (중복 제거)
with st.sidebar:
    # 브랜드 헤더
    st.markdown("""
    <div style="text-align: center; padding: 25px 0; border-bottom: 2px solid #e8ecf0; margin-bottom: 25px;">
        <h2 style="color: #1f2937; font-weight: 700; margin: 0; font-size: 22px; letter-spacing: -0.5px;">ETF 추천시스템</h2>
        <p style="color: #6b7280; font-size: 11px; margin: 8px 0 0 0; font-weight: 500;">AI-Powered Investment Solution</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 현재 단계 표시
    st.markdown("**현재 단계**")
    st.markdown("""
    <div style="background: #f8fafc; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
        <div style="font-size: 14px; color: #374151; font-weight: 600;">
            💼 포트폴리오 구성
        </div>
        <div style="font-size: 12px; color: #6b7280; margin-top: 5px;">
            최적 분산 투자 포트폴리오 제안
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 사용자 프로필 정보
    if 'user_profile' in st.session_state:
        st.markdown("**투자 프로필**")
        profile = st.session_state.user_profile
        
        risk_level = ["매우 보수적", "보수적", "중립적", "적극적", "매우 적극적"][profile['risk_tolerance']-1]
        horizon = ["단기", "중단기", "중기", "중장기", "장기"][profile['investment_horizon']-1]
        
        st.markdown(f"""
        <div style="background: #f8fafc; padding: 15px; border-radius: 8px;">
            <div style="font-size: 13px; color: #374151; margin-bottom: 8px;">
                <strong>위험 성향:</strong> {risk_level}
            </div>
            <div style="font-size: 13px; color: #374151;">
                <strong>투자 기간:</strong> {horizon}
            </div>
        </div>
        """, unsafe_allow_html=True)

st.title("포트폴리오 구성")

# 필수 데이터 확인
if 'recommendations' not in st.session_state:
    st.warning("먼저 ETF 추천을 받아주세요.")
    if st.button("ETF 추천 받기"):
        st.switch_page("pages/2_추천결과.py")
    st.stop()

recommendations = st.session_state.recommendations

# 추천 시스템 초기화
if 'recommender' not in st.session_state:
    st.session_state.recommender = RealETFRecommender()
    # 데이터 로딩
    with st.spinner("ETF 데이터를 로딩하는 중입니다..."):
        st.session_state.recommender.load_and_process_data(st.session_state.user_profile)

recommender = st.session_state.recommender

st.markdown("### 1단계: 핵심 ETF 선택")
st.markdown("추천받은 ETF 중에서 포트폴리오의 핵심이 될 ETF를 선택해주세요.")

# 핵심 ETF 선택
core_etf_options = [f"{row['Ticker']} - {row['Name']}" for _, row in recommendations.iterrows()]
selected_core = st.selectbox(
    "핵심 ETF 선택",
    core_etf_options,
    help="포트폴리오의 중심이 될 ETF를 선택하세요. 이 ETF와 낮은 상관관계를 가진 보완 ETF를 추천해드립니다."
)

if selected_core:
    # 선택된 ETF 정보 추출
    core_ticker = selected_core.split(' - ')[0]
    core_etf = recommendations[recommendations['Ticker'] == core_ticker].iloc[0]
    
    # 선택된 핵심 ETF 정보 표시
    st.markdown(f"**선택된 핵심 ETF**: {core_etf['Name']}")
    
    # 핵심 ETF 성과 지표
    core_metrics = [
        {
            "label": "1년 수익률",
            "value": f"{core_etf['Return_1Y']:.1f}%",
            "help": "최근 1년간의 투자 수익률입니다."
        },
        {
            "label": "변동성",
            "value": f"{core_etf['Volatility']:.1f}%",
            "help": "가격 변동의 정도를 나타냅니다."
        },
        {
            "label": "샤프 비율",
            "value": f"{core_etf['Sharpe_Ratio']:.2f}",
            "help": "위험 대비 수익률 지표입니다. 1.0 이상이면 우수합니다."
        },
        {
            "label": "최대 낙폭",
            "value": f"{core_etf['Max_Drawdown']:.1f}%",
            "help": "과거 최고점 대비 최대 하락폭입니다."
        }
    ]
    
    display_large_metric_row(core_metrics)
    
    st.markdown("---")
    st.markdown("### 2단계: 분산 투자를 위한 보완 ETF 추천")

    st.markdown("선택하신 핵심 ETF와 낮은 상관관계를 가지면서 샤프 지수가 높은 ETF들을 추천합니다.")

    # 보완 ETF 추천 로직
    try:
        # 전체 ETF 데이터에서 보완 ETF 찾기
        if hasattr(recommender, 'metrics_df') and recommender.metrics_df is not None and not recommender.metrics_df.empty:
            all_etfs_raw = recommender.metrics_df.copy()

            # 필요한 컬럼명 매핑
            all_etfs = pd.DataFrame()
            all_etfs['Ticker'] = all_etfs_raw.index
            # 간단한 ETF 이름 및 카테고리 매핑 (추후 개선 가능)
            all_etfs['Name'] = [f"ETF {ticker}" for ticker in all_etfs_raw.index]
            all_etfs['Category'] = ['기타' for _ in all_etfs_raw.index]
            all_etfs['Return_1Y'] = all_etfs_raw['Annual Return'] * 100
            all_etfs['Volatility'] = all_etfs_raw['Annual Volatility'] * 100
            all_etfs['Sharpe_Ratio'] = all_etfs_raw['Sharpe Ratio']
            all_etfs['Max_Drawdown'] = all_etfs_raw['Max Drawdown'] * 100

            # 핵심 ETF와의 실제 상관관계 계산
            returns_df = recommender.returns_df
            if core_ticker not in returns_df.columns:
                st.error("핵심 ETF 수익률 데이터를 찾을 수 없습니다.")
                st.stop()

            complement_candidates = all_etfs[all_etfs['Ticker'] != core_ticker].copy()
            complement_candidates['Correlation'] = complement_candidates['Ticker'].apply(
                lambda tk: returns_df[core_ticker].corr(returns_df[tk]) if tk in returns_df.columns else np.nan
            )
            complement_candidates.dropna(subset=['Correlation'], inplace=True)

            # 상관관계가 낮고 샤프지수가 높은 ETF 선별
            filtered_complements = complement_candidates[
                complement_candidates['Sharpe_Ratio'] > 0
            ]
            filtered_complements['CorrelationAbs'] = filtered_complements['Correlation'].abs()

            base_filtered = filtered_complements[filtered_complements['CorrelationAbs'] <= 0.5]
            if base_filtered.empty:
                st.warning("상관관계 0.5 이하이면서 샤프 지수가 양수인 보완 ETF를 찾을 수 없습니다. 조건을 완화합니다.")
                base_filtered = filtered_complements

            ranked_complements = base_filtered.sort_values(
                ['CorrelationAbs', 'Sharpe_Ratio'], ascending=[True, False]
            ).head(5)

            if not ranked_complements.empty:
                st.success(f"{len(ranked_complements)}개의 보완 ETF를 찾았습니다!")

                # 보완 ETF 목록 표시
                for i, (_, etf) in enumerate(ranked_complements.iterrows()):
                    with st.expander(f"보완 ETF #{i+1}: {etf['Name']}", expanded=i==0):

                        complement_metrics = [
                            {
                                "label": "1년 수익률",
                                "value": f"{etf['Return_1Y']:.1f}%",
                                "help": "최근 1년간의 투자 수익률입니다.",
                            },
                            {
                                "label": "변동성",
                                "value": f"{etf['Volatility']:.1f}%",
                                "help": "가격 변동의 정도를 나타냅니다.",
                            },
                            {
                                "label": "샤프 비율",
                                "value": f"{etf['Sharpe_Ratio']:.2f}",
                                "help": "위험 대비 수익률 지표입니다.",
                            }
                        ]

                        display_large_metric_row(complement_metrics)

                        # 상관관계 표시
                        display_correlation_with_help(
                            etf['Correlation'],
                            core_etf['Name'],
                            etf['Name']
                        )
                # 포트폴리오 구성 섹션
                st.markdown("---")
                st.markdown("### 3단계: 포트폴리오 비중 설정")
                
                # 선택할 보완 ETF
                complement_options = ["선택 안함"] + [f"{row['Ticker']} - {row['Name']}" for _, row in ranked_complements.iterrows()]
                selected_complement = st.selectbox(
                    "보완 ETF 선택",
                    complement_options,
                    help="핵심 ETF와 함께 포트폴리오를 구성할 보완 ETF를 선택하세요."
                )
                
                if selected_complement != "선택 안함":
                    # 비중 설정
                    core_weight = st.slider(
                        f"핵심 ETF ({core_etf['Name']}) 비중",
                        min_value=30,
                        max_value=90,
                        value=60,
                        step=5,
                        help="포트폴리오에서 핵심 ETF가 차지할 비중을 설정하세요."
                    )
                    
                    complement_weight = 100 - core_weight
                    
                    complement_ticker = selected_complement.split(' - ')[0]
                    complement_etf = ranked_complements[ranked_complements['Ticker'] == complement_ticker].iloc[0]
                    
                    st.markdown(f"**보완 ETF ({complement_etf['Name']}) 비중**: {complement_weight}%")
                    
                    # 포트폴리오 성과 예측
                    st.markdown("---")
                    st.markdown("### 포트폴리오 성과 예측")
                    
                    # 가중평균 계산
                    portfolio_return = (core_etf['Return_1Y'] * core_weight + complement_etf['Return_1Y'] * complement_weight) / 100
                    portfolio_volatility = np.sqrt(
                        (core_weight/100)**2 * (core_etf['Volatility']/100)**2 + 
                        (complement_weight/100)**2 * (complement_etf['Volatility']/100)**2 + 
                        2 * (core_weight/100) * (complement_weight/100) * (core_etf['Volatility']/100) * (complement_etf['Volatility']/100) * complement_etf['Correlation']
                    ) * 100
                    
                    portfolio_sharpe = portfolio_return / portfolio_volatility if portfolio_volatility > 0 else 0
                    
                    # 포트폴리오 성과 메트릭
                    portfolio_metrics = [
                        {
                            "label": "예상 연간 수익률",
                            "value": f"{portfolio_return:.1f}%",
                            "help": "포트폴리오의 예상 연간 수익률입니다."
                        },
                        {
                            "label": "예상 변동성",
                            "value": f"{portfolio_volatility:.1f}%",
                            "help": "포트폴리오의 예상 변동성입니다."
                        },
                        {
                            "label": "예상 샤프 비율",
                            "value": f"{portfolio_sharpe:.2f}",
                            "help": "포트폴리오의 위험 대비 수익률 지표입니다."
                        }
                    ]
                    
                    display_large_metric_row(portfolio_metrics)
                    
                    # 포트폴리오 구성 시각화
                    fig_pie = px.pie(
                        values=[core_weight, complement_weight],
                        names=[core_etf['Name'], complement_etf['Name']],
                        title="포트폴리오 구성 비중"
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                    
                    # 분산 효과 분석
                    st.markdown("---")
                    st.markdown("### 분산 투자 효과 분석")
                    
                    correlation_value = complement_etf['Correlation']
                    if abs(correlation_value) <= 0.1:
                        diversification_level = "매우 우수"
                        diversification_color = "success"
                    elif abs(correlation_value) <= 0.2:
                        diversification_level = "우수"
                        diversification_color = "success"
                    elif abs(correlation_value) <= 0.3:
                        diversification_level = "적당"
                        diversification_color = "info"
                    else:
                        diversification_level = "보통"
                        diversification_color = "warning"
                    
                    if diversification_color == "success":
                        st.success(f"분산 투자 효과: {diversification_level} (상관관계: {correlation_value:.2f})")
                    elif diversification_color == "info":
                        st.info(f"분산 투자 효과: {diversification_level} (상관관계: {correlation_value:.2f})")
                    else:
                        st.warning(f"분산 투자 효과: {diversification_level} (상관관계: {correlation_value:.2f})")
                    
                    # 백테스팅 시뮬레이션
                    st.markdown("---")
                    st.markdown("### 백테스팅 시뮬레이션")
                    
                    # 간단한 백테스팅 (2년간 일일 수익률 시뮬레이션)
                    np.random.seed(42)
                    days = 500
                    
                    # 일일 수익률 시뮬레이션
                    core_daily_returns = np.random.normal(
                        core_etf['Return_1Y']/365/100, 
                        core_etf['Volatility']/np.sqrt(365)/100, 
                        days
                    )
                    
                    complement_daily_returns = np.random.normal(
                        complement_etf['Return_1Y']/365/100, 
                        complement_etf['Volatility']/np.sqrt(365)/100, 
                        days
                    )
                    
                    # 포트폴리오 일일 수익률
                    portfolio_daily_returns = (
                        core_daily_returns * core_weight/100 + 
                        complement_daily_returns * complement_weight/100
                    )
                    
                    # 누적 수익률 계산
                    portfolio_cumulative = np.cumprod(1 + portfolio_daily_returns)
                    core_cumulative = np.cumprod(1 + core_daily_returns)
                    complement_cumulative = np.cumprod(1 + complement_daily_returns)
                    
                    # 백테스팅 결과 표시
                    total_return = (portfolio_cumulative[-1] - 1) * 100
                    annual_volatility = np.std(portfolio_daily_returns) * np.sqrt(365) * 100
                    
                    # pandas Series로 변환하여 cummax 사용
                    portfolio_series = pd.Series(portfolio_cumulative)
                    max_dd = ((portfolio_series / portfolio_series.cummax()) - 1).min() * 100
                    
                    backtest_metrics = [
                        {
                            "label": "총 수익률",
                            "value": f"{total_return:.1f}%",
                            "help": "시뮬레이션 기간 동안의 총 수익률입니다."
                        },
                        {
                            "label": "연간 변동성",
                            "value": f"{annual_volatility:.1f}%",
                            "help": "연간 기준 변동성입니다."
                        },
                        {
                            "label": "최대 낙폭",
                            "value": f"{max_dd:.1f}%",
                            "help": "시뮬레이션 기간 중 최대 하락폭입니다."
                        }
                    ]
                    
                    display_large_metric_row(backtest_metrics)
                    
                    # 누적 수익률 차트
                    dates = pd.date_range(start='2022-01-01', periods=days, freq='D')
                    
                    fig_backtest = go.Figure()
                    
                    fig_backtest.add_trace(go.Scatter(
                        x=dates,
                        y=(portfolio_cumulative - 1) * 100,
                        mode='lines',
                        name='포트폴리오',
                        line=dict(color='blue', width=3)
                    ))
                    
                    fig_backtest.add_trace(go.Scatter(
                        x=dates,
                        y=(core_cumulative - 1) * 100,
                        mode='lines',
                        name=core_etf['Name'],
                        line=dict(color='red', width=2)
                    ))
                    
                    fig_backtest.add_trace(go.Scatter(
                        x=dates,
                        y=(complement_cumulative - 1) * 100,
                        mode='lines',
                        name=complement_etf['Name'],
                        line=dict(color='green', width=2)
                    ))
                    
                    fig_backtest.update_layout(
                        title="백테스팅 시뮬레이션 결과",
                        xaxis_title="날짜",
                        yaxis_title="누적 수익률 (%)",
                        height=500
                    )
                    
                    st.plotly_chart(fig_backtest, use_container_width=True)
                    
                    st.info("""
                    **백테스팅 시뮬레이션 결과**
                    
                    이 시뮬레이션은 과거 데이터를 기반으로 한 가상의 성과입니다. 
                    실제 투자 성과는 다를 수 있으며, 과거 성과가 미래 수익을 보장하지 않습니다.
                    """)
            
            else:
                st.error("조건에 맞는 보완 ETF를 찾을 수 없습니다.")
        
        else:
            st.error("추천 데이터를 불러올 수 없습니다. 먼저 ETF 추천을 받아주세요.")
            if st.button("ETF 추천 받기", key="get_recommendations"):
                st.switch_page("pages/2_추천결과.py")
    
    except Exception as e:
        st.error(f"보완 ETF 추천 중 오류가 발생했습니다: {str(e)}")

# 투자 주의사항
st.markdown("---")
st.warning("""
**투자 주의사항**
- 이 포트폴리오 구성은 과거 데이터를 기반으로 한 분석 결과입니다.
- 실제 시장에서는 예상과 다른 결과가 나올 수 있습니다.
- 투자 전에 반드시 전문가와 상담하시기 바랍니다.
- 모든 투자에는 원금 손실의 위험이 있습니다.
""")

