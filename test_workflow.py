# -*- coding: utf-8 -*-
"""
测试工作流前7条内容（execution之前的规划阶段）
1. 系统初始化
2. 接收用户原始输入
3. questionnaire_designer生成问题
4. profile_drawer分析用户画像
5. 开始双重循环
6. strategy_planner生成战略计划  
7. task_planner生成子目标和执行命令
"""

import json
from Data.mcp_models import MCP, WorkingMemory
from Data.strategies import StrategyData
from Interfaces.llm_api_interface import OpenAIInterface
from Interfaces.database_interface import RedisClient
from Entities.strategy_planner import LLMStrategyPlanner
from Entities.task_planner import LLMTaskPlanner
from Entities.questionnaire_designer import QuestionnaireDesigner
from Entities.profile_drawer import ProfileDrawer
from Tools.tool_registry import ToolRegistry
from GUI.utils.logger import WorkflowLogger

def test_workflow(user_requirements=None):
    """测试工作流第1-7条内容"""
    
    logger = WorkflowLogger()
    
    logger.add_log(phase="start", message="开始测试工作流第1-7条内容（execution之前的规划阶段）")
    
    # 用户输入
    if user_requirements is None:
        user_requirements = input("\n请输入您的需求（或按回车使用默认示例）: ").strip()
    if not user_requirements:
        user_requirements = "帮我分析2024年人工智能在医疗领域的最新发展趋势和主要应用案例"
    
    session_id = "test_session_001"
    
    try:
        # ==================== 第1条：系统初始化 ====================
        logger.add_log(phase="Initialization", message="开始测试工作流第1-7条内容（execution之前的规划阶段）")
        
        # 1.1-1.2: 初始化接口
        logger.add_log(phase="Initialization", message="1.1-1.2: 初始化LLM接口和数据库接口...")
        llm_interface = OpenAIInterface()
        db_interface = RedisClient()
        logger.add_log(phase="Initialization", message="✅ LLM接口和数据库接口初始化完成")
        
        # 1.3: 初始化数据类
        logger.add_log(phase="Initialization", message="1.3: 初始化数据类...")
        mcp = MCP(user_requirements=user_requirements, session_id=session_id)
        working_memory = WorkingMemory()
        strategies = StrategyData() 
        logger.add_log(phase="Initialization", message="✅ MCP、WorkingMemory、StrategyData初始化完成")
        
        # 1.4: 初始化实体
        logger.add_log(phase="Initialization", message="1.4: 初始化LLM实体...")
        questionnaire_designer = QuestionnaireDesigner(llm_interface, db_interface)
        profile_drawer = ProfileDrawer(llm_interface, db_interface)
        strategy_planner = LLMStrategyPlanner(llm_interface)
        task_planner = LLMTaskPlanner(llm_interface)
        logger.add_log(phase="Initialization", message="✅ 所有LLM实体初始化完成")
        
        # 1.5: 初始化工具注册表
        logger.add_log(phase="Initialization", message="1.5: 初始化工具注册表...")
        tool_registry = ToolRegistry()
        available_tools = tool_registry.list_tools()
        logger.add_log(phase="Initialization", message=f"✅ 工具注册表初始化完成，可用工具: {available_tools}")
        
        # ==================== 第2条：接收用户原始输入 ====================
        logger.add_log(phase="User Input", message="第2条：接收用户原始输入")
        logger.add_log(phase="User Input", message=f"用户需求: {user_requirements}")
        logger.add_log(phase="User Input", message="✅ 用户原始输入已接收")
        
        # ==================== 第3条：生成问题 ====================
        logger.add_log(phase="Questionnaire Designer", message="第3条：questionnaire_designer生成问题")
        
        questionnaire = questionnaire_designer.process(mcp)
        logger.add_log(phase="Questionnaire Designer", message=f"生成的问题清单:\n{questionnaire}")
        
        # 模拟用户补充信息
        logger.add_log(phase="Questionnaire Designer", message="\n请根据上述问题提供补充信息:")
        supplementary_info = input("补充信息（或按回车使用默认）: ").strip()
        if not supplementary_info:
            supplementary_info = "我主要关注深度学习在医疗影像诊断方面的应用，特别是在癌症检测和早期诊断方面的突破。我希望了解具体的技术实现和临床应用效果。"
        
        logger.add_log(phase="Questionnaire Designer", message="✅ 问题生成和用户补充完成")
        
        # ==================== 第4条：用户画像分析 ====================
        logger.add_log(phase="Profile Drawer", message="第4条：profile_drawer分析用户画像")
        
        mcp = profile_drawer.process(mcp, supplementary_info)
        
        logger.add_log(phase="Profile Drawer", message="用户画像分析结果:")
        if mcp.completion_requirement:
            logger.add_log(phase="Profile Drawer", message=f"原始输入: {mcp.completion_requirement.original_input}")
            logger.add_log(phase="Profile Drawer", message=f"补充内容: {mcp.completion_requirement.supplementary_content}")
            logger.add_log(phase="Profile Drawer", message=f"用户画像: {mcp.completion_requirement.profile_analysis}")
        
        logger.add_log(phase="Profile Drawer", message="✅ 用户画像分析完成，completion_requirement已更新")
        
        # ==================== 第5条：开始双重循环 ====================
        logger.add_log(phase="Double Loop", message="第5条：开始双重循环（用户信息输入完成）")
        logger.add_log(phase="Double Loop", message="✅ 用户信息输入阶段完成，开始进入嵌套双重循环")
        
        # ==================== 第6条：战略规划 ====================
        logger.add_log(phase="Strategy Planner", message="第6条：strategy_planner生成战略计划")
        
        mcp = strategy_planner.process(mcp, strategies)
        
        logger.add_log(phase="Strategy Planner", message="生成的战略计划:")
        for i, plan in enumerate(mcp.strategy_plans, 1):
            logger.add_log(phase="Strategy Planner", message=f"{i}. ID: {plan.id}")
            logger.add_log(phase="Strategy Planner", message=f"   描述: {plan.description}")
            logger.add_log(phase="Strategy Planner", message=f"   状态: {'已完成' if plan.is_completed else '待执行'}")
        
        logger.add_log(phase="Strategy Planner", message="✅ 战略计划生成完成")
        
        # ==================== 第7条：任务规划 ====================
        logger.add_log(phase="Task Planner", message="第7条：task_planner生成子目标和执行命令")
        
        logger.add_log(phase="Task Planner", message="7.1: 读取工具注册表...")
        logger.add_log(phase="Task Planner", message=f"可用工具: {available_tools}")
        
        logger.add_log(phase="Task Planner", message="7.2-7.5: 生成子目标和执行命令...")
        mcp = task_planner.process(mcp, strategies)
        
        logger.add_log(phase="Task Planner", message="生成的子目标:")
        for i, subgoal in enumerate(mcp.sub_goals, 1):
            logger.add_log(f"{i}. ID: {subgoal.id}")
            logger.add_log(f"   父战略计划: {subgoal.parent_strategy_plan_id}")
            logger.add_log(f"   描述: {subgoal.description}")
            logger.add_log(f"   状态: {'已完成' if subgoal.is_completed else '待执行'}")
        
        logger.add_log("生成的执行命令:")
        for i, command in enumerate(mcp.executable_commands, 1):
            logger.add_log(f"{i}. ID: {command.id}")
            logger.add_log(f"   父子目标: {command.parent_sub_goal_id}")
            logger.add_log(f"   工具: {command.tool}")
            logger.add_log(f"   参数: {json.dumps(command.params, ensure_ascii=False, indent=2)}")
            logger.add_log(f"   状态: {'已完成' if command.is_completed else '待执行'}")
        
        logger.add_log("✅ 子目标和执行命令生成完成")
        
        # ==================== 测试总结 ====================
        logger.add_log("\n" + "="*60)
        logger.add_log("测试总结")
        logger.add_log("="*60)
        logger.add_log(f"✅ 第1条 - 系统初始化: 完成")
        logger.add_log(f"✅ 第2条 - 接收用户原始输入: 完成")
        logger.add_log(f"✅ 第3条 - questionnaire_designer生成问题: 完成")
        logger.add_log(f"✅ 第4条 - profile_drawer分析用户画像: 完成")
        logger.add_log(f"✅ 第5条 - 开始双重循环: 完成")
        logger.add_log(f"✅ 第6条 - strategy_planner生成战略计划: 完成 ({len(mcp.strategy_plans)}个计划)")
        logger.add_log(f"✅ 第7条 - task_planner生成子目标和执行命令: 完成 ({len(mcp.sub_goals)}个子目标, {len(mcp.executable_commands)}个命令)")
        
        logger.add_log(f"\n🎉 前7条工作流测试全部完成！")
        logger.add_log(f"📋 生成了 {len(mcp.strategy_plans)} 个战略计划")
        logger.add_log(f"🎯 生成了 {len(mcp.sub_goals)} 个子目标") 
        logger.add_log(f"⚡ 生成了 {len(mcp.executable_commands)} 个可执行命令")
        logger.add_log(f"\n💡 下一步可以进入第8条execution阶段执行这些命令")
        
        return mcp, working_memory, strategies
        
    except Exception as e:
        logger.add_log(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None
    
    finally:
        if 'db_interface' in locals():
            db_interface.disconnect()

if __name__ == "__main__":
    test_workflow()