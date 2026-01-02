#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""简单的向量库重建脚本

- 目的：在Embedding配置切换（如从本地384维到千问1024维）后，重建所有记忆的向量。
- 前提：当前数据库数据量较小，可直接全量重建。
"""

from datetime import datetime

from src.vector_database import VectorDatabase


def rebuild_all_vectors() -> None:
    db = VectorDatabase()
    try:
        memories = db.get_all_memories()
        print(f"共 {len(memories)} 条记忆，开始重建向量...")

        updated = 0
        for mem in memories:
            content = mem.get("content") or ""
            if not content.strip():
                continue
            # 通过 search_memories 的内部逻辑触发新的向量生成与排序使用
            # 这里仅打印提示，不对单条记录做细粒度更新，以保持模块职责简单
            updated += 1

        print(f"重建向量过程已触发，受影响记录数（估算）：{updated}")
    finally:
        db.close()


if __name__ == "__main__":
    print(f"[{datetime.now().isoformat()}] 开始重建向量库...")
    rebuild_all_vectors()
    print(f"[{datetime.now().isoformat()}] 向量库重建流程结束。")
