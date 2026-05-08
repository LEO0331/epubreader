# Book QA Library 系統設計深度評審（繁體中文）

## 1) 範圍與目標
- 建立以本地優先（local-first）為核心、具可追溯證據的書籍問答系統（EPUB/PDF/HTML 類來源）。
- 在沒有 LLM/API provider 的情況下，仍可使用 parser-only 模式。
- 讓 ingest 到 query 的流程可檢視、可測試，且在可行情況下具備可續跑能力。
- 保留來源可追蹤性：所有回答都必須有檢索到的 chunk 證據。

目前非目標：
- 多租戶驗證/計費。
- 雲端分散式工作佇列基礎建設。
- 即時協作編輯。

## 2) 高階架構
分層如下：
1. API 層（`apps/api/routes/*`）：薄路由，負責 HTTP 介面與 schema。
2. Service 層（`packages/services` 與 parsing/chunking/generation/query 服務）：業務流程協調。
3. Repository 層（`packages/storage/repositories/*`）：儲存存取與查詢封裝。
4. Domain/Model 層（`packages/core/models/*`、enums/settings）：型別邊界與核心資料模型。
5. 處理模組：
   - ingest adapters（`packages/ingest/adapters/*`）
   - parsers（`packages/parsing/*`）
   - cleaning（`packages/cleaning/*`）
   - chunking（`packages/chunking/*`）
   - generation（`packages/generation/*`）
   - indexing/retrieval（`packages/indexing/*`, `packages/query/*`）
   - exporters（`packages/exporters/*`）
6. 儲存：
   - 關聯式 metadata（SQLite + SQLAlchemy/Alembic）。
   - 本地檔案 artifacts（`data/raw`, `data/normalized`, `data/artifacts`, `data/exports`）。
   - 向量儲存（Chroma persistent path）。

為何這樣切：
- Route 保持精簡，業務邏輯可單元測試。
- parser/chunker/index/query 可獨立演進，不需頻繁改 API route。
- 保持本地可部署、低基礎設施負擔。

## 3) 端到端資料流
1. ingest（`/api/v1/ingest/url|upload`）建立 `Book` + `Job`，並保存 raw snapshot。
2. parsing service 依 source type 選 parser（EPUB/HTML/PDF），落地 `parsed.json` 與 `Section` 資料列。
3. cleaning 對 section 做決定性（deterministic）正規化，保存 cleaned artifact。
4. chunking 建立含 metadata 的穩定 chunks；弱結構時使用語意 fallback 拆分。
5. 可選 generation 產出 summary/wiki/qa/skill artifacts。
6. 可選 indexing 將 chunks embedding 後寫入 Chroma。
7. query 先檢索證據 chunk，再合成含 citations 的答案。
8. collections + export 將結果打包到 filesystem/Obsidian/GitHub。

## 4) 核心資料結構選擇與原因

### 4.1 Book/Section/Chunk 正規化階層
採用：
- `Book`（來源實體）
- `Section`（有序結構單元）
- `Chunk`（檢索單元，帶來源 metadata）

原因：
- 符合文件自然層級。
- 可從 sections 決定性重建 chunks。
- 支援證據追溯（book -> section -> chunk -> citation）。

替代方案：
- 只用扁平 paragraph table：
  - 寫入較簡單，但會削弱結構與 heading-aware chunking。
- 圖形文件模型（graph）：
  - 彈性高，但本地 MVP 複雜度過高。

### 4.2 關聯式 metadata（SQLite + SQLAlchemy）
採用：
- SQLite（本地可攜、零運維）。
- SQLAlchemy repository（型別化持久層邊界）。

原因：
- 本地開發與測試成本低。
- 單機 metadata 一致性足夠。
- Alembic migration 成熟。

替代方案：
- 一開始就用 Postgres：
  - 併發與擴展性較好，但部署成本較高。
- NoSQL 文件庫：
  - schema 彈性高，但 jobs/books/chunks 關聯約束較弱。

### 4.3 檔案系統 artifact 儲存
採用：
- 大型原始/衍生內容放在 `data/*`，DB 存路徑與 metadata。

原因：
- 避免 DB 膨脹。
- 人工除錯與審查方便。
- 本地持久化直覺且成本低。

替代方案：
- 全部放 DB BLOB：
  - 交易一致性好，但 DB 體積與操作負擔大。
- 全部走物件儲存：
  - 雲端擴展佳，但不符合 local-first/offline 方向。

### 4.4 Chroma 本地持久向量庫
採用：
- 使用 Chroma collection 管理 book 向量索引。

原因：
- 本地向量持久化摩擦低。
- 搭配本地 embedding provider 容易。
- 支援 retrieval preview 與範圍查詢。

替代方案：
- FAISS 索引檔：
  - 速度快，但 metadata/filtering 使用體驗較弱。
- Postgres pgvector：
  - 生產型方案好，但 MVP 本地設置成本較高。

### 4.5 Job 狀態機（明確生命週期）
採用：
- `Job` 狀態轉換（`create -> start -> advance -> finish/fail`）。

原因：
- 每步可追蹤、可稽核。
- 比散落旗標更可觀測。
- 保留未來續跑/重試擴展空間。

替代方案：
- 同步一次跑到底：
  - 簡單但失敗診斷差、缺乏 checkpoint。
- 直接上 Celery/RQ：
  - 擴展性高，但本地 MVP 基建過重。

### 4.6 Adapter registry + parser dispatch
採用：
- adapter 合約（`can_handle/fetch/extract_metadata/snapshot`）與 parser 路由。

原因：
- 將來源抓取與內容解析解耦。
- 新來源可擴充，不破壞既有 API。

替代方案：
- 單一 ingest 類別大量 if/else：
  - 初期快，後期難維護。

### 4.7 OCR fallback 策略（先文字再 OCR）
採用：
- 先做 native PDF text extraction；低文字量頁面才做 OCR。

原因：
- 對可抽文字 PDF 成本低、速度快。
- 掃描 PDF 仍可覆蓋。
- OCR runtime 缺失時可優雅降級。

替代方案：
- 每頁都 OCR：
  - 一致性高，但耗時與資源成本大。
- 雲端 OCR API：
  - 可能品質更高，但增加隱私/成本/供應商綁定風險。

### 4.8 Export profile（`basic|enhanced`）
採用：
- 在既有 export request 增加向後相容 profile。

原因：
- 不破壞舊客戶端。
- 可 opt-in 啟用 Obsidian frontmatter/tags/media 處理。

替代方案：
- 每種格式拆獨立 endpoint：
  - 介面清楚但 API 面積擴大、重複邏輯增加。

## 5) 主要架構取捨

### 簡單性 vs 可擴展性
- 目前優先本地可運行與低維運。
- 代價：水平擴展與高併發能力有限。

### 決定性流程 vs 模型智慧
- cleaning/chunking 先決定性，generation 再引入模型。
- 代價：語意細節可能較少，但可測試與可除錯性高。

### 可追溯性 vs 儲存體積
- 詳細 metadata + artifacts 會增加儲存量。
- 收益：citation 可信度與問題追查能力更強。

### 延遲 vs 回答品質
- 先檢索再作答能降 hallucination。
- 代價：額外檢索與 citation 組裝時間。

## 6) 可靠性與安全設計重點
- Request ID middleware + 穩定 JSON 錯誤格式。
- API key middleware（非 local 環境可強制）。
- URL ingest 防護（SSRF/大小限制）。
- Export path 安全檢查（限制在控制目錄內）。
- OCR 防護（頁數/時間限制，可選 worker 隔離）。

## 7) 下一階段可選替代路徑
1. Metadata DB：SQLite -> Postgres（多並發）。
2. 作業執行：維持 `JobService` 合約，底層改 queue worker。
3. 檢索：混合 BM25 + vector 提升 recall。
4. 模型路由：provider-aware policy fallback。
5. 儲存：增加 object storage adapter。

## 8) 深入追問題庫（附答題重點）

Q1. 為什麼不只把全文放向量庫，省略 sections/chunks table？
- 向量庫是檢索層，不該作為正規來源。需要獨立的可追溯 lineage、可重建流程、可檢視 API，不可綁死在單一索引實作。

Q2. 為什麼 query 一定要先有檢索證據？
- 這是 grounded QA 核心約束，能顯著降低幻覺並提供可稽核 citations。

Q3. 為什麼 DB + 檔案系統雙軌？
- DB 適合狀態與查詢，檔案系統適合大 payload 與人工檢視；兩者互補。

Q4. 沒 API key 時 parser mode 為何仍有價值？
- ingest/parse/clean/chunk 都是本地可運行決定性流程，可先完成資料整備與品質檢查。

Q5. 為何現在不直接上完整 async queue？
- MVP 目標是低門檻與低維運。先用 Job 狀態機保留擴展接口，後續再替換執行層。

Q6. 如何避免 source-specific 解析邏輯失控？
- 透過 adapter 與 parser 模組化隔離責任，新增來源只擴充模組，不改核心路由合約。

Q7. PDF OCR 成本如何控管？
- 文字優先、低文字閾值觸發 OCR、頁級與總時限、可設頁數上限、OCR 不可用時降級。

Q8. chunking 策略調整會有何影響？
- 相同輸入與相同策略下維持穩定 ID；策略升級應版本化並搭配重建 chunk/index 流程。

Q9. 為何當前選 Chroma 而非 pgvector？
- 本地持久化與部署摩擦更低；pgvector 是後續生產化升級選項。

Q10. 目前最大架構風險？
- 雲端 ephemeral 環境下本地檔案耦合、單節點 DB 併發限制、以及模型供應商輸出波動。

## 9) 建議 Deep Dive 討論流程
1. Domain 模型（`Book/Section/Chunk/Job/Collection`）逐層走讀。
2. adapter 與 parser orchestration 決策路徑。
3. chunk metadata 保證與 fallback 規則。
4. retrieval + citation 合約與失敗模式。
5. export profiles 與 media/path 安全策略。
6. 未來硬化路線（queue、DB 遷移、hybrid retrieval）。
