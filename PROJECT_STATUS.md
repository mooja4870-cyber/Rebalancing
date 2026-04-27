# PROJECT_STATUS

Last updated: 2026-04-27 11:19:39

## Current State

- Inherited project at `d:\AI\project\Rebalancing`.
- GitHub remote `origin` is set to `https://github.com/mooja4870-cyber/Rebalancing.git`.
- Real user input analysis MVP exists: profile/cashflow/assets save API, DB financial snapshot table, personalized orchestration, input screen, and harness coverage.
- Required input report fields appear in the asset input flow: real estate, deposits, stocks, gold/silver, crypto asset, loan balance, monthly loan interest, monthly income, monthly expense, family count/ages, and retirement goal.
- Analysis API returns an `analysis_report` with asset, cashflow, debt, family, retirement goal, risk flags, simulation, and action plan sections.
- Asset input UX includes visible labels, helper text, required markers, mobile-friendly spacing, visible submit button, family age count validation, auto-scroll to report/errors, localStorage state persistence, and reused `user_id`.
- Numeric display format is `#,###,###.#` for money/percent report values and money input defaults.
- Asset input bottom navigation has been removed.
- Asset input page title is `자산/가족/수입/지출 현황`.
- Asset input page now shows `수정` and `저장` at the bottom first; `분석보고서 만들기` appears only after saving the form state.
- Started cogui-first rebuild from the beginning of the guideline.
- Smart diagnosis input now includes gender, residence region, job category, annual income, family composition, real estate type/count/current market value, loan info, deposits/installment savings, stocks/funds, pension/insurance, other assets, and short/mid/long-term goals.
- Personalized report now includes cogui pipeline, life-stage profile, region characteristics mapping, market data interface status, Korean action plans, sensible risk status, and net cashflow after monthly loan interest.
- Current local server is running on `http://localhost:8000/`.
- Verification passed with `python backend/tests/system_audit.py`.

## Working Rules

- Read this file before every task.
- Update this file after code changes.
- Preserve existing structure, naming, style, indentation, and scope.
- Modify only the user-requested area.
- Use web references for coding fixes when implementation details need verification.
