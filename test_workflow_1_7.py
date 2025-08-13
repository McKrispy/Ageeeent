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

def test_workflow_phases_1_7():
    """测试工作流第1-7条内容"""
    
    print("="*60)
    print("开始测试工作流第1-7条内容（execution之前的规划阶段）")
    print("="*60)
    
    # 用户输入
    user_requirements = input("\n请输入您的需求（或按回车使用默认示例）: ").strip()
    if not user_requirements:
        user_requirements = "帮我分析2024年人工智能在医疗领域的最新发展趋势和主要应用案例"
    
    session_id = "test_session_001"
    
    try:
        # ==================== 第1条：系统初始化 ====================
        print("\n" + "="*50)
        print("第1条：系统初始化")
        print("="*50)
        
        # 1.1-1.2: 初始化接口
        print("1.1-1.2: 初始化LLM接口和数据库接口...")
        llm_interface = OpenAIInterface()
        db_interface = RedisClient()
        print("✅ LLM接口和数据库接口初始化完成")
        
        # 1.3: 初始化数据类
        print("1.3: 初始化数据类...")
        mcp = MCP(user_requirements=user_requirements, session_id=session_id)
        working_memory = WorkingMemory()
        strategies = StrategyData()
        print("✅ MCP、WorkingMemory、StrategyData初始化完成")
        
        # 1.4: 初始化实体
        print("1.4: 初始化LLM实体...")
        questionnaire_designer = QuestionnaireDesigner(llm_interface, db_interface)
        profile_drawer = ProfileDrawer(llm_interface, db_interface)
        strategy_planner = LLMStrategyPlanner(llm_interface)
        task_planner = LLMTaskPlanner(llm_interface)
        print("✅ 所有LLM实体初始化完成")
        
        # 1.5: 初始化工具注册表
        print("1.5: 初始化工具注册表...")
        tool_registry = ToolRegistry()
        available_tools = tool_registry.list_tools()
        print(f"✅ 工具注册表初始化完成，可用工具: {available_tools}")
        
        # ==================== 第2条：接收用户原始输入 ====================
        print("\n" + "="*50)
        print("第2条：接收用户原始输入")
        print("="*50)
        print(f"用户需求: {user_requirements}")
        print("✅ 用户原始输入已接收")
        
        # ==================== 第3条：生成问题 ====================
        print("\n" + "="*50)
        print("第3条：questionnaire_designer生成问题")
        print("="*50)
        
        questionnaire = questionnaire_designer.process(mcp)
        print(f"生成的问题清单:\n{questionnaire}")
        
        # 模拟用户补充信息
        print("\n请根据上述问题提供补充信息:")
        supplementary_info = input("补充信息（或按回车使用默认）: ").strip()
        if not supplementary_info:
            supplementary_info = "我主要关注深度学习在医疗影像诊断方面的应用，特别是在癌症检测和早期诊断方面的突破。我希望了解具体的技术实现和临床应用效果。"
        
        print("✅ 问题生成和用户补充完成")
        
        # ==================== 第4条：用户画像分析 ====================
        print("\n" + "="*50)
        print("第4条：profile_drawer分析用户画像")
        print("="*50)
        
        mcp = profile_drawer.process(mcp, supplementary_info)
        
        print("用户画像分析结果:")
        if mcp.completion_requirement:
            print(f"原始输入: {mcp.completion_requirement.original_input}")
            print(f"补充内容: {mcp.completion_requirement.supplementary_content}")
            print(f"用户画像: {mcp.completion_requirement.profile_analysis}")
        
        print("✅ 用户画像分析完成，completion_requirement已更新")
        
        # ==================== 第5条：开始双重循环 ====================
        print("\n" + "="*50)
        print("第5条：开始双重循环（用户信息输入完成）")
        print("="*50)
        print("✅ 用户信息输入阶段完成，开始进入嵌套双重循环")
        
        # ==================== 第6条：战略规划 ====================
        print("\n" + "="*50)
        print("第6条：strategy_planner生成战略计划")
        print("="*50)
        
        mcp = strategy_planner.process(mcp, strategies)
        
        print("生成的战略计划:")
        for i, plan in enumerate(mcp.strategy_plans, 1):
            print(f"{i}. ID: {plan.id}")
            print(f"   描述: {plan.description}")
            print(f"   状态: {'已完成' if plan.is_completed else '待执行'}")
        
        print("✅ 战略计划生成完成")
        
        # ==================== 第7条：任务规划 ====================
        print("\n" + "="*50)
        print("第7条：task_planner生成子目标和执行命令")
        print("="*50)
        
        print("7.1: 读取工具注册表...")
        print(f"可用工具: {available_tools}")
        
        print("7.2-7.5: 生成子目标和执行命令...")
        mcp = task_planner.process(mcp, strategies)
        
        print("\n生成的子目标:")
        for i, subgoal in enumerate(mcp.sub_goals, 1):
            print(f"{i}. ID: {subgoal.id}")
            print(f"   父战略计划: {subgoal.parent_strategy_plan_id}")
            print(f"   描述: {subgoal.description}")
            print(f"   状态: {'已完成' if subgoal.is_completed else '待执行'}")
        
        print(f"\n生成的执行命令:")
        for i, command in enumerate(mcp.executable_commands, 1):
            print(f"{i}. ID: {command.id}")
            print(f"   父子目标: {command.parent_sub_goal_id}")
            print(f"   工具: {command.tool}")
            print(f"   参数: {json.dumps(command.params, ensure_ascii=False, indent=2)}")
            print(f"   状态: {'已完成' if command.is_completed else '待执行'}")
            print("-" * 40)
        
        print("✅ 子目标和执行命令生成完成")
        
        # ==================== 测试总结 ====================
        print("\n" + "="*60)
        print("测试总结")
        print("="*60)
        print(f"✅ 第1条 - 系统初始化: 完成")
        print(f"✅ 第2条 - 接收用户原始输入: 完成")
        print(f"✅ 第3条 - questionnaire_designer生成问题: 完成")
        print(f"✅ 第4条 - profile_drawer分析用户画像: 完成")
        print(f"✅ 第5条 - 开始双重循环: 完成")
        print(f"✅ 第6条 - strategy_planner生成战略计划: 完成 ({len(mcp.strategy_plans)}个计划)")
        print(f"✅ 第7条 - task_planner生成子目标和执行命令: 完成 ({len(mcp.sub_goals)}个子目标, {len(mcp.executable_commands)}个命令)")
        
        print(f"\n🎉 前7条工作流测试全部完成！")
        print(f"📋 生成了 {len(mcp.strategy_plans)} 个战略计划")
        print(f"🎯 生成了 {len(mcp.sub_goals)} 个子目标") 
        print(f"⚡ 生成了 {len(mcp.executable_commands)} 个可执行命令")
        print(f"\n💡 下一步可以进入第8条execution阶段执行这些命令")
        
        return mcp, working_memory, strategies
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None
    
    finally:
        if 'db_interface' in locals():
            db_interface.disconnect()

if __name__ == "__main__":
    test_workflow_phases_1_7()