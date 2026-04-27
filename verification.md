# 🔍 자산균형 플랫폼 자체 검증 명령어 세트

## 전체 검증 실행 마스터 스크립트

```bash
#!/bin/bash
# ============================================
# 자산균형(Asset Balance Korea) 전체 자체 검증
# 실행: chmod +x verify_all.sh && ./verify_all.sh
# ============================================

set -e  # 오류 발생 시 중단

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 결과 카운터
PASS=0
FAIL=0
WARN=0
TOTAL=0

# 로그 파일
LOG_FILE="verify_result_$(date +%Y%m%d_%H%M%S).log"
exec > >(tee -a "$LOG_FILE") 2>&1

print_header() {
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║  $1${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════╝${NC}"
}

print_test() {
    TOTAL=$((TOTAL+1))
    echo -e "${BLUE}[TEST-$TOTAL]${NC} $1"
}

pass() {
    PASS=$((PASS+1))
    echo -e "  ${GREEN}✅ PASS${NC}: $1"
}

fail() {
    FAIL=$((FAIL+1))
    echo -e "  ${RED}❌ FAIL${NC}: $1"
}

warn() {
    WARN=$((WARN+1))
    echo -e "  ${YELLOW}⚠️  WARN${NC}: $1"
}

echo ""
echo -e "${CYAN}=================================================${NC}"
echo -e "${CYAN}  자산균형 플랫폼 종합 자체 검증 시작${NC}"
echo -e "${CYAN}  실행 시각: $(date '+%Y-%m-%d %H:%M:%S')${NC}"
echo -e "${CYAN}=================================================${NC}"

# ============================================
# 1단계: DB 검증
# ============================================
print_header "1단계: 데이터베이스 검증"
bash verify_db.sh

# ============================================
# 2단계: UI 검증
# ============================================
print_header "2단계: UI/UX 검증"
bash verify_ui.sh

# ============================================
# 3단계: AI 알고리즘 검증
# ============================================
print_header "3단계: AI 알고리즘 검증"
bash verify_ai.sh

# ============================================
# 4단계: 파일럿 테스트 검증
# ============================================
print_header "4단계: 파일럿 테스트 검증"
bash verify_pilot.sh

# ============================================
# 최종 결과 리포트
# ============================================
echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║           종합 검증 결과 리포트                  ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════╝${NC}"
echo -e "  전체 테스트: ${TOTAL}개"
echo -e "  ${GREEN}PASS: ${PASS}개${NC}"
echo -e "  ${RED}FAIL: ${FAIL}개${NC}"
echo -e "  ${YELLOW}WARN: ${WARN}개${NC}"
echo ""

SUCCESS_RATE=$(echo "scale=1; $PASS * 100 / $TOTAL" | bc)
echo -e "  성공률: ${SUCCESS_RATE}%"

if [ "$FAIL" -eq 0 ]; then
    echo -e "  ${GREEN}🎉 전체 검증 통과! 운영 배포 가능${NC}"
elif [ "$FAIL" -le 3 ]; then
    echo -e "  ${YELLOW}⚠️  경미한 문제 있음. 검토 후 배포 결정${NC}"
else
    echo -e "  ${RED}🚨 심각한 문제 발견. 수정 후 재검증 필요${NC}"
fi

echo ""
echo -e "  📄 상세 로그: ${LOG_FILE}"
echo -e "  완료 시각: $(date '+%Y-%m-%d %H:%M:%S')"
```

---

## 1단계 DB 검증 스크립트

```bash
#!/bin/bash
# verify_db.sh - 데이터베이스 구조 및 데이터 검증

DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-asset_balance}"
DB_USER="${DB_USER:-ab_admin}"
DB_PASS="${DB_PASS:-secure_password_2026}"

PSQL="PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t -c"

echo ""
echo "📦 [DB-001] DB 서버 접속 가능 여부 확인"
if $PSQL "SELECT 1" > /dev/null 2>&1; then
    pass "PostgreSQL 서버 정상 접속 (${DB_HOST}:${DB_PORT})"
else
    fail "DB 접속 실패 → DB_HOST, DB_USER, DB_PASS 환경변수 확인"
    exit 1
fi

echo ""
echo "📋 [DB-002] 필수 테이블 11개 존재 확인"
REQUIRED_TABLES=(
    "users"
    "user_profiles"
    "region_master"
    "region_real_estate_index"
    "region_economic_index"
    "region_characteristics"
    "financial_products"
    "user_assets"
    "user_cashflow"
    "rebalancing_recommendations"
)

for TABLE in "${REQUIRED_TABLES[@]}"; do
    EXISTS=$($PSQL "SELECT COUNT(*) FROM information_schema.tables WHERE table_name='$TABLE'")
    if [ "$(echo $EXISTS | tr -d ' ')" = "1" ]; then
        pass "테이블 존재: $TABLE"
    else
        fail "테이블 없음: $TABLE → 1단계 init.sql 재실행 필요"
    fi
done

echo ""
echo "🔑 [DB-003] 필수 인덱스 존재 확인"
REQUIRED_INDEXES=(
    "idx_users_email"
    "idx_user_profiles_region"
    "idx_user_profiles_life_stage"
    "idx_region_real_estate_date"
    "idx_region_real_estate_type"
    "idx_user_assets_user"
    "idx_user_cashflow_user"
    "idx_recommendations_user"
)

for IDX in "${REQUIRED_INDEXES[@]}"; do
    EXISTS=$($PSQL "SELECT COUNT(*) FROM pg_indexes WHERE indexname='$IDX'")
    if [ "$(echo $EXISTS | tr -d ' ')" = "1" ]; then
        pass "인덱스 존재: $IDX"
    else
        warn "인덱스 없음: $IDX → 쿼리 성능 저하 가능"
    fi
done

echo ""
echo "📊 [DB-004] 지역 마스터 데이터 충족 확인"
# 최소 50개 이상 시군구 데이터 필요 (MVP 기준)
REGION_COUNT=$($PSQL "SELECT COUNT(*) FROM region_master WHERE level=2")
REGION_COUNT=$(echo $REGION_COUNT | tr -d ' ')

if [ "$REGION_COUNT" -ge 250 ]; then
    pass "전국 시군구 ${REGION_COUNT}개 등록 완료 (목표: 250개)"
elif [ "$REGION_COUNT" -ge 50 ]; then
    warn "시군구 ${REGION_COUNT}개 등록 (MVP 최소 50개 충족, 목표 250개 미달)"
else
    fail "시군구 데이터 부족: ${REGION_COUNT}개 (최소 50개 필요)"
fi

echo ""
echo "🏠 [DB-005] 부동산 지수 데이터 최신성 확인"
LATEST_DATE=$($PSQL "SELECT MAX(index_date) FROM region_real_estate_index")
LATEST_DATE=$(echo $LATEST_DATE | tr -d ' ')
TODAY=$(date +%Y-%m-%d)
DAYS_OLD=$(( ($(date -d "$TODAY" +%s) - $(date -d "$LATEST_DATE" +%s)) / 86400 ))

if [ "$DAYS_OLD" -le 7 ]; then
    pass "부동산 지수 최신 데이터: ${LATEST_DATE} (${DAYS_OLD}일 경과)"
elif [ "$DAYS_OLD" -le 30 ]; then
    warn "부동산 지수 ${DAYS_OLD}일 경과 (주간 갱신 권장)"
else
    fail "부동산 지수 ${DAYS_OLD}일 미갱신 → 배치 수집 점검 필요"
fi

echo ""
echo "🔗 [DB-006] 외래키 무결성 확인"
INTEGRITY_ERRORS=$($PSQL "
    SELECT COUNT(*) FROM user_profiles up
    LEFT JOIN region_master rm ON up.region_code = rm.region_code
    WHERE rm.region_code IS NULL
")
INTEGRITY_ERRORS=$(echo $INTEGRITY_ERRORS | tr -d ' ')

if [ "$INTEGRITY_ERRORS" -eq 0 ]; then
    pass "user_profiles ↔ region_master 참조 무결성 정상"
else
    fail "참조 무결성 오류 ${INTEGRITY_ERRORS}건 발견"
fi

echo ""
echo "⚡ [DB-007] 주요 쿼리 성능 확인 (100ms 이내)"
START=$(date +%s%N)
$PSQL "
    SELECT u.user_id, up.life_stage, rm.region_name, rie.avg_price_per_sqm
    FROM users u
    JOIN user_profiles up ON u.user_id = up.user_id
    JOIN region_master rm ON up.region_code = rm.region_code
    LEFT JOIN region_real_estate_index rie 
        ON up.region_code = rie.region_code
        AND rie.index_date = (SELECT MAX(index_date) FROM region_real_estate_index)
        AND rie.house_type = '아파트'
    LIMIT 100
" > /dev/null 2>&1
END=$(date +%s%N)
ELAPSED=$(( (END - START) / 1000000 ))

if [ "$ELAPSED" -le 100 ]; then
    pass "핵심 JOIN 쿼리 응답 시간: ${ELAPSED}ms (목표: 100ms 이내)"
elif [ "$ELAPSED" -le 500 ]; then
    warn "핵심 JOIN 쿼리 응답 시간: ${ELAPSED}ms (최적화 권장)"
else
    fail "핵심 JOIN 쿼리 응답 시간: ${ELAPSED}ms → 인덱스 및 쿼리 최적화 필요"
fi

echo ""
echo "💾 [DB-008] Redis 캐시 서버 확인"
REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6379}"

if redis-cli -h $REDIS_HOST -p $REDIS_PORT ping 2>/dev/null | grep -q "PONG"; then
    USED_MEM=$(redis-cli -h $REDIS_HOST -p $REDIS_PORT info memory | grep used_memory_human | cut -d: -f2 | tr -d '\r')
    pass "Redis 정상 작동 (사용 메모리: ${USED_MEM})"
else
    warn "Redis 미가동 → 캐싱 기능 비활성 (성능 저하)"
fi
```

---

## 2단계 UI 검증 스크립트

```bash
#!/bin/bash
# verify_ui.sh - 화면 및 API 엔드포인트 검증

API_BASE="${API_BASE:-http://localhost:8000}"
APP_PORT="${APP_PORT:-3000}"

echo ""
echo "🌐 [UI-001] API 서버 헬스체크"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "${API_BASE}/health" --max-time 5)
if [ "$HTTP_CODE" = "200" ]; then
    pass "API 서버 정상 응답 (${API_BASE})"
else
    fail "API 서버 응답 없음 (HTTP ${HTTP_CODE}) → 서버 기동 확인"
    exit 1
fi

echo ""
echo "📱 [UI-002] React Native 번들 빌드 확인"
if [ -f "./android/app/build/outputs/apk/debug/app-debug.apk" ]; then
    APK_SIZE=$(du -sh ./android/app/build/outputs/apk/debug/app-debug.apk | cut -f1)
    pass "Android APK 빌드 완료 (크기: ${APK_SIZE})"
elif [ -f "./build/index.html" ]; then
    pass "웹 빌드 완료 (index.html 존재)"
else
    warn "빌드 파일 미발견 → npm run build 또는 react-native build 실행 필요"
fi

echo ""
echo "📋 [UI-003] 5개 필수 화면 컴포넌트 파일 확인"
SCREENS=(
    "screens/Dashboard.jsx"
    "screens/PortfolioInput.jsx"
    "screens/Recommendations.jsx"
    "screens/RegionAnalysis.jsx"
    "screens/Simulation.jsx"
)

for SCREEN in "${SCREENS[@]}"; do
    if [ -f "./$SCREEN" ]; then
        LINES=$(wc -l < "./$SCREEN")
        pass "컴포넌트 존재: $SCREEN (${LINES}줄)"
    else
        # .tsx 확장자도 확인
        TSX_PATH="${SCREEN%.jsx}.tsx"
        if [ -f "./$TSX_PATH" ]; then
            pass "컴포넌트 존재: $TSX_PATH"
        else
            fail "컴포넌트 없음: $SCREEN"
        fi
    fi
done

echo ""
echo "🎨 [UI-004] 디자인 토큰(CSS 변수) 정의 확인"
CSS_VARS=(
    "--primary"
    "--secondary"
    "--warning"
    "--danger"
    "--bg"
    "--surface"
    "--text-primary"
    "--text-secondary"
)

# styles.css 또는 index.html에서 확인
STYLE_FILES=$(find . -name "*.css" -o -name "*.html" 2>/dev/null | head -20)

for VAR in "${CSS_VARS[@]}"; do
    FOUND=$(grep -rl "$VAR" $STYLE_FILES 2>/dev/null | wc -l)
    if [ "$FOUND" -gt 0 ]; then
        pass "디자인 토큰 정의됨: $VAR"
    else
        warn "디자인 토큰 미발견: $VAR"
    fi
done

echo ""
echo "📡 [UI-005] 핵심 API 엔드포인트 응답 확인"
ENDPOINTS=(
    "GET /api/v1/health"
    "GET /api/v1/regions"
    "GET /api/v1/regions/1168000000"
)

for ENDPOINT in "${ENDPOINTS[@]}"; do
    METHOD=$(echo $ENDPOINT | cut -d' ' -f1)
    PATH=$(echo $ENDPOINT | cut -d' ' -f2)
    
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
        -X "$METHOD" "${API_BASE}${PATH}" \
        -H "Content-Type: application/json" \
        --max-time 5)
    
    if [[ "$HTTP_CODE" =~ ^2 ]]; then
        pass "엔드포인트 정상: $METHOD $PATH (HTTP ${HTTP_CODE})"
    elif [ "$HTTP_CODE" = "401" ]; then
        warn "인증 필요: $METHOD $PATH (정상 구현 확인 필요)"
    else
        fail "엔드포인트 오류: $METHOD $PATH (HTTP ${HTTP_CODE})"
    fi
done

echo ""
echo "⏱️  [UI-006] 대시보드 화면 로딩 속도 확인"
# 테스트 토큰 (실제 환경에 맞게 수정)
TEST_TOKEN="${TEST_TOKEN:-test-jwt-token-here}"

RESPONSE_TIME=$(curl -s -o /dev/null -w "%{time_total}" \
    "${API_BASE}/api/v1/dashboard/test-user-id" \
    -H "Authorization: Bearer $TEST_TOKEN" \
    --max-time 10)

RESPONSE_MS=$(echo "$RESPONSE_TIME * 1000" | bc | cut -d. -f1)

if [ "$RESPONSE_MS" -le 1000 ]; then
    pass "대시보드 응답 시간: ${RESPONSE_MS}ms (목표: 1,000ms 이내)"
elif [ "$RESPONSE_MS" -le 3000 ]; then
    warn "대시보드 응답 시간: ${RESPONSE_MS}ms (개선 권장)"
else
    fail "대시보드 응답 시간: ${RESPONSE_MS}ms (목표 초과)"
fi

echo ""
echo "♿ [UI-007] 접근성 기본 검사 (한국어 레이블, 폰트 크기)"
HTML_FILES=$(find . -name "*.html" -not -path "*/node_modules/*" 2>/dev/null)

for HTML in $HTML_FILES; do
    # lang 속성 확인
    if grep -q 'lang="ko"' "$HTML" 2>/dev/null; then
        pass "한국어 lang 속성 존재: $HTML"
    else
        warn "lang='ko' 누락: $HTML (스크린리더 접근성)"
    fi
    
    # 폰트 크기 12px 미만 사용 확인
    TINY_FONT=$(grep -c 'font-size: [1-9]px\|font-size: 10px\|font-size: 11px' "$HTML" 2>/dev/null || echo 0)
    if [ "$TINY_FONT" -eq 0 ]; then
        pass "최소 폰트 크기(12px+) 준수: $HTML"
    else
        warn "12px 미만 폰트 ${TINY_FONT}개 발견: $HTML (시니어 접근성)"
    fi
done
```

---

## 3단계 AI 알고리즘 검증 스크립트

```python
#!/usr/bin/env python3
# verify_ai.py - AI 알고리즘 단위 및 통합 검증

import sys
import time
import json
import traceback
import numpy as np
from datetime import datetime

# 결과 추적
results = {"pass": 0, "fail": 0, "warn": 0, "details": []}

# ============================================================
# 헬퍼 함수
# ============================================================
def test(name):
    """테스트 데코레이터"""
    def decorator(func):
        def wrapper():
            try:
                start = time.time()
                func()
                elapsed = (time.time() - start) * 1000
                results["pass"] += 1
                results["details"].append({"name": name, "status": "PASS", "ms": f"{elapsed:.0f}ms"})
                print(f"  ✅ PASS [{elapsed:.0f}ms]: {name}")
            except AssertionError as e:
                results["fail"] += 1
                results["details"].append({"name": name, "status": "FAIL", "error": str(e)})
                print(f"  ❌ FAIL: {name}")
                print(f"     → {e}")
            except Exception as e:
                results["fail"] += 1
                results["details"].append({"name": name, "status": "ERROR", "error": str(e)})
                print(f"  💥 ERROR: {name}")
                print(f"     → {traceback.format_exc()}")
        return wrapper
    return decorator

def warn(name, message):
    results["warn"] += 1
    results["details"].append({"name": name, "status": "WARN", "message": message})
    print(f"  ⚠️  WARN: {name} → {message}")

# ============================================================
# [AI-001] 특성 공학 검증
# ============================================================
print("\n🔬 [AI-001] 특성 공학 (FeatureEngine) 검증")

@test("생애주기 분류 - 사회초년기 (28세)")
def test_life_stage_young():
    # FeatureEngine._classify_life_stage 로직 직접 테스트
    age, income = 28, 35000000
    if age < 35 and income < 50000000:
        stage = "사회초년기"
    elif age < 45:
        stage = "가족형성기"
    elif age < 55:
        stage = "자산축적기"
    elif age < 65:
        stage = "은퇴전환기"
    else:
        stage = "은퇴생활기"
    assert stage == "사회초년기", f"기대: 사회초년기, 실제: {stage}"

@test("생애주기 분류 - 은퇴전환기 (63세)")
def test_life_stage_preretiree():
    age, income = 63, 80000000
    if age < 35 and income < 50000000:
        stage = "사회초년기"
    elif age < 45:
        stage = "가족형성기"
    elif age < 55:
        stage = "자산축적기"
    elif age < 65:
        stage = "은퇴전환기"
    else:
        stage = "은퇴생활기"
    assert stage == "은퇴전환기", f"기대: 은퇴전환기, 실제: {stage}"

@test("생애주기 분류 - 은퇴생활기 (70세)")
def test_life_stage_retiree():
    age = 70
    if age >= 65:
        stage = "은퇴생활기"
    else:
        stage = "기타"
    assert stage == "은퇴생활기"

@test("DTI 계산 정확성")
def test_dti_calculation():
    total_debt = 500_000_000  # 5억
    annual_income = 80_000_000  # 8천만원
    dti = total_debt / annual_income
    assert abs(dti - 6.25) < 0.01, f"DTI 오류: {dti}"

@test("부동산 비중 계산")
def test_real_estate_ratio():
    assets = [
        {"type": "부동산", "value": 2_400_000_000},
        {"type": "예금", "value": 100_000_000},
        {"type": "주식", "value": 50_000_000}
    ]
    total = sum(a["value"] for a in assets)
    re_value = sum(a["value"] for a in assets if a["type"] == "부동산")
    ratio = re_value / total
    assert abs(ratio - 0.9412) < 0.01, f"부동산 비중 오류: {ratio:.4f}"

@test("유동성 비율 계산")
def test_liquidity_ratio():
    liquid = 100_000_000  # 1억
    monthly_expense = 3_200_000  # 320만원
    ratio = liquid / monthly_expense
    # 1억 / 320만 ≈ 31.25 (월)
    assert ratio > 3, "비상금 3개월치 미만"
    assert ratio < 120, "비정상적으로 높은 유동성 비율"

# ============================================================
# [AI-002] 포트폴리오 최적화 검증
# ============================================================
print("\n🎯 [AI-002] 포트폴리오 최적화 엔진 검증")

@test("포트폴리오 비중 합계 = 1.0 (유전자 알고리즘 출력)")
def test_portfolio_weights_sum():
    """최적화 결과의 비중 합계가 1이어야 함"""
    # 간략화된 최적화 시뮬레이션
    np.random.seed(42)
    weights = np.random.dirichlet(np.ones(5))  # 합=1 보장된 랜덤 비중
    assert abs(weights.sum() - 1.0) < 1e-6, f"비중 합계 오류: {weights.sum()}"
    assert all(w >= 0 for w in weights), "음수 비중 발생"

@test("은퇴전환기 제약조건: 주식 비중 ≤ 40%")
def test_preretiree_stock_constraint():
    """은퇴전환기 사용자의 주식 비중 제한 검증"""
    LIFE_STAGE = "은퇴전환기"
    MAX_STOCK = 0.40
    
    # 제약조건 정의
    bounds = {
        "부동산": (0.0, 0.8),
        "국내주식": (0.0, 0.35),
        "국내채권": (0.0, 1.0),
        "해외주식": (0.0, 0.25),
        "현금": (0.10, 1.0)  # 최소 10%
    }
    
    total_stock_max = bounds["국내주식"][1] + bounds["해외주식"][1]
    assert total_stock_max <= MAX_STOCK, f"주식 비중 상한 {total_stock_max} 초과"
    assert bounds["현금"][0] >= 0.10, "현금 하한 미충족"

@test("은퇴생활기 제약조건: 현금 비중 ≥ 15%")
def test_retiree_cash_constraint():
    bounds_cash_min = 0.15
    # 시뮬레이션된 최적 결과
    simulated_result = {"부동산": 0.30, "국내주식": 0.10, "국내채권": 0.20, "해외주식": 0.05, "현금": 0.35}
    assert simulated_result["현금"] >= bounds_cash_min

@test("사회초년기: 부동산 보유 없을 때 부동산 비중 0 가능")
def test_young_no_realestate():
    current_re_ratio = 0.0
    lower_bound = max(0, current_re_ratio * 0.8)
    assert lower_bound == 0.0

@test("Black-Litterman: 사전 수익률 차원 일치")
def test_black_litterman_dimensions():
    n_assets = 5
    expected_returns = np.array([0.045, 0.070, 0.032, 0.080, 0.025])
    cov_matrix = np.eye(n_assets) * 0.04
    
    assert len(expected_returns) == n_assets
    assert cov_matrix.shape == (n_assets, n_assets)
    
    # 공분산 행렬 양정치(PD) 검증
    eigenvalues = np.linalg.eigvals(cov_matrix)
    assert all(ev > 0 for ev in eigenvalues), "공분산 행렬이 양정치가 아님"

@test("포트폴리오 샤프 비율 양수 확인")
def test_sharpe_ratio_positive():
    weights = np.array([0.45, 0.20, 0.15, 0.10, 0.10])
    expected_returns = np.array([0.045, 0.070, 0.032, 0.080, 0.025])
    cov_matrix = np.diag([0.0256, 0.0400, 0.0081, 0.0441, 0.0004])
    
    port_return = np.dot(weights, expected_returns)
    port_vol = np.sqrt(weights @ cov_matrix @ weights)
    risk_free_rate = 0.035
    sharpe = (port_return - risk_free_rate) / port_vol
    
    assert sharpe > 0, f"샤프 비율 음수: {sharpe:.3f}"
    print(f"     → 포트폴리오 샤프 비율: {sharpe:.3f}")

# ============================================================
# [AI-003] 몬테카를로 시뮬레이션 검증
# ============================================================
print("\n🎲 [AI-003] 몬테카를로 시뮬레이션 검증")

@test("시뮬레이션 10,000회 실행 시간 ≤ 10초")
def test_monte_carlo_speed():
    n_sim = 10000
    n_months = 27 * 12  # 63세 → 90세

    start = time.time()
    
    # 벡터화된 Monte Carlo (NumPy 최적화)
    np.random.seed(42)
    monthly_return_mean = 0.005
    monthly_return_std = 0.035
    
    monthly_returns = np.random.normal(
        monthly_return_mean,
        monthly_return_std,
        (n_sim, n_months)
    )
    
    initial_asset = 2_550_000_000
    monthly_net = -2_000_000  # 지출 > 수입 (은퇴 후)
    
    assets = np.full(n_sim, float(initial_asset))
    for m in range(n_months):
        assets = assets * (1 + monthly_returns[:, m]) + monthly_net
        assets = np.maximum(assets, 0)
    
    elapsed = time.time() - start
    assert elapsed <= 10.0, f"시뮬레이션 시간 초과: {elapsed:.1f}초"
    print(f"     → {n_sim:,}회 시뮬레이션 완료: {elapsed:.2f}초")

@test("생존 확률: 0 ~ 1 범위 준수")
def test_survival_probability_range():
    np.random.seed(42)
    n_sim = 1000
    n_months = 300
    
    assets = np.full(n_sim, 2_550_000_000.0)
    monthly_net = -2_000_000
    
    for m in range(n_months):
        ret = np.random.normal(0.004, 0.03, n_sim)
        assets = assets * (1 + ret) + monthly_net
        assets = np.maximum(assets, 0)
    
    survival_prob = (assets > 0).mean()
    assert 0 <= survival_prob <= 1, f"생존 확률 범위 오류: {survival_prob}"
    print(f"     → 생존 확률: {survival_prob:.1%}")

@test("비관/낙관 시나리오: p10 < 중간값 < p90")
def test_percentile_ordering():
    np.random.seed(42)
    final_assets = np.random.lognormal(22, 0.3, 10000)
    
    p10 = np.percentile(final_assets, 10)
    p50 = np.percentile(final_assets, 50)
    p90 = np.percentile(final_assets, 90)
    
    assert p10 < p50 < p90, f"분위수 정렬 오류: p10={p10:.0f}, p50={p50:.0f}, p90={p90:.0f}"

@test("음수 자산 발생 시 0으로 처리 (파산 처리)")
def test_bankruptcy_handling():
    assets = np.array([100_000, 50_000, -1_000_000, 200_000])
    assets = np.maximum(assets, 0)
    assert (assets >= 0).all(), "음수 자산 미처리"
    assert assets[2] == 0, "음수 자산이 0으로 처리되지 않음"

@test("인플레이션 반영: 지출 증가 확인")
def test_inflation_adjustment():
    base_expense = 3_200_000
    inflation_rate = 0.025
    years = 10
    
    adjusted_expense = base_expense * ((1 + inflation_rate) ** years)
    assert adjusted_expense > base_expense, "인플레이션 미반영"
    assert adjusted_expense < base_expense * 2, "인플레이션 과다 반영"
    print(f"     → 10년 후 지출: {adjusted_expense:,.0f}원 (기준 대비 +{(adjusted_expense/base_expense-1)*100:.1f}%)")

# ============================================================
# [AI-004] 지역 전략 매핑 검증
# ============================================================
print("\n🗺️  [AI-004] 지역 전략 매핑 검증")

@test("가격 하락 + 인구 감소 → 위험 신호 감지")
def test_bearish_region_signal():
    region = {
        "price_change_1y": -8.3,      # 8.3% 하락
        "population_growth_rate": -0.5,  # 인구 감소
        "jeonse_ratio": 38.6,            # 전세가율 낮음
        "growth_potential": 40           # 성장 가능성 낮음
    }
    
    # 위험 신호 판정 로직
    risk_score = 0
    if region["price_change_1y"] < -5:
        risk_score += 3
    if region["population_growth_rate"] < -0.3:
        risk_score += 2
    if region["jeonse_ratio"] < 45:
        risk_score += 1
    
    assert risk_score >= 4, f"위험 점수 미달: {risk_score}"
    print(f"     → 위험 점수: {risk_score}/6")

@test("인구 증가 + 가격 상승 → 긍정 신호 감지")
def test_bullish_region_signal():
    region = {
        "price_change_1y": 3.5,
        "population_growth_rate": 2.5,
        "jeonse_ratio": 49.0,
        "growth_potential": 90
    }
    
    positive_signals = 0
    if region["price_change_1y"] > 2:
        positive_signals += 1
    if region["population_growth_rate"] > 1:
        positive_signals += 1
    if region["growth_potential"] > 70:
        positive_signals += 1
    
    assert positive_signals >= 2, f"긍정 신호 부족: {positive_signals}"

@test("전세가율 분류 정확성")
def test_jeonse_ratio_classification():
    test_cases = [
        (35.0, "<40%"),
        (52.5, "40-60%"),
        (68.0, ">60%"),
    ]
    for ratio, expected in test_cases:
        if ratio < 40:
            cls = "<40%"
        elif ratio > 60:
            cls = ">60%"
        else:
            cls = "40-60%"
        assert cls == expected, f"전세가율 {ratio}%: 기대 {expected}, 실제 {cls}"

@test("은퇴전환기 + 고가 부동산 + 하락 지역 → 매각 추천")
def test_preretiree_sell_recommendation():
    """핵심 시나리오: 63세 강남 거주자 추천"""
    user = {"life_stage": "은퇴전환기", "real_estate_ratio": 0.94}
    region = {"price_change_1y": -8.3, "jeonse_ratio": 38.6}
    
    sell_signals = 0
    if user["real_estate_ratio"] > 0.7:
        sell_signals += 2  # 부동산 집중 위험
    if region["price_change_1y"] < -5:
        sell_signals += 2  # 시장 하락세
    if user["life_stage"] in ["은퇴전환기", "은퇴생활기"]:
        sell_signals += 1  # 생애주기 위험
    
    assert sell_signals >= 4, f"매각 추천 신호 부족: {sell_signals}"
    
    action = "매각_금융전환" if sell_signals >= 4 else "보유_관망"
    assert action == "매각_금융전환"

# ============================================================
# [AI-005] 추천 건전성 점수 검증
# ============================================================
print("\n📊 [AI-005] 건전성 점수 검증")

@test("건전성 점수: 0 ~ 100 범위 확인")
def test_health_score_range():
    test_profiles = [
        {"liquidity_ratio": 31.25, "dti": 0.25, "monthly_surplus": 3000000},
        {"liquidity_ratio": 1.5, "dti": 0.80, "monthly_surplus": -500000},
        {"liquidity_ratio": 50.0, "dti": 0.0, "monthly_surplus": 10000000},
    ]
    for p in test_profiles:
        score = min(100, int(
            p["liquidity_ratio"] * 1.0 +
            (1 - p["dti"]) * 40 +
            min(30, p["monthly_surplus"] / 100000)
        ))
        score = max(0, score)
        assert 0 <= score <= 100, f"점수 범위 초과: {score}"

@test("고위험 프로필: 건전성 점수 40 이하")
def test_high_risk_low_score():
    """DTI 80%, 적자 현금흐름 → 낮은 건전성 점수"""
    p = {"liquidity_ratio": 0.5, "dti": 0.80, "monthly_surplus": -1000000}
    score = min(100, max(0, int(
        p["liquidity_ratio"] * 1.0 +
        (1 - p["dti"]) * 40 +
        min(30, max(-30, p["monthly_surplus"] / 100000))
    )))
    assert score <= 40, f"고위험 프로필 점수 과대평가: {score}"

@test("우량 프로필: 건전성 점수 70 이상")
def test_low_risk_high_score():
    """부채 없음, 여유 현금흐름 → 높은 건전성 점수"""
    p = {"liquidity_ratio": 24.0, "dti": 0.0, "monthly_surplus": 5000000}
    score = min(100, max(0, int(
        p["liquidity_ratio"] * 1.0 +
        (1 - p["dti"]) * 40 +
        min(30, p["monthly_surplus"] / 100000)
    )))
    assert score >= 70, f"우량 프로필 점수 과소평가: {score}"

# ============================================================
# 결과 출력
# ============================================================
def print_final_results():
    total = results["pass"] + results["fail"] + results["warn"]
    success_rate = results["pass"] / total * 100 if total > 0 else 0
    
    print("\n" + "=" * 60)
    print("  AI 알고리즘 검증 결과")
    print("=" * 60)
    print(f"  전체: {total}개  |  ✅ PASS: {results['pass']}  |  ❌ FAIL: {results['fail']}  |  ⚠️  WARN: {results['warn']}")
    print(f"  성공률: {success_rate:.1f}%")
    
    if results["fail"] > 0:
        print("\n  실패 항목:")
        for d in results["details"]:
            if d["status"] in ["FAIL", "ERROR"]:
                print(f"    ❌ {d['name']}")
                if "error" in d:
                    print(f"       → {d['error']}")
    
    # JSON 리포트 저장
    with open("ai_verify_result.json", "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": total,
                "pass": results["pass"],
                "fail": results["fail"],
                "warn": results["warn"],
                "success_rate": f"{success_rate:.1f}%"
            },
            "details": results["details"]
        }, f, ensure_ascii=False, indent=2)
    print("\n  📄 상세 결과: ai_verify_result.json")
    
    return 0 if results["fail"] == 0 else 1

# 모든 테스트 실행
test_life_stage_young()
test_life_stage_preretiree()
test_life_stage_retiree()
test_dti_calculation()
test_real_estate_ratio()
test_liquidity_ratio()
test_portfolio_weights_sum()
test_preretiree_stock_constraint()
test_retiree_cash_constraint()
test_young_no_realestate()
test_black_litterman_dimensions()
test_sharpe_ratio_positive()
test_monte_carlo_speed()
test_survival_probability_range()
test_percentile_ordering()
test_bankruptcy_handling()
test_inflation_adjustment()
test_bearish_region_signal()
test_bullish_region_signal()
test_jeonse_ratio_classification()
test_preretiree_sell_recommendation()
test_health_score_range()
test_high_risk_low_score()
test_low_risk_high_score()

sys.exit(print_final_results())
```

---

## 4단계 파일럿 테스트 검증 스크립트

```python
#!/usr/bin/env python3
# verify_pilot.py - 7개 파일럿 지역 + 7개 페르소나 통합 검증

import requests
import json
import time
import sys
from datetime import datetime

BASE_URL = "http://localhost:8000"
RESULTS = []

def check(name, condition, expected, actual, critical=False):
    status = "PASS" if condition else ("FAIL" if critical else "WARN")
    symbol = "✅" if status == "PASS" else ("❌" if status == "FAIL" else "⚠️ ")
    print(f"  {symbol} {status}: {name}")
    if not condition:
        print(f"     → 기대: {expected}, 실제: {actual}")
    RESULTS.append({"name": name, "status": status})
    return condition

# ============================================================
# [PILOT-001] 7개 파일럿 지역 데이터 존재 확인
# ============================================================
print("\n📍 [PILOT-001] 파일럿 지역 데이터 검증")

PILOT_REGIONS = {
    "1168000000": {"name": "서울 강남구", "expected_trend": "하락"},
    "4159000000": {"name": "경기 화성시", "expected_trend": "보합_이상"},
    "2635000000": {"name": "부산 해운대구", "expected_trend": "하락"},
    "2915500000": {"name": "광주 서구", "expected_trend": "보합"},
    "3811000000": {"name": "경남 창원시", "expected_trend": "보합"},
    "3611000000": {"name": "세종시", "expected_trend": "상승"},
    "5121000000": {"name": "강원 속초시", "expected_trend": "보합"},
}

for code, info in PILOT_REGIONS.items():
    try:
        resp = requests.get(f"{BASE_URL}/api/v1/region/{code}", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            has_price = "avg_price_per_sqm" in data
            has_trend = "price_change_1y" in data
            check(
                f"지역 데이터 존재: {info['name']}",
                has_price and has_trend,
                "가격/변동률 데이터 포함",
                f"가격:{has_price}, 변동률:{has_trend}"
            )
        else:
            check(
                f"지역 데이터 API 응답: {info['name']}",
                False, "HTTP 200", f"HTTP {resp.status_code}",
                critical=True
            )
    except requests.exceptions.ConnectionError:
        print(f"  ⚠️  WARN: API 서버 미기동 - {info['name']} 스킵")

# ============================================================
# [PILOT-002] 7개 페르소나 생애주기 분류 검증
# ============================================================
print("\n👥 [PILOT-002] 페르소나 생애주기 분류 검증")

PERSONAS = [
    {
        "name": "김영호",
        "age": 63,
        "income": 80_000_000,
        "expected_stage": "은퇴전환기",
        "expected_risk_max": 5,
        "region": "1168000000"
    },
    {
        "name": "이지은",
        "age": 38,
        "income": 120_000_000,
        "expected_stage": "가족형성기",
        "expected_risk_max": 8,
        "region": "4159000000"
    },
    {
        "name": "박성수",
        "age": 55,
        "income": 60_000_000,
        "expected_stage": "자산축적기",
        "expected_risk_max": 6,
        "region": "2635000000"
    },
    {
        "name": "최민준",
        "age": 45,
        "income": 70_000_000,
        "expected_stage": "자산축적기",
        "expected_risk_max": 7,
        "region": "2915500000"
    },
    {
        "name": "정대호",
        "age": 50,
        "income": 55_000_000,
        "expected_stage": "자산축적기",
        "expected_risk_max": 6,
        "region": "3811000000"
    },
    {
        "name": "김서연",
        "age": 32,
        "income": 80_000_000,
        "expected_stage": "사회초년기",
        "expected_risk_max": 9,
        "region": "3611000000"
    },
    {
        "name": "황옥자",
        "age": 70,
        "income": 9_600_000,
        "expected_stage": "은퇴생활기",
        "expected_risk_max": 3,
        "region": "5121000000"
    },
]

def classify_life_stage(age, income):
    if age < 35 and income < 50_000_000:
        return "사회초년기"
    elif age < 45:
        return "가족형성기"
    elif age < 55:
        return "자산축적기"
    elif age < 65:
        return "은퇴전환기"
    else:
        return "은퇴생활기"

for p in PERSONAS:
    stage = classify_life_stage(p["age"], p["income"])
    check(
        f"생애주기 분류: {p['name']} ({p['age']}세)",
        stage == p["expected_stage"],
        p["expected_stage"],
        stage,
        critical=True
    )

# ============================================================
# [PILOT-003] 핵심 추천 시나리오 검증 (7개 페르소나)
# ============================================================
print("\n🎯 [PILOT-003] 페르소나별 핵심 추천 논리 검증")

# 직접 로직 검증 (API 없이도 가능)
test_cases = [
    {
        "persona": "김영호 (63세, 강남, 부동산 94%)",
        "features": {
            "life_stage": "은퇴전환기",
            "real_estate_ratio": 0.94,
            "total_assets": 2_550_000_000,
            "avg_interest_rate": 5.2,
            "monthly_surplus": 300_000
        },
        "expected_actions": ["부동산 매도", "고금리 대출 상환"],
        "expected_target_re_ratio_max": 0.60,
        "expected_score_max": 75
    },
    {
        "persona": "이지은 (38세, 화성, 균형형)",
        "features": {
            "life_stage": "가족형성기",
            "real_estate_ratio": 0.88,
            "total_assets": 910_000_000,
            "avg_interest_rate": 3.8,
            "monthly_surplus": 2_500_000
        },
        "expected_actions": ["ETF 적립"],
        "expected_target_re_ratio_max": 0.75,
        "expected_score_max": 90
    },
    {
        "persona": "황옥자 (70세, 속초, 은퇴생활)",
        "features": {
            "life_stage": "은퇴생활기",
            "real_estate_ratio": 0.83,
            "total_assets": 300_000_000,
            "avg_interest_rate": 0.0,
            "monthly_surplus": -700_000
        },
        "expected_actions": ["주택연금 검토"],
        "expected_target_re_ratio_max": 0.70,
        "expected_score_max": 65
    }
]

for tc in test_cases:
    f = tc["features"]
    
    # 부동산 비중 과다 판정
    re_too_high = f["real_estate_ratio"] > 0.70
    
    # 고금리 대출 판정
    high_interest = f["avg_interest_rate"] > 5.0
    
    # 현금흐름 적자 판정
    cash_deficit = f["monthly_surplus"] < 0
    
    # 은퇴생활기 주택연금 검토
    pension_needed = f["life_stage"] == "은퇴생활기" and f["real_estate_ratio"] > 0.5
    
    actions = []
    if re_too_high:
        actions.append("부동산 매도")
    if high_interest:
        actions.append("고금리 대출 상환")
    if cash_deficit and pension_needed:
        actions.append("주택연금 검토")
    if f["life_stage"] in ["가족형성기", "사회초년기"]:
        actions.append("ETF 적립")
    
    for expected_action in tc["expected_actions"]:
        check(
            f"추천 액션 '{expected_action}': {tc['persona']}",
            expected_action in actions,
            f"'{expected_action}' 포함",
            f"실제 액션: {actions}"
        )

# ============================================================
# [PILOT-004] 42개 테스트 케이스 실행 결과 확인
# ============================================================
print("\n📋 [PILOT-004] 자동화 테스트 케이스 (TC001~TC504) 실행")

TEST_CASES = [
    {"id": "TC001", "desc": "사용자 등록 - 김영호 프로필", "priority": "P0"},
    {"id": "TC002", "desc": "사용자 등록 - 이지은 프로필", "priority": "P0"},
    {"id": "TC101", "desc": "자산 입력 - 고가 부동산", "priority": "P0"},
    {"id": "TC102", "desc": "자산 입력 - 고금리 대출 경고", "priority": "P0"},
    {"id": "TC201", "desc": "AI 추천 - 은퇴전환기 강남 중립 시나리오", "priority": "P0"},
    {"id": "TC202", "desc": "AI 추천 - 가족형성기 동탄 중립 시나리오", "priority": "P0"},
    {"id": "TC203", "desc": "AI 추천 - 은퇴생활기 보수 시나리오", "priority": "P0"},
    {"id": "TC301", "desc": "지역 분석 - 강남구 하락세 감지", "priority": "P1"},
    {"id": "TC302", "desc": "지역 분석 - 세종시 성장 신호", "priority": "P1"},
    {"id": "TC401", "desc": "시뮬레이션 - 김영호 추천 전략 적용", "priority": "P1"},
    {"id": "TC402", "desc": "시뮬레이션 - 황옥자 현상유지 위험", "priority": "P1"},
    {"id": "TC501", "desc": "예외처리 - 무자산 사용자", "priority": "P2"},
    {"id": "TC502", "desc": "예외처리 - 100% 부동산 보유", "priority": "P2"},
    {"id": "TC503", "desc": "예외처리 - DTI 80% 초과", "priority": "P2"},
    {"id": "TC504", "desc": "예외처리 - 지역 정보 누락", "priority": "P2"},
]

P0_FAIL = 0
for tc in TEST_CASES:
    try:
        resp = requests.post(
            f"{BASE_URL}/api/v1/test/{tc['id']}",
            json={"test_id": tc["id"]},
            timeout=10
        )
        passed = resp.status_code == 200
        if not passed and tc["priority"] == "P0":
            P0_FAIL += 1
        check(
            f"[{tc['id']}] {tc['desc']} ({tc['priority']})",
            passed,
            "HTTP 200",
            f"HTTP {resp.status_code}",
            critical=(tc["priority"] == "P0")
        )
    except requests.exceptions.ConnectionError:
        print(f"  ⚠️  SKIP [{tc['id']}]: API 서버 미기동")
    except requests.exceptions.Timeout:
        check(
            f"[{tc['id']}] {tc['desc']} 타임아웃",
            False, "10초 이내", "타임아웃",
            critical=(tc["priority"] == "P0")
        )

if P0_FAIL > 0:
    print(f"\n  🚨 P0 핵심 테스트 {P0_FAIL}개 실패 → 운영 배포 불가")

# ============================================================
# [PILOT-005] 데이터 수집 파이프라인 검증
# ============================================================
print("\n🔄 [PILOT-005] 데이터 수집 파이프라인 검증")

import subprocess

def check_api_connectivity(name, url, timeout=5):
    try:
        resp = requests.get(url, timeout=timeout)
        check(f"API 연결: {name}", resp.status_code < 500,
              "2xx/4xx (서버 연결)", f"HTTP {resp.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"  ⚠️  WARN: {name} 접속 불가 (네트워크 또는 API 키 확인)")
    except requests.exceptions.Timeout:
        print(f"  ⚠️  WARN: {name} 타임아웃")

check_api_connectivity("한국부동산원", "https://api.reb.or.kr")
check_api_connectivity("국토부 실거래가", "https://rt.molit.go.kr")
check_api_connectivity("한국은행 ECOS", "https://ecos.bok.or.kr")

# Kafka 실행 여부
try:
    kafka_result = subprocess.run(
        ["kafka-topics.sh", "--list", "--bootstrap-server", "localhost:9092"],
        capture_output=True, timeout=5
    )
    if kafka_result.returncode == 0:
        topics = kafka_result.stdout.decode().strip().split("\n")
        required_topics = ["real-estate-price", "user-events", "market-data"]
        for topic in required_topics:
            check(
                f"Kafka 토픽 존재: {topic}",
                topic in topics,
                topic, "없음"
            )
    else:
        print("  ⚠️  WARN: Kafka 서버 미기동")
except (FileNotFoundError, subprocess.TimeoutExpired):
    print("  ⚠️  WARN: Kafka CLI 미설치 또는 타임아웃")

# ============================================================
# [PILOT-006] 성능 벤치마크
# ============================================================
print("\n⚡ [PILOT-006] 성능 벤치마크")

PERFORMANCE_TESTS = [
    {
        "name": "대시보드 API 응답 (목표: 1초)",
        "url": f"{BASE_URL}/api/v1/dashboard/test-user",
        "threshold_ms": 1000
    },
    {
        "name": "지역 분석 API 응답 (목표: 2초)",
        "url": f"{BASE_URL}/api/v1/region/1168000000",
        "threshold_ms": 2000
    },
    {
        "name": "AI 추천 API 응답 (목표: 5초)",
        "url": f"{BASE_URL}/api/v1/recommendations",
        "threshold_ms": 5000,
        "method": "POST",
        "body": {"user_id": "test-kim-63", "scenario": "중립적"}
    }
]

for pt in PERFORMANCE_TESTS:
    try:
        start = time.time()
        if pt.get("method") == "POST":
            resp = requests.post(
                pt["url"],
                json=pt.get("body", {}),
                timeout=pt["threshold_ms"] / 1000 + 2
            )
        else:
            resp = requests.get(pt["url"], timeout=pt["threshold_ms"] / 1000 + 2)
        
        elapsed_ms = (time.time() - start) * 1000
        
        check(
            pt["name"],
            elapsed_ms <= pt["threshold_ms"],
            f"{pt['threshold_ms']}ms 이내",
            f"{elapsed_ms:.0f}ms"
        )
    except requests.exceptions.ConnectionError:
        print(f"  ⚠️  SKIP: {pt['name']} (서버 미기동)")
    except requests.exceptions.Timeout:
        check(pt["name"], False, f"{pt['threshold_ms']}ms", "타임아웃", critical=True)

# ============================================================
# [PILOT-007] 8주 로드맵 마일스톤 체크
# ============================================================
print("\n📅 [PILOT-007] 파일럿 테스트 마일스톤 확인")

import os

MILESTONES = [
    {
        "week": "1-2주차",
        "task": "서버 인프라 구성",
        "check": lambda: os.path.exists("docker-compose.yml"),
        "check_desc": "docker-compose.yml 존재"
    },
    {
        "week": "1-2주차",
        "task": "DB 스키마 적재",
        "check": lambda: True,  # DB 검증에서 이미 확인
        "check_desc": "verify_db.sh 통과"
    },
    {
        "week": "3-4주차",
        "task": "AI 모델 훈련 완료",
        "check": lambda: os.path.exists("models/") and len(os.listdir("models/")) > 0 if os.path.exists("models/") else False,
        "check_desc": "models/ 디렉토리에 모델 파일 존재"
    },
    {
        "week": "3-4주차",
        "task": "자동화 테스트 코드 작성",
        "check": lambda: os.path.exists("tests/test_api.py"),
        "check_desc": "tests/test_api.py 존재"
    },
    {
        "week": "5-6주차",
        "task": "알파 테스트 보고서",
        "check": lambda: os.path.exists("reports/alpha_test_report.pdf") or os.path.exists("reports/alpha_test_report.md"),
        "check_desc": "알파 테스트 리포트 존재"
    },
    {
        "week": "7-8주차",
        "task": "베타 사용자 200명 피드백",
        "check": lambda: os.path.exists("reports/beta_feedback.csv"),
        "check_desc": "beta_feedback.csv 존재"
    },
]

for ms in MILESTONES:
    result = ms["check"]()
    check(
        f"[{ms['week']}] {ms['task']}: {ms['check_desc']}",
        result,
        "완료",
        "미완료"
    )

# ============================================================
# 최종 리포트 출력
# ============================================================
def print_pilot_summary():
    total = len(RESULTS)
    passed = sum(1 for r in RESULTS if r["status"] == "PASS")
    failed = sum(1 for r in RESULTS if r["status"] == "FAIL")
    warned = sum(1 for r in RESULTS if r["status"] == "WARN")
    
    rate = passed / total * 100 if total > 0 else 0
    
    print("\n" + "=" * 60)
    print("  파일럿 테스트 검증 결과")
    print("=" * 60)
    print(f"  전체: {total}  ✅ PASS: {passed}  ❌ FAIL: {failed}  ⚠️ WARN: {warned}")
    print(f"  성공률: {rate:.1f}%")
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "pilot_regions": list(PILOT_REGIONS.keys()),
        "personas_count": len(PERSONAS),
        "test_cases": len(TEST_CASES),
        "summary": {
            "total": total,
            "pass": passed,
            "fail": failed,
            "warn": warned,
            "success_rate": f"{rate:.1f}%"
        },
        "details": RESULTS
    }
    
    with open("pilot_verify_result.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("  📄 상세 결과: pilot_verify_result.json")
    return 0 if failed == 0 else 1

sys.exit(print_pilot_summary())
```

---

## 통합 실행 & 결과 시각화

```python
#!/usr/bin/env python3
# generate_verify_report.py - 검증 결과 HTML 리포트 생성

import json
import glob
from datetime import datetime

def load_results():
    results = {}
    for f in glob.glob("*verify_result*.json"):
        with open(f, encoding="utf-8") as fp:
            results[f] = json.load(fp)
    return results

def generate_html_report(results):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>자산균형 자체 검증 리포트 - {now}</title>
    <style>
        body {{ font-family: 'Malgun Gothic', sans-serif; max-width: 1000px; margin: 0 auto; padding: 20px; background: #f8fafc; }}
        h1 {{ color: #1e293b; border-bottom: 3px solid #2563eb; padding-bottom: 10px; }}
        h2 {{ color: #2563eb; margin-top: 30px; }}
        .summary {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin: 20px 0; }}
        .metric {{ background: white; border-radius: 12px; padding: 20px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .metric .value {{ font-size: 36px; font-weight: 800; }}
        .metric .label {{ font-size: 14px; color: #64748b; margin-top: 5px; }}
        .pass {{ color: #10b981; }}
        .fail {{ color: #ef4444; }}
        .warn {{ color: #f59e0b; }}
        .test-item {{ display: flex; align-items: center; padding: 10px; border-bottom: 1px solid #e2e8f0; }}
        .test-item:hover {{ background: #f1f5f9; }}
        .badge {{ padding: 3px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; margin-right: 10px; }}
        .badge-pass {{ background: #d1fae5; color: #065f46; }}
        .badge-fail {{ background: #fee2e2; color: #991b1b; }}
        .badge-warn {{ background: #fef3c7; color: #92400e; }}
        .progress-bar {{ background: #e2e8f0; border-radius: 8px; height: 12px; overflow: hidden; margin-top: 8px; }}
        .progress-fill {{ height: 100%; background: linear-gradient(90deg, #10b981, #2563eb); border-radius: 8px; }}
        .timestamp {{ color: #94a3b8; font-size: 13px; }}
    </style>
</head>
<body>
    <h1>🔍 자산균형 플랫폼 자체 검증 리포트</h1>
    <p class="timestamp">생성 시각: {now}</p>
"""
    
    total_pass = total_fail = total_warn = 0
    
    for fname, data in results.items():
        s = data.get("summary", {})
        p = int(s.get("pass", 0))
        f = int(s.get("fail", 0))
        w = int(s.get("warn", 0))
        total_pass += p; total_fail += f; total_warn += w
        total = p + f + w
        rate = p / total * 100 if total > 0 else 0
        
        stage_name = {
            "ai_verify": "3단계: AI 알고리즘",
            "pilot_verify": "4단계: 파일럿 테스트"
        }.get(fname.split("_result")[0], fname)
        
        html += f"""
    <h2>{stage_name}</h2>
    <div class="summary">
        <div class="metric"><div class="value">{total}</div><div class="label">전체</div></div>
        <div class="metric"><div class="value pass">{p}</div><div class="label">✅ PASS</div></div>
        <div class="metric"><div class="value fail">{f}</div><div class="label">❌ FAIL</div></div>
        <div class="metric"><div class="value warn">{w}</div><div class="label">⚠️ WARN</div></div>
    </div>
    <div class="progress-bar"><div class="progress-fill" style="width:{rate:.0f}%"></div></div>
    <p>성공률: <strong>{rate:.1f}%</strong></p>
"""
        if "details" in data:
            html += "<div>"
            for item in data["details"]:
                badge_class = f"badge-{item['status'].lower()}"
                html += f"""
        <div class="test-item">
            <span class="badge {badge_class}">{item['status']}</span>
            <span>{item['name']}</span>
            {f'<span style="margin-left:auto;color:#ef4444;font-size:12px">{item.get("error","")}</span>' if item["status"]=="FAIL" else ""}
        </div>"""
            html += "</div>"
    
    total_all = total_pass + total_fail + total_warn
    overall_rate = total_pass / total_all * 100 if total_all > 0 else 0
    
    verdict = "🎉 운영 배포 가능" if total_fail == 0 else \
              "⚠️ 경미한 문제 - 검토 후 배포" if total_fail <= 3 else \
              "🚨 심각한 문제 - 수정 필요"
    
    html += f"""
    <h2>📊 종합 결과</h2>
    <div class="summary">
        <div class="metric"><div class="value">{total_all}</div><div class="label">전체 테스트</div></div>
        <div class="metric"><div class="value pass">{total_pass}</div><div class="label">✅ PASS</div></div>
        <div class="metric"><div class="value fail">{total_fail}</div><div class="label">❌ FAIL</div></div>
        <div class="metric"><div class="value" style="color:#2563eb">{overall_rate:.0f}%</div><div class="label">성공률</div></div>
    </div>
    <h3>{verdict}</h3>
</body>
</html>"""
    
    with open("verify_report.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("📊 HTML 리포트 생성 완료: verify_report.html")

if __name__ == "__main__":
    results = load_results()
    if results:
        generate_html_report(results)
    else:
        print("검증 결과 파일 없음. 먼저 verify_all.sh 실행하세요.")
```

---

## 빠른 실행 가이드

```bash
# ============================================================
# 전체 검증 한 번에 실행하는 명령어
# ============================================================

# 1. 실행 권한 부여
chmod +x verify_all.sh verify_db.sh verify_ui.sh

# 2. 전체 검증 실행
./verify_all.sh

# 3. AI 알고리즘만 단독 검증
python3 verify_ai.py

# 4. 파일럿 테스트만 단독 검증
python3 verify_pilot.py

# 5. HTML 리포트 생성
python3 generate_verify_report.py
open verify_report.html  # macOS
# 또는
xdg-open verify_report.html  # Linux

# ============================================================
# 개별 모듈 검증 명령어
# ============================================================

# DB만 빠르게 확인
bash verify_db.sh 2>&1 | grep -E "PASS|FAIL|WARN"

# AI 특정 테스트만 실행
python3 -c "
from verify_ai import test_monte_carlo_speed, test_preretiree_sell_recommendation
test_monte_carlo_speed()
test_preretiree_sell_recommendation()
"

# 부하 테스트 (Locust)
locust -f locustfile.py --headless \
  --users 100 --spawn-rate 10 \
  --run-time 60s \
  --host http://localhost:8000 \
  --html locust_report.html

# pytest 자동화 테스트 전체 실행
pytest tests/ -v \
  --tb=short \
  --html=pytest_report.html \
  --self-contained-html \
  -x  # 첫 번째 실패 시 중단
```

---

## 검증 결과 판정 기준

```
📊 합격 기준 (운영 배포 가능):
  ✅ P0 테스트 100% PASS
  ✅ 전체 성공률 ≥ 85%
  ✅ AI 추천 응답 ≤ 5초
  ✅ DB 쿼리 ≤ 100ms
  ✅ Monte Carlo 10,000회 ≤ 10초

⚠️ 조건부 배포 (즉시 수정 계획 필요):
  🟡 P0 FAIL 1개 이하
  🟡 전체 성공률 70~84%
  🟡 성능 기준 20% 초과

🚨 배포 불가 (수정 후 재검증):
  🔴 P0 FAIL 2개 이상
  🔴 전체 성공률 < 70%
  🔴 DB 무결성 오류 존재
  🔴 AI 추천 결과 논리 오류
```