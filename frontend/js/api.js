// 자산균형 API 통신 모듈
const API_BASE_URL = "http://localhost:8000/api/v1";

async def fetchRecommendation(userId) {
    try {
        const response = await fetch(`${API_BASE_URL}/recommendations/${userId}`);
        return await response.json();
    } catch (error) {
        console.error("데이터 로드 실패:", error);
        return null;
    }
}

async def fetchRegionAnalysis(regionCode) {
    try {
        const response = await fetch(`${API_BASE_URL}/analysis/region/${regionCode}`);
        return await response.json();
    } catch (error) {
        console.error("지역 데이터 로드 실패:", error);
        return null;
    }
}

// 화면 초기화 및 애니메이션 처리
document.addEventListener('DOMContentLoaded', () => {
    console.log("자산균형 UI 엔진 가동 중...");
    // 숫자 카운팅 애니메이션 등 추가 예정
});
