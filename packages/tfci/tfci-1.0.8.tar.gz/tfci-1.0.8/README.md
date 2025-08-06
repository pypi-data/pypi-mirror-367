# TFCI (Time Forecasting CI)

간단한 시계열 예측 라이브러리

## 로컬 설치
```bash
git clone https://github.com/ci671233/tfci.git
python tfci.py
```

### 기본 라이브러리 (tfci)
```bash
pip install tfci
```

### MCP 확장 패키지 (tfci-mcp)
```bash
pip install tfci-mcp
```

## 사용법

### 기본 라이브러리 사용
```python
from tfci import predict

# YAML 설정 파일로 예측 실행
predict("config.yaml")
```

### MCP 패키지 사용
```python
from tfci_mcp import TFCIMCPClient

# MCP 클라이언트로 예측 실행
client = TFCIMCPClient()
client.start_server()
result = client.predict("config.yaml")
client.stop_server()
```

### 다른 MCP들과 함께 사용
```python
from tfci_mcp import TFCIMCPClient
from viz_mcp import VizMCPClient

# 예측 → 시각화 파이프라인
tfci_client = TFCIMCPClient()
tfci_client.start_server()
result = tfci_client.predict("config.yaml")

viz_client = VizMCPClient()
chart = viz_client.create_chart(result)

tfci_client.stop_server()
```

## 기능

### tfci 라이브러리
- ✅ 시계열 예측 (Prophet 기반)
- ✅ YAML 설정 파일 지원
- ✅ DB2 데이터베이스 연동
- ✅ group_key 리스트 지원
- ✅ 멀티프로세싱 지원

### tfci-mcp 패키지
- ✅ MCP (Model Context Protocol) 지원
- ✅ 다른 MCP들과 조합 가능
- ✅ JSON-RPC 통신
- ✅ 서버/클라이언트 분리

## 설정 파일 예시

```yaml
input:
  source_type: "db" # or csv
  db_type: "db2"
  connection:
    host: "DBURL"
    port: PortNumber
    user: "UserName"
    password: "Pwd!"
    database: "DBName"
  table: "TableName"
  features: ["COL_1", "COL_2", "COL_3"]
  target: ["COL_4"]
prediction:
  task_type: "timeseries"
  future_steps: 5 # 예측 구간 (5년 후)
  time_col: "COL_1"
  group_key: ["COL_2", "COL_3"]
output:
  source_type: "db" # or csv
  db_type: "db2"
  connection:
    host: "DBURL"
    port: PortNumber
    user: "UserName"
    password: "Pwd!"
    database: "DBName"
  table: "TableName"
```

## 프로젝트 구조

```
tfci/
├── tfci/              # 메인 라이브러리
│   └── __init__.py
│   └── pyproject.toml
├── tfci_mcp/          # MCP 패키지
│   ├── __init__.py
│   ├── client.py
│   └── pyproject.toml
├── mcp/               # MCP 서버/클라이언트
│   ├── mcp_server.py
│   └── client.py
├── config/            # 설정 관리
├── core/              # 핵심 로직
├── data/              # 데이터 처리
└── model/             # 모델 관련
```

## 의존성

### tfci
- pandas>=2.0.0
- numpy>=1.20.0
- prophet>=1.1.0
- scikit-learn>=1.0.0
- tqdm>=4.60.0
- PyYAML>=6.0
- requests>=2.25.0

### tfci-mcp
- tfci>=1.0.5

## 라이선스

MIT License
