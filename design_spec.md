# ETF 추천 시스템 Streamlit 앱 설계

## 앱 구조 설계

### 메인 앱 파일: app.py
- Streamlit 멀티페이지 구조 사용
- 사이드바 네비게이션
- 세션 상태 관리

### 페이지 구성
1. **🏠 홈페이지** (`pages/1_홈.py`)
   - 서비스 소개
   - 사용법 안내
   - 시작하기 버튼

2. **📋 투자 성향 설문** (`pages/2_투자성향설문.py`)
   - 7가지 질문을 단계별 진행
   - 진행률 표시
   - 결과 저장

3. **🎯 ETF 추천 결과** (`pages/3_추천결과.py`)
   - Top-7 ETF 추천
   - 핵심 정보 카드 형태 표시
   - 추천 이유 설명

4. **📊 상세 분석** (`pages/4_상세분석.py`)
   - 성과 차트 (Plotly 인터랙티브)
   - 위험 지표 비교
   - 시장 대비 성과

5. **💼 포트폴리오 시뮬레이션** (`pages/5_포트폴리오.py`)
   - 선택한 ETF로 포트폴리오 구성
   - 백테스팅 결과
   - 리밸런싱 시뮬레이션

### 유틸리티 모듈
- `utils/etf_recommender.py`: 기존 추천 로직 모듈화
- `utils/data_loader.py`: 데이터 로딩 및 캐싱
- `utils/visualizations.py`: 차트 생성 함수들
- `utils/ui_components.py`: 재사용 가능한 UI 컴포넌트

### 데이터 파일
- `data/user_etf_preferences.xlsx`: 사용자 선호도 데이터
- `data/etf_info.json`: ETF 기본 정보 (이름, 카테고리 등)

## UI/UX 디자인 원칙

### 색상 테마
- 주색상: 파란색 계열 (신뢰감)
- 위험도 표시: 빨강(고위험) → 노랑(중위험) → 초록(저위험)
- 수익률: 빨강(손실) → 회색(무변화) → 초록(수익)

### 레이아웃
- 사이드바: 네비게이션 + 진행 상태
- 메인 영역: 3컬럼 레이아웃 활용
- 카드 형태의 정보 표시
- 반응형 디자인

### 사용자 경험
- 단계별 안내 메시지
- 툴팁으로 용어 설명
- 로딩 상태 표시
- 에러 처리 및 안내

## 기술 스택
- **Frontend**: Streamlit
- **Data**: pandas, numpy
- **Visualization**: plotly, altair
- **ML**: scikit-learn, umap-learn
- **Finance**: FinanceDataReader
- **Styling**: Custom CSS

