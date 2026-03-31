"""Playground 生成器 API v1

核心功能：
- POST /api/playground/generate - 触发 Playground 生成
- GET /api/playground/html/{task_id} - 获取生成的 HTML
- GET /api/playground/sse/{task_id} - SSE 进度流

流程：
1. 前端 POST 项目数据 → 生成 task_id
2. 后台调用 generate_playground.py 生成 HTML
3. 前端 SSE 订阅进度
4. 生成完成后前端获取 HTML 并预览
"""

import uuid
import json
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel, Field

log = logging.getLogger("cyberteam.playground")

router = APIRouter(prefix="/playground", tags=["playground v1"])


# === Request/Response Models ===

class PlaygroundRequest(BaseModel):
    """Playground 生成请求。"""
    project_name: str = Field(..., description="项目名称")
    project_date: str = Field(..., description="项目日期")
    funnel: dict[str, int] = Field(default_factory=dict, description="漏斗数据")
    channels: dict[str, dict] = Field(default_factory=dict, description="渠道配置")
    budget: float = Field(default=0, description="总预算")
    risk_level: str = Field(default="中等", description="风险等级")
    notes: Optional[str] = Field(default="", description="备注")


class PlaygroundResponse(BaseModel):
    """生成响应。"""
    task_id: str


# === 内存存储 ===

# 存储生成状态和结果
_generation_status: dict[str, dict] = {}
_generated_html: dict[str, str] = {}


# === 后台生成任务 ===

async def _run_playground_generator(
    task_id: str,
    project_name: str,
    project_date: str,
    funnel: dict,
    channels: dict,
    budget: float,
    risk_level: str,
    notes: str,
) -> None:
    """后台运行 Playground 生成脚本。"""
    _generation_status[task_id] = {
        "status": "running",
        "step": "初始化...",
        "percent": 0,
        "started_at": datetime.now().isoformat(),
    }

    try:
        # 1. 查找 generate_playground.py 脚本
        # 优先从项目目录查找（项目内自带的生成器）
        base_dir = Path(__file__).parent.parent.parent.parent  # backend/app/api/v1/ -> cyberteam-v4/
        projects_root = base_dir / "projects"

        # 查找匹配的项目目录
        matched_dir = None
        for candidate in projects_root.iterdir():
            if candidate.is_dir() and not candidate.name.startswith("_"):
                if candidate.name.startswith(project_name) or project_name in candidate.name:
                    matched_dir = candidate
                    break

        if matched_dir:
            generator_script = matched_dir / "05_Playground" / "generate_playground.py"
            template_html = matched_dir / "05_Playground" / "活动看板_v8.html"
            output_file = matched_dir / "05_Playground" / f"活动看板_{project_name}.html"

            if generator_script.exists():
                _generation_status[task_id] = {
                    "status": "running",
                    "step": "正在调用生成脚本...",
                    "percent": 20,
                    "started_at": _generation_status[task_id]["started_at"],
                }

                # 调用生成脚本
                import subprocess
                result = subprocess.run(
                    ["python3", str(generator_script), "--project", str(matched_dir)],
                    capture_output=True,
                    text=True,
                    timeout=60,
                )

                if result.returncode == 0:
                    _generation_status[task_id] = {
                        "status": "running",
                        "step": "生成完成，准备输出...",
                        "percent": 90,
                        "started_at": _generation_status[task_id]["started_at"],
                    }

                    # 读取生成的 HTML
                    if output_file.exists():
                        html_content = output_file.read_text(encoding="utf-8")
                        _generated_html[task_id] = html_content
                    elif template_html.exists():
                        # fallback: 返回模板 HTML
                        _generated_html[task_id] = template_html.read_text(encoding="utf-8")
                else:
                    log.error(f"[Playground] 生成失败: {result.stderr[:500]}")
                    _generation_status[task_id] = {
                        "status": "error",
                        "step": f"脚本执行失败: {result.stderr[:200]}",
                        "percent": 0,
                        "started_at": _generation_status[task_id]["started_at"],
                        "error": result.stderr[:500],
                    }
                    return
            else:
                # 没有生成脚本，生成默认 HTML
                _generation_status[task_id] = {
                    "status": "running",
                    "step": "生成默认 Playground...",
                    "percent": 50,
                    "started_at": _generation_status[task_id]["started_at"],
                }
                _generated_html[task_id] = _generate_default_html(
                    project_name, project_date, funnel, channels, budget, risk_level, notes
                )
        else:
            # 没找到项目目录，生成默认 HTML
            _generation_status[task_id] = {
                "status": "running",
                "step": "生成默认 Playground...",
                "percent": 50,
                "started_at": _generation_status[task_id]["started_at"],
            }
            _generated_html[task_id] = _generate_default_html(
                project_name, project_date, funnel, channels, budget, risk_level, notes
            )

        _generation_status[task_id] = {
            "status": "completed",
            "step": "完成",
            "percent": 100,
            "started_at": _generation_status[task_id]["started_at"],
            "completed_at": datetime.now().isoformat(),
        }

        log.info(f"[Playground] 生成完成: task_id={task_id}, project={project_name}")

    except subprocess.TimeoutExpired:
        _generation_status[task_id] = {
            "status": "error",
            "step": "生成超时（60s）",
            "percent": 0,
            "started_at": _generation_status[task_id]["started_at"],
            "error": "生成超时",
        }
    except Exception as e:
        log.exception(f"[Playground] 生成异常: task_id={task_id}")
        _generation_status[task_id] = {
            "status": "error",
            "step": f"异常: {str(e)[:100]}",
            "percent": 0,
            "started_at": _generation_status[task_id]["started_at"],
            "error": str(e),
        }


def _generate_default_html(
    project_name: str,
    project_date: str,
    funnel: dict,
    channels: dict,
    budget: float,
    risk_level: str,
    notes: str,
) -> str:
    """生成默认的 Playground HTML。"""
    # 漏斗数据
    曝光 = funnel.get("曝光", 0)
    点击 = funnel.get("点击", 0)
    注册 = funnel.get("注册", 0)
    成交 = funnel.get("成交", 0)
    点击率 = (点击 / 曝光 * 100) if 曝光 > 0 else 0
    注册率 = (注册 / 点击 * 100) if 点击 > 0 else 0
    成交率 = (成交 / 注册 * 100) if 注册 > 0 else 0
    总转化率 = (成交 / 曝光 * 100) if 曝光 > 0 else 0

    # 渠道汇总
    total_cost = sum(c.get("成本", 0) for c in channels.values())
    avg_roi = sum(c.get("ROI", 0) for c in channels.values()) / len(channels) if channels else 0

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>活动看板 - {project_name}</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f0f2f5; padding: 20px; }}
.container {{ max-width: 1200px; margin: 0 auto; }}
.header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 24px; border-radius: 12px; margin-bottom: 20px; }}
.header h1 {{ font-size: 24px; margin-bottom: 8px; }}
.header p {{ opacity: 0.9; font-size: 14px; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px; margin-bottom: 20px; }}
.card {{ background: white; border-radius: 12px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
.card h3 {{ font-size: 14px; color: #666; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 1px; }}
.metric {{ font-size: 32px; font-weight: bold; color: #333; margin-bottom: 4px; }}
.metric-label {{ font-size: 12px; color: #999; }}
.funnel {{ display: flex; flex-direction: column; align-items: center; gap: 8px; }}
.funnel-stage {{ background: #667eea; color: white; padding: 12px 24px; border-radius: 8px; text-align: center; width: 100%; }}
.funnel-arrow {{ color: #667eea; font-size: 20px; }}
.funnel-rate {{ font-size: 12px; color: #999; margin-top: 4px; }}
.channel-item {{ display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid #f0f0f0; }}
.channel-item:last-child {{ border-bottom: none; }}
.channel-name {{ font-weight: 500; }}
.channel-stats {{ display: flex; gap: 16px; font-size: 13px; color: #666; }}
.budget-bar {{ height: 8px; background: #f0f0f0; border-radius: 4px; overflow: hidden; margin-top: 8px; }}
.budget-fill {{ height: 100%; background: linear-gradient(90deg, #667eea, #764ba2); border-radius: 4px; transition: width 0.3s; }}
.notes {{ background: #f5f5f5; padding: 16px; border-radius: 8px; font-size: 14px; color: #666; line-height: 1.6; }}
.risk-tag {{ display: inline-block; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 500; }}
.risk-low {{ background: #d4edda; color: #155724; }}
.risk-medium {{ background: #fff3cd; color: #856404; }}
.risk-high {{ background: #f8d7da; color: #721c24; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>{project_name}</h1>
    <p>项目日期: {project_date} | 风险等级: <span class="risk-tag risk-{'low' if risk_level == '低' else 'medium' if risk_level == '中等' else 'high'}">{risk_level}</span></p>
  </div>

  <div class="grid">
    <div class="card">
      <h3>总曝光</h3>
      <div class="metric">{曝光:,.0f}</div>
      <div class="metric-label">全渠道累计</div>
    </div>
    <div class="card">
      <h3>总成交</h3>
      <div class="metric">{成交:,.0f}</div>
      <div class="metric-label">总体转化率: {总转化率:.4f}%</div>
    </div>
    <div class="card">
      <h3>总成本</h3>
      <div class="metric">{total_cost:,.0f}元</div>
      <div class="metric-label">平均 ROI: {avg_roi:.2f}x</div>
    </div>
    <div class="card">
      <h3>预算使用</h3>
      <div class="metric">{budget:,.0f}元</div>
      <div class="budget-bar"><div class="budget-fill" style="width: {min(total_cost/budget*100, 100) if budget > 0 else 0}%"></div></div>
    </div>
  </div>

  <div class="grid">
    <div class="card">
      <h3>转化漏斗</h3>
      <div class="funnel">
        <div class="funnel-stage">曝光 {曝光:,.0f}</div>
        <div class="funnel-arrow">↓</div>
        <div class="funnel-stage">点击 {点击:,.0f} <span class="funnel-rate">({点击率:.2f}%)</span></div>
        <div class="funnel-arrow">↓</div>
        <div class="funnel-stage">注册 {注册:,.0f} <span class="funnel-rate">({注册率:.2f}%)</span></div>
        <div class="funnel-arrow">↓</div>
        <div class="funnel-stage">成交 {成交:,.0f} <span class="funnel-rate">({成交率:.2f}%)</span></div>
      </div>
    </div>

    <div class="card">
      <h3>渠道详情</h3>
      <div class="channel-list">
        {''.join(f'''
        <div class="channel-item">
          <span class="channel-name">{ch}</span>
          <div class="channel-stats">
            <span>曝光: {c.get("曝光", 0):,}</span>
            <span>成本: {c.get("成本", 0):,}元</span>
            <span style="color: {'#52c41a' if c.get("ROI", 0) >= 3 else '#faad14'}">ROI: {c.get("ROI", 0):.1f}x</span>
          </div>
        </div>''' for ch, c in channels.items())}
      </div>
    </div>
  </div>

  <div class="card">
    <h3>备注</h3>
    <div class="notes">{notes or '暂无备注'}</div>
  </div>
</div>
</body>
</html>"""


# === Routes ===

@router.post("/generate", response_model=PlaygroundResponse)
async def generate_playground(req: PlaygroundRequest, background_tasks: BackgroundTasks):
    """触发 Playground 生成。

    后台运行生成脚本，生成了 HTML 后存入内存。
    前端通过 SSE 订阅进度，完成后通过 /html/{task_id} 获取结果。
    """
    task_id = str(uuid.uuid4())[:8]

    # 立即返回 task_id
    background_tasks.add_task(
        _run_playground_generator,
        task_id,
        req.project_name,
        req.project_date,
        req.funnel,
        req.channels,
        req.budget,
        req.risk_level,
        req.notes or "",
    )

    return PlaygroundResponse(task_id=task_id)


@router.get("/html/{task_id}")
async def get_playground_html(task_id: str):
    """获取生成的 HTML 内容。"""
    # 先查状态
    status_info = _generation_status.get(task_id, {})
    gen_status = status_info.get("status", "")

    if gen_status == "error":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"生成失败: {status_info.get('error', 'unknown')}",
        )

    if gen_status == "running":
        return {"error": "still_running", "step": status_info.get("step", "生成中...")}

    html = _generated_html.get(task_id)
    if not html:
        return {"error": "not_found"}

    return HTMLResponse(content=html)


@router.get("/sse/{task_id}")
async def playground_sse(task_id: str):
    """SSE 进度流。

    事件类型：
    - progress: { "step": "xxx", "percent": 50 }
    - complete: { "html": "..." }
    - error: { "message": "xxx" }
    - done: (无数据，表示流结束)
    """
    async def event_generator():
        try:
            while True:
                status_info = _generation_status.get(task_id, {})
                gen_status = status_info.get("status", "")

                if gen_status == "completed":
                    html = _generated_html.get(task_id, "")
                    yield f"data: {json.dumps({'type': 'complete', 'html': html}, ensure_ascii=False)}\n\n"
                    break

                elif gen_status == "error":
                    yield f"data: {json.dumps({'type': 'error', 'message': status_info.get('error', '生成失败')}, ensure_ascii=False)}\n\n"
                    break

                elif gen_status == "running":
                    yield f"data: {json.dumps({'type': 'progress', 'step': status_info.get('step', '生成中...'), 'percent': status_info.get('percent', 0)}, ensure_ascii=False)}\n\n"

                await asyncio.sleep(0.5)

            yield "data: [DONE]\n\n"

        except Exception as e:
            log.exception(f"[Playground SSE] task_id={task_id}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
