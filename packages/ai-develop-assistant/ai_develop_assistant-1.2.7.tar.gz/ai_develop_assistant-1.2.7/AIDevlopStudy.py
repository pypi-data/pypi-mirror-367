"""
MCP Server - AI需求分析和设计助手
协助AI初级开发者完善需求分析和架构设计

包含三个核心工具：
1. requirement_clarifier - 需求澄清助手
2. requirement_manager - 需求文档管理器  
3. architecture_designer - 架构设计生成器
"""

import logging
import os
import json
from typing import Any, Dict, List, Union
from datetime import datetime
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from mcp.types import Tool, TextContent, Resource

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("StudyAIDevelop")

# 配置存储目录
def get_storage_dir():
    """获取存储目录，优先使用环境变量配置"""
    env_dir = os.getenv("MCP_STORAGE_DIR", "./mcp_data")
    storage_dir = Path(env_dir)
    storage_dir.mkdir(exist_ok=True)
    return storage_dir

# 全局需求文档存储
current_requirements = {
    "project_overview": [],
    "functional_requirements": [],
    "technical_requirements": [],
    "design_requirements": "",
    "deployment_requirements": [],
    "ai_constraints": [],
    "clarification_history": [],
    "architecture_designs": [],
    "last_updated": None,
    "project_id": None,
    "branch_status": {}  # 分支完成状态跟踪
}
final_markdown_content = ""
# 存储管理类
class RequirementStorage:
    def __init__(self):
        self.storage_dir = get_storage_dir()
        self.requirements_file = self.storage_dir / "requirements.json"
        self.history_file = self.storage_dir / "history.json"
        self.load_requirements()

    def load_requirements(self):
        """加载已保存的需求文档"""
        global current_requirements
        try:
            if self.requirements_file.exists():
                with open(self.requirements_file, 'r', encoding='utf-8') as f:
                    saved_data = json.load(f)
                    current_requirements.update(saved_data)
                logger.info(f"✅ 已加载需求文档: {self.requirements_file}")
        except Exception as e:
            logger.warning(f"⚠️ 加载需求文档失败: {e}")

    def save_requirements(self):
        """保存需求文档到文件"""
        try:
            current_requirements["last_updated"] = datetime.now().isoformat()
            with open(self.requirements_file, 'w', encoding='utf-8') as f:
                json.dump(current_requirements, f, ensure_ascii=False, indent=2)
            logger.info(f"✅ 需求文档已保存: {self.requirements_file}")
        except Exception as e:
            logger.error(f"❌ 保存需求文档失败: {e}")

    

    def export_final_document(self):
        """导出最终的完整需求和架构文档"""
        try:
            final_doc = {
                "project_summary": {
                    "generated_at": datetime.now().isoformat(),
                    "project_id": current_requirements.get("project_id"),
                    "last_updated": current_requirements.get("last_updated")
                },
                "requirements": current_requirements,
                "export_format": "markdown"
            }

            export_file = self.storage_dir / f"final_document_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(final_doc, f, ensure_ascii=False, indent=2)

            # 同时生成Markdown格式
            md_file = self.storage_dir / f"final_document_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            self.generate_markdown_report(md_file)

            logger.info(f"✅ 最终文档已导出: {export_file}")
            return str(export_file)
        except Exception as e:
            logger.error(f"❌ 导出最终文档失败: {e}")
            return None

    def generate_markdown_report(self, md_file: Path):
        """生成Markdown格式的报告"""
        try:
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write("# 🚀 AI开发项目需求与架构文档\n\n")
                f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

                # 项目概述
                if current_requirements.get("project_overview"):
                    f.write("## 📋 项目概述\n\n")
                    for item in current_requirements["project_overview"]:
                        f.write(f"- {item}\n")
                    f.write("\n")

                # 功能需求
                if current_requirements.get("functional_requirements"):
                    f.write("## ⚙️ 功能需求\n\n")
                    for item in current_requirements["functional_requirements"]:
                        f.write(f"- {item}\n")
                    f.write("\n")

                # 技术需求
                if current_requirements.get("technical_requirements"):
                    f.write("## 🔧 技术需求\n\n")
                    for item in current_requirements["technical_requirements"]:
                        f.write(f"- {item}\n")
                    f.write("\n")

                # 架构设计
                if current_requirements.get("architecture_designs"):
                    f.write("## 🏗️ 架构设计\n\n")
                    for design in current_requirements["architecture_designs"]:
                        f.write(f"{design}\n\n")

                # 澄清历史
                if current_requirements.get("clarification_history"):
                    f.write("## 📝 需求澄清历史\n\n")
                    for item in current_requirements["clarification_history"]:
                        f.write(f"- {item}\n")
                    f.write("\n")

            logger.info(f"✅ Markdown报告已生成: {md_file}")
        except Exception as e:
            logger.error(f"❌ 生成Markdown报告失败: {e}")

# 初始化存储管理器
storage = RequirementStorage()

  

# 新增的、作为唯一流程起点的工具
@mcp.tool()
def start_new_project(user_request: str) -> str:
    """
    (最终起点) 开始一个全新的项目。
    此工具会彻底重置所有状态，然后为新需求创建蓝图。
    """
    global current_requirements
    
    logger.info(f"🚀 接到新项目启动指令: {user_request}")
    logger.info("🧹 开始重置系统状态...")

    # 1. 彻底重置内存中的全局变量
    current_requirements = {
        "project_overview": [], "functional_requirements": [], "technical_requirements": [],
        "design_requirements": "", "deployment_requirements": [], "ai_constraints": [],
        "clarification_history": [], "architecture_designs": [], "data_model_design": [],
        "mobile_specifics": [], "project_governance": [], "smart_contract_design": [],
        "wallet_integration": [], "off_chain_services": [], "frontend_interaction": [],
        "security_audit": [], "last_updated": None, "project_id": None, "branch_status": {}
    }
    logger.info("✅ 内存状态已重置。")

    # 2. 删除旧的持久化文件
    try:
        if storage.requirements_file.exists():
            os.remove(storage.requirements_file)
            logger.info(f"✅ 已删除旧的需求文件: {storage.requirements_file}")
        if storage.history_file.exists():
            os.remove(storage.history_file)
            logger.info(f"✅ 已删除旧的历史文件: {storage.history_file}")
    except Exception as e:
        logger.error(f"❌ 清理旧文件时出错: {e}")
        return f"# ❌ 项目启动失败\n\n在清理旧项目文件时发生错误: {e}"

    logger.info("✅ 系统状态已完全重置，准备创建新蓝图...")
    
    # 3. 内部调用蓝图创建的核心逻辑
    try:
        # # 主控AI不直接调用create_requirement_blueprint，而是由启动工具封装调用
        report = create_requirement_blueprint(user_request)
        return f"# 🎉 新项目已启动！\n\n{report}"
    except Exception as e:
        return f"# ❌ 项目启动失败\n\n在为您创建新项目蓝图时发生错误: {e}"
# ==============================================================================
# 1. 【全新职责】的工具：create_requirement_blueprint
#    职责：只作为“首席架构师”提示词模板的提供者。
# ==============================================================================
@mcp.tool()
def create_requirement_blueprint(user_request: str) -> str:
    """
    (模板提供者) 返回用于创建需求蓝图的、专家级的提示词模板。
    """
    logger.info(f"为请求'{user_request}'提供了需求蓝图的提示词模板。")
    
    # 这个函数现在唯一的职责就是构建并返回这个强大的Prompt
    prompt_template = f"""
    # 角色与任务
    你现在是主控AI，请立即代入世界顶级CTO和首席产品经理的角色。你的当前任务是分析用户的初始请求，并生成一个全面、专业的“需求蓝图”JSON对象然后调用requirement_manager工具进行保存，不需要返回给用户。

    # 用户的原始请求
    "{user_request}"

    # 你的分析与规划指令
    1.  **识别项目类型**: 分析请求，识别其核心类型 (例如：SaaS平台, 数据分析工具, 社交App, AI机器人, 物联网, Web3 DApp等)。
    2.  **规划核心分支**: 基于识别出的项目类型，规划出所有必须澄清的关键需求分支。你的规划必须体现专业性，主动思考结合用户需求多维度深度分析（不限于以下示例）：
        - `user_personas_and_journeys` (用户画像与核心旅程)
        - `core_functional_modules` (核心功能模块拆解)
        - `data_model_and_storage` (数据模型与存储方案)
        - `technology_stack_and_non_functional` (技术栈选型与非功能性需求)
        - `ui_ux_design_principles` (UI/UX设计原则)
    3.  **严格的输出格式**: 你必须且只能输出一个格式完全正确的JSON对象，绝对不能包含任何诸如“好的，这是您要的...”之类的解释性文字或代码块标记。
    4.  **当一个工具的输出是作为另一个工具的输入时，你应在后台静默完成调用，无需在对话中展示中间结果（如JSON字符串）（此工具不需要输出给用户展示，直接将json按照要求保存更新即可）。
    # JSON输出格式定义
    {{
      "project_title": "string",
      "status": "CLARIFYING",
      "checklist": [
        {{
          "branch_name": "string",
          "storage_key": "string",
          "status": "pending"
        }}
      ]
    }}
    """
    return prompt_template

# 需求澄清助手工具
# ==============================================================================
# 【新增/替换】 访谈专家 - 提示词提供者
# ==============================================================================
@mcp.tool()
def requirement_clarifier(branch_name_to_clarify: str, project_title: str) -> str:
    """
    (模板提供者) 针对单个分支，返回用于生成“问题清单”的专家级提示词模板。
    """
    logger.info(f"为分支'{branch_name_to_clarify}'提供了问题清单的提示词模板。")
    
    prompt_template = f"""
    # 角色与任务
    你现在是主控AI，请立即代入资深用户访谈专家的角色。你的任务是针对一个具体的需求分支，设计出一系列能够彻底澄清所有细节的、结构化的问题清单，不需要返回给用户json、字典等，直接按照下方要求保存即可

    # 背景
    我们正在澄清项目“{project_title}”的“{branch_name_to_clarify}”分支。

    # 你的分析与规划指令
    1.  **拆解分支**: 将“{branch_name_to_clarify}”这个宏观概念，拆解成专业的3-5个完成需求必须被回答的具体子问题。使用save_clarification_tasks工具保存
    
    2.  **严格的保存格式**: 你必须且只能保存一个格式完全正确的JSON对象，绝对不能包含任何解释性文字或代码块标记以及未经过用户确认认可的建议。
    3.  **经过用户澄清后的调用要求**:在不确定用户授权范围前永远默认只能更新或者保存经过用户确认的单分支或者当前分支的一个或者多个问题，只有用户确定后的问题才可以修改此问题的状态status:'pending' -> 'completed'。
    4.  **提供专业建议**: 针对你提出的每一个子问题，都返回给用户一个简洁、专业、符合行业最佳实践的建议用来引导用户。
    5.  **行为准则: “你必须严格遵守最小权限原则。当用户授予你自主决策权时（如‘你决定’、‘常规方案’等），该授权仅限于当前正在讨论的、最具体的一个分支的一个或多个问题。你绝对禁止将此授权泛化到任何其他未开始澄清分支或正在进行中的分支中的其他未确定问题上。收得到类似指令时必须询问用户用户授权的是当前分支还是分支内的此问题还是所有分支”
    6.  **询问用户，用户回答前不允许有任何动作。用户明确回答“剩余分支都由你来决策”之后你必须严格遵循以下循环算法，绝对禁止跳过任何一步：

        从所有分支中，筛选出所有status为pending的分支列表。
        For 循环：从该列表的第一个分支开始，逐一遍历。
        对于循环中的每一个分支，你必须：
        执行针对当前分支生成3-5个生成需求必须被回答的专业化具体子问题。然后save_clarification_tasks工具保存。然后更新状态status；'pending' -> 'completed'。
        循环直到列表为空。在完成所有待办分支之前，绝对禁止进行下一步（如检查架构前提）。”

    # JSON输出格式定义（单个分支单个问题格式，实际列表长度根据要求生成对应数量的问题）
    {{
      "branch_name": "{branch_name_to_clarify}",
      "clarification_tasks": [
        {{
          "question_id": "string (例如: FUNC_Q1)",
          "question_text": "string (具体的问题)",
          "ai_suggestion": "",
          "status": "pending",
          "user_answer": null
        }}
      ]
    }}
    """
    return prompt_template
# ==============================================================================
# 【新增】 访谈专家 - 结果保存器
# ==============================================================================
@mcp.tool()
def save_clarification_tasks(branch_storage_key: str, tasks_data: Union[str, dict]) -> str:
    """ 1.生成某个分支的问题清单 2.更新某个分支某些问题的澄清结果(字典或JSON字符串)保存到指定分支。"""
    try:
        tasks_obj = {}
        if isinstance(tasks_data, dict):
            tasks_obj = tasks_data
        elif isinstance(tasks_data, str):
            tasks_obj = json.loads(tasks_data)
        else:
            raise TypeError(f"不支持的tasks_data类型: {type(tasks_data)}")

        if "requirement_blueprint" in current_requirements:
            for branch in current_requirements["requirement_blueprint"]["checklist"]:
                if branch["storage_key"] == branch_storage_key:
                    branch["clarification_tasks"] = tasks_obj.get("clarification_tasks", [])
                    storage.save_requirements()
                    return f"✅ 分支 '{tasks_obj.get('branch_name')}' 的澄清任务已规划完毕。"
        raise ValueError(f"在蓝图中未找到指定的storage_key: {branch_storage_key}")
    except Exception as e:
        return f"# ❌ 保存任务清单失败: {e}"

# ==============================================================================
# 【新增】状态更新工具：update_branch_status
# ==============================================================================
@mcp.tool()
def update_branch_status(branch_storage_key: str, status: str) -> str:
    """
    (状态更新器) 更新需求蓝图中指定分支的状态 (例如: 'pending' -> 'completed')。
    """
    global current_requirements
    try:
        if "requirement_blueprint" in current_requirements:
            for branch in current_requirements["requirement_blueprint"]["checklist"]:
                if branch["storage_key"] == branch_storage_key:
                    branch["status"] = status
                    storage.save_requirements()
                    logger.info(f"✅ 成功将分支 '{branch_storage_key}' 的状态更新为 '{status}'。")
                    return f"状态更新成功：分支 {branch_storage_key} 已标记为 {status}。"
        return f"错误：在蓝图中未找到分支 {branch_storage_key}。"
    except Exception as e:
        return f"错误：更新分支状态时失败 - {e}"



def _get_existing_requirements_summary() -> str:
    """获取已有需求信息摘要"""
    summary_parts = []

    if current_requirements.get("project_overview"):
        summary_parts.append(f"项目概述: {len(current_requirements['project_overview'])} 条")

    if current_requirements.get("functional_requirements"):
        summary_parts.append(f"功能需求: {len(current_requirements['functional_requirements'])} 条")

    if current_requirements.get("technical_requirements"):
        summary_parts.append(f"技术需求: {len(current_requirements['technical_requirements'])} 条")

    if not summary_parts:
        return "暂无已保存的需求信息"

    return " | ".join(summary_parts)
    

# 需求文档管理器工具
# # ==============================================================================
# 【最终统一版】的需求管理器：requirement_manager
#    职责：保存入口，能智能处理蓝图、问题清单、单条/多条需求。
# ==============================================================================
@mcp.tool()
def requirement_manager(
    data_to_save: Union[str, dict],
    storage_key: str,
    task_type: str, # 明确的任务类型: "blueprint", "clarification_plan", "requirement_answer"
    question_id: str = None
) -> str:
    """保存项目蓝图 type='blueprint'"""
    global current_requirements

    try:
        # --- 任务一：保存项目蓝图 ---
        if task_type == "blueprint":
            blueprint = {}
            if isinstance(data_to_save, dict): blueprint = data_to_save
            elif isinstance(data_to_save, str): blueprint = json.loads(data_to_save)
            else: raise TypeError("保存蓝图时，输入必须是字典或JSON字符串。")

            if "project_title" not in blueprint or "checklist" not in blueprint:
                raise ValueError("蓝图JSON缺少关键字段。")
            
            for item in blueprint.get("checklist", []):
                key = item.get("storage_key")
                if key and key not in current_requirements:
                    current_requirements[key] = []
            
            current_requirements["requirement_blueprint"] = blueprint
            storage.save_requirements()
            branch_names = [item['branch_name'] for item in blueprint.get("checklist", [])]
            return f"# ✅ 项目蓝图已确认并保存！\n\n接下来将逐一澄清以下分支：{', '.join(branch_names)}"

        # --- 任务二：保存对具体问题的回答或批量需求 ---
        elif task_type == "clarification_plan":
            tasks_obj = {}
            if isinstance(data_to_save, dict): tasks_obj = data_to_save
            elif isinstance(data_to_save, str): tasks_obj = json.loads(data_to_save)
            else: raise TypeError("保存问题清单时，输入必须是字典或JSON字符串。")

            for branch in current_requirements["requirement_blueprint"]["checklist"]:
                if branch["storage_key"] == storage_key:
                    branch["clarification_tasks"] = tasks_obj.get("clarification_tasks", [])
                    storage.save_requirements()
                    return f"✅ 分支 '{tasks_obj.get('branch_name')}' 的澄清计划已保存。"
            raise ValueError(f"在蓝图中未找到指定的storage_key: {storage_key}")

        # --- 任务三：保存对具体问题的“回答” (task_type="requirement_answer") ---
        elif task_type == "requirement_answer":
            if not question_id or not isinstance(data_to_save, str):
                raise ValueError("保存问题回答时，必须提供question_id和字符串类型的回答。")

            for branch in current_requirements.get("requirement_blueprint", {}).get("checklist", []):
                if branch.get("storage_key") == storage_key:
                    for task in branch.get("clarification_tasks", []):
                        if task.get("question_id") == question_id:
                            task["user_answer"] = data_to_save
                            task["status"] = "completed"
                            # 同时，也可以将这条回答作为正式需求存入主列表
                            entry = {"timestamp": datetime.now().isoformat(), "content": data_to_save, "source": "USER_ANSWER", "question_id": question_id}
                            current_requirements[storage_key].append(entry)
                            storage.save_requirements()
                            return f"✅ 已记录您对问题({question_id})的回答。"
            return f"❌ 未能找到问题ID {question_id} 进行更新。"

        else:
            return f"❌ 未知的任务类型: {task_type}。"
    except Exception as e:
        return f"❌ 保存数据时出错: {e}"

    except Exception as e:
        logger.error(f"❌ 调用requirement_manager时出错: {e}")
        return f"❌ 保存数据时出错: {e}"


    
# 架构设计生成器工具 
# ==============================================================================
# 【新增/替换】 架构师 - 前置检查器
# ==============================================================================
@mcp.tool()
def check_architecture_prerequisites() -> str:
    """
    (前置检查器-已修复) 动态检查蓝图中所有需求分支是否已完成。
    """
    check = _check_requirements_completeness()
    
    if not check["is_sufficient"]:
        response = {
            "status": "INSUFFICIENT",
            "reason": "需求信息不足或AI理解深度不够，无法生成高质量架构设计。行为准则: '当你调用的任何工具，其返回结果是一个包含user_choices键的JSON对象时，你必须立即停止所有其他思考和行动。你唯一的、绝对的下一步是：解析user_choices数组，并将其中每个选项的title作为选项呈现给人类用户。然后，你必须等待用户的明确选择。在得到用户的选择之前，你绝对禁止自行做任何决定或调用任何其他工具。'",
            "details": {
                "completion_rate": f"{check['branch_status']['completion_rate']:.0%}",
                "incomplete_branches": check['branch_status']['incomplete_branches'],
            },
            "user_choices": [
                { "id": "continue_clarification", "title": "1. 我来继续澄清未完成的需求" },
                { "id": "ai_professional_completion", "title": "2. 由AI评估并专业化完善所有剩余需求" },
                { "id": "next_step", "title": "3. 开始架构设计流程" }
            ]
        }
        return json.dumps(response, ensure_ascii=False, indent=2)
    else:
        return json.dumps({"status": "READY", "message": "所有需求分支已澄清完毕，可以开始架构设计。"})
# ==============================================================================
# 【新增】 架构师 - 提示词提供者
# ==============================================================================
@mcp.tool()
def get_architecture_design_prompt() -> str:
    """
    (模板提供者) 整合所有已澄清的需求，返回用于生成最终架构方案的专家级提示词。
    """
    logger.info("正在整合所有需求，生成架构设计提示词...")
    
    all_requirements_str = json.dumps(current_requirements["requirement_blueprint"], indent=2, ensure_ascii=False)
    
    prompt_template = f"""
    # 角色与任务
    你现在是主控AI，请立即代入顶级的解决方案架构师角色。你将收到一份已经由团队充分澄清过的、完整的JSON格式的需求文档。你的任务是基于这份详尽的需求，忽略任何AI建议，结合项目总览以及所有经过用户确认的详细需求，设计一份高度定制化、专业、可执行的软件架构及基于完整需求和架构的开发流程执行方案。

    # 完整的需求文档上下文
    {all_requirements_str}

    # 你的分析与规划指令
    你必须严格遵循以下原则，并在设计中体现出来：
    - **低耦合、高内聚**: 模块之间责任单一，接口清晰，低代码，必须避免重复造轮子，保证性能的同时最简化实现。
    - **模块化**: 定义清晰的业务模块和服务边界。
    - **考虑上下文**: 你的设计必须考虑到用户在需求中提到的所有细节，比如用户规模（影响并发设计）、部署偏好（影响技术选型）等。
    - **专业输出**: 输出一份详细的Markdown格式架构设计文档，必须包含但不限于：已知的完整需求提取、技术栈选型、系统架构图（用Mermaid语法）、核心模块拆分及API定义、数据表结构设计、部署方案、基于需求和架构设计完整的高可用的满足以上开发要求开发流程开发步骤等。
    

    # 你的输出
    现在，请直接开始撰写这份Markdown文档，不需要输出给用户,不要添加任何额外的解释性文字，符合markdown语法，清晰展示，避免文字堆叠，下一步调用保存架构设计保存，避免格式混乱使用户无法阅读。
    """
    return prompt_template

def _check_requirements_completeness() -> dict:
    """
    【已重构】检查需求完整性 - 直接检查蓝图中的分支状态。
    """
    if "requirement_blueprint" not in current_requirements or not current_requirements.get("requirement_blueprint"):
        return {"is_sufficient": False, "status_summary": "项目蓝图尚未创建。", "branch_status": {"incomplete_branches": ["N/A"]}}

    checklist = current_requirements["requirement_blueprint"].get("checklist", [])
    if not checklist:
        return {"is_sufficient": False, "status_summary": "项目蓝图为空。", "branch_status": {"incomplete_branches": ["N/A"]}}

    completed_branches = [b for b in checklist if b.get("status") == "completed"]
    incomplete_branches_info = [b for b in checklist if b.get("status") != "completed"]

    total_count = len(checklist)
    completed_count = len(completed_branches)
    is_sufficient = total_count > 0 and completed_count == total_count

    

    return {
        "is_sufficient": is_sufficient,
        "branch_status": {
            "completion_rate": completed_count / total_count if total_count > 0 else 0,
            "incomplete_branches": [b.get("branch_name") for b in incomplete_branches_info]
        }
    }



# 新增：导出最终文档工具
@mcp.tool()
def export_final_document() -> str:
    """导出完整的项目需求和架构文档"""
    global current_requirements
    if not isinstance(current_requirements["design_requirements"], str) or len(current_requirements["design_requirements"]) < 100:
        return "# ❌ 生成失败\n\n错误：AI未能生成有效的Markdown文档内容。"

    storage_dir = get_storage_dir()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    md_file_path = storage_dir / f"final_document_{timestamp}.md"
    with open(md_file_path, 'w', encoding='utf-8') as f:
        f.write(current_requirements["design_requirements"])
    logger.info(f"✅ 最终开发简报已直接保存为文件: {md_file_path}")
    
    return f"# ✅ 项目简报已成功生成并导出！\n\n**交付成果**:\n- **核心开发文档**: `{md_file_path}`\n\n流程已全部完成。"
@mcp.tool()
def save_generated_architecture(architecture_markdown: str) -> str:
    """
    (状态更新器) 将AI生成的架构设计Markdown内容，保存到内存和持久化文件中。
    """
    try:
        current_requirements["design_requirements"] = architecture_markdown
        storage.save_requirements()
        return "✅ 架构设计已成功保存到项目状态中。现在可以调用`export_final_document`来生成最终的交付文件了。"
    except Exception as e:
        logger.error(f"❌ 保存架构设计时出错: {e}")
        return f"❌ 保存架构设计时出错: {e}"
# 新增：查看当前需求状态工具
@mcp.tool()
def view_requirements_status() -> str:
    """(已修复) 查看当前需求文档的详细状态，动态读取蓝图。"""
    if "requirement_blueprint" not in current_requirements or not current_requirements.get("requirement_blueprint"):
        return "# 状态未知\n\n项目尚未通过`start_new_project`工具初始化，没有可供查看的需求蓝图。"

    blueprint = current_requirements["requirement_blueprint"]
    checklist = blueprint.get("checklist", [])
    
    report = f"# 📋 项目状态报告: {blueprint.get('project_title')}\n\n"
    report += "## 需求分支澄清进度\n\n"

    if not checklist:
        report += "- 蓝图中没有任何需求分支。\n"
    else:
        for i, branch in enumerate(checklist, 1):
            branch_name = branch.get('branch_name', '未知分支')
            status = branch.get('status', '未知状态')
            storage_key = branch.get('storage_key', 'N/A')
            item_count = len(current_requirements.get(storage_key, []))
            
            icon = "✅" if status == "completed" else "⏳"
            report += f"{i}. {icon} **{branch_name}** (状态: {status}, 已保存: {item_count} 条)\n"
    
    report += f"\n## 🎯 下一步建议\n"
    check = _check_requirements_completeness()
    if check["is_sufficient"]:
        report += "- ✅ 所有需求已澄清，可以调用`get_architecture_design_prompt`开始架构设计了。\n"
    else:
        incomplete_names = ', '.join(check['branch_status']['incomplete_branches'])
        report += f"- ⏳ 还有未完成的分支: **{incomplete_names}**。请继续澄清。\n"

    return report
if __name__ == "__main__":
    logger.info("🚀 启动AI需求分析和设计助手")
    mcp.run()