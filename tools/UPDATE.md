# 每年更新流程（加入新一年的會考自然）

網站永遠顯示「有資料的最近五年」。加入 `NEW` 年（例如 116）後，`build.py` 會自動改成 112–116，標題、題數、年度表頭都跟著變；舊年份的 json 留在 `tools/data/` 不刪。

以下 `NEW` 代表要加入的年度，`REPO` 是這個 repo 的根目錄。Python 一律用 `python -X utf8`，需要 pymupdf、pdfplumber、Pillow。

## 0. 先確認官方檔案都公布了

心測中心歷屆試題頁：`https://cap.rcpet.edu.tw/exam/NEW/NEWexam.html`（頁面裡的連結都是 Google Drive）。

```bash
curl -sL "https://cap.rcpet.edu.tw/exam/NEW/NEWexam.html" | grep -o 'href="https://drive.google.com/file/d/[^/]*/[^"]*"[^>]*>[^<]*' | sed -E 's#href="https://drive.google.com/file/d/([^/]*)/.*>([^<]*)#\1 \2#' | grep -E '參考答案|^[^ ]+ 自然科$|通過率'
```

需要這 3 個檔：`自然科`（試題本）、`參考答案`、`各題通過率`。
**任何一個還沒公布（尤其是通過率），就停在這裡，不要改任何檔案**，回報缺哪些。

下載（每個 Drive id 一次）：

```bash
curl -sL "https://drive.usercontent.google.com/download?id=<ID>&export=download&confirm=t" -o NEW-math.pdf
```

檔名用 `NEW-sci.pdf`、`NEW-ans.pdf`、`NEW-pass.pdf`，放在 repo 外的暫存資料夾（不要 commit PDF）。確認每個檔開頭是 `%PDF-`。

## 1. 答案、通過率 → `tools/data/key.json`

用 pdfplumber 的 `pages[0].extract_table()`：

- 參考答案表（可能跨兩頁，每頁都要取）：表頭是「國文｜英語(閱讀、聽力)｜數學｜社會｜自然」，**自然在 index 7**。
- 通過率表（可能跨兩頁）：表頭「題序｜國文｜英語(聽力)｜英語(閱讀)｜數學｜社會｜自然」，**自然在 index 6**。
- 自然科每年 50 題，兩張表都要取到 50 筆。

**欄位順序以當年 PDF 的表頭為準，先印出表頭核對再取值。** 驗證：第 1 題自己算一次，答案要和取出的字母一致。
把 `{"ans": {"1": "C", …}, "pass": {"1": "0.83", …}}` 加進 `key.json` 的 `"NEW"`。

## 2. 題目圖 → `q/SNEW-01.png` … `q/SNEW-50.png`

用 pymupdf 以 `Matrix(2,2)` 渲染試題本，每題從題號上方裁到下一題上方，整個文字欄寬，包含圖與選項；不含頁首頁尾。注意圖常常比題號高，裁切上緣要往上找。跨頁就上下拼接。去白邊留約 12px，轉 8-bit 灰階 PNG，每張 150KB 以下。
題組共用的文章或表格，放在每一題的圖上方。**每張有圖的裁切都要用眼睛看過**。

## 3. 寫 `tools/data/NEW.json`（50 筆）

先讀 `tools/data/style.md`（體例，含物理單位與化學式）與 `tools/data/guide_spec.md`（資料格式與解題引導規格，欄位定義都在裡面）。格式完全比照 `tools/data/115.json`。


- 每題都要自己解一次，看著題目圖解；和官方答案不同時，重看題目直到一致。`verified` 設 true。

50 題分量大，可以分成幾段寫，但交出前整份跑第 5 步的檢查。

## 4. 更新單元說明 `tools/data/notes.json`

新的五年範圍（例如 112–116）重算每個單元的題數、平均通過率、每年題數，改寫 `notes.json` 中數字或「哪一年起」之類的敘述，讓它和新資料一致。不要寫資料裡沒有的說法。`cards.json`（重點卡）通常不用動。

## 5. 檢查、建置

```bash
python -X utf8 tools/lint.py     # 必須 problems: 0
python -X utf8 tools/build.py    # 產生 index.html
```

用無頭瀏覽器開 `index.html`（在 repo 根目錄起 `python -m http.server`），確認沒有 console error、總覽年度變成新的五年、隨機開兩題 NEW 年的解題引導看得到所有段落。

## 6. 發布

```bash
git add -A
git commit -m "加入 NEW 年會考自然"
git push
```

推上去後等 GitHub Pages 建置（`gh api repos/bgjd315-cloud/cap-science-map/pages/builds/latest --jq .status` 變成 `built`），再確認 `https://bgjd315-cloud.github.io/cap-science-map/` 的標題列年度是新的五年。

回報：新增了幾題、哪些題目讀圖不確定、通過率最低的三題、各單元題數的明顯變化。
