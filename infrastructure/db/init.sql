-- ============================================
-- 자산균형(Asset Balance Korea) DB 초기화 스키마
-- ============================================

-- 1. 사용자 기본 정보
CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(50) NOT NULL,
    birth_date DATE NOT NULL,
    gender CHAR(1) CHECK (gender IN ('M', 'F')),
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    last_login TIMESTAMP
);

-- 2. 사용자 상세 프로필
CREATE TABLE IF NOT EXISTS user_profiles (
    profile_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    region_code VARCHAR(10) NOT NULL,
    job_category VARCHAR(30),
    job_detail VARCHAR(50),
    annual_income DECIMAL(15,2),
    family_type VARCHAR(20),
    dependents_count INT DEFAULT 0,
    housing_type VARCHAR(20),
    life_stage VARCHAR(20),
    risk_tolerance INT CHECK (risk_tolerance BETWEEN 1 AND 10),
    investment_experience INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. 지역 마스터 테이블 (전국 250개 시군구 기반)
CREATE TABLE IF NOT EXISTS region_master (
    region_code VARCHAR(10) PRIMARY KEY,
    region_name VARCHAR(50) NOT NULL,
    parent_code VARCHAR(10),
    level INT NOT NULL,
    area_sqkm DECIMAL(10,2),
    population INT,
    population_density DECIMAL(10,2),
    is_metropolitan BOOLEAN DEFAULT false
);

-- 4. 지역별 부동산 지수
CREATE TABLE IF NOT EXISTS region_real_estate_index (
    id BIGSERIAL PRIMARY KEY,
    region_code VARCHAR(10) REFERENCES region_master(region_code),
    index_date DATE NOT NULL,
    house_type VARCHAR(20) NOT NULL,
    avg_price_per_sqm DECIMAL(15,2),
    avg_jeonse_price_per_sqm DECIMAL(15,2),
    jeonse_to_sale_ratio DECIMAL(5,2),
    price_change_1m DECIMAL(5,2),
    price_change_1y DECIMAL(5,2),
    transaction_volume INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(region_code, index_date, house_type)
);

-- 5. 사용자 보유 자산
CREATE TABLE IF NOT EXISTS user_assets (
    asset_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    asset_type VARCHAR(30) NOT NULL,
    asset_subtype VARCHAR(50),
    asset_name VARCHAR(100),
    region_code VARCHAR(10) REFERENCES region_master(region_code),
    purchase_date DATE,
    purchase_price DECIMAL(15,2),
    current_value DECIMAL(15,2),
    debt_amount DECIMAL(15,2) DEFAULT 0,
    debt_interest_rate DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. 지역별 정성적 특성 (Module 2 연동용)
CREATE TABLE IF NOT EXISTS region_characteristics (
    region_code VARCHAR(10) PRIMARY KEY REFERENCES region_master(region_code),
    category VARCHAR(30),
    development_stage VARCHAR(30),
    infrastructure_score INT,
    growth_potential INT,
    investment_recommendation VARCHAR(30)
);

-- 7. 기초 데이터 삽입 (수도권 및 주요 광역시 확장)
INSERT INTO region_master (region_code, region_name, parent_code, level, area_sqkm, population, population_density, is_metropolitan) VALUES
('1100000000', '서울특별시', NULL, 1, 605.21, 9420000, 15569.2, true),
('1168000000', '서울 강남구', '1100000000', 2, 39.55, 548000, 13855.9, true),
('1171000000', '서울 송파구', '1100000000', 2, 33.88, 668000, 19716.6, true),
('4100000000', '경기도', NULL, 1, 10184.60, 13600000, 1335.4, true),
('4159000000', '경기 화성시', '4100000000', 2, 697.86, 906000, 1298.3, true),
('2600000000', '부산광역시', NULL, 1, 770.07, 3340000, 4337.3, false),
('2635000000', '부산 해운대구', '2600000000', 2, 51.53, 416000, 8072.9, false),
('2700000000', '대구광역시', NULL, 1, 883.7, 2380000, 2693.3, false),
('2723000000', '대구 수성구', '2700000000', 2, 76.5, 420000, 5490.2, false);

-- 7. 금융상품 마스터
CREATE TABLE IF NOT EXISTS financial_products (
    product_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_name VARCHAR(100) NOT NULL,
    category VARCHAR(30),
    provider VARCHAR(50),
    risk_level INT,
    expected_return DECIMAL(5,2),
    is_tax_benefit BOOLEAN DEFAULT false
);

-- 8. 사용자 소득/지출 (Cashflow)
CREATE TABLE IF NOT EXISTS user_cashflow (
    cashflow_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    record_year INT NOT NULL,
    record_month INT,
    salary_income DECIMAL(15,2) DEFAULT 0,
    living_expense DECIMAL(15,2) DEFAULT 0,
    debt_repayment DECIMAL(15,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 9. 리밸런싱 추천 기록 (History)
CREATE TABLE IF NOT EXISTS rebalancing_recommendations (
    recommendation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    recommendation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    summary VARCHAR(500),
    expected_return DECIMAL(5,2),
    risk_score DECIMAL(5,2)
);

-- 10. 대량 지역 데이터 확장 (전국 주요 50개 우선)
INSERT INTO region_master (region_code, region_name, parent_code, level, is_metropolitan) VALUES
('1165000000', '서울 서초구', '1100000000', 2, true),
('1144000000', '서울 마포구', '1100000000', 2, true),
('4111000000', '경기 수원시', '4100000000', 2, true),
('4113000000', '경기 성남시', '4100000000', 2, true),
('3611000000', '세종특별자치시', NULL, 1, false);

