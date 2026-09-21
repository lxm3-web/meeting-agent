# meeting-agent — 會議追蹤專員（Agent 版）

claude.ai/code 選這個 repo（或本機 `claude`）→ 說「週會記錄在 inbox，幫我更新待辦」→ 更新後的待辦表、給總經理的摘要、一人一則交辦通知、逾期提醒、待釐清清單寫到 `outbox/` → 看完說「好，發下去」。

公司、人物、會議內容皆虛構。**demo 完歸零**：`inbox/*.done` 改回 `.txt`、清 `outbox/`、`data/待辦追蹤.csv` 換回 `data/待辦追蹤_原始.csv`、log 只留表頭。
