#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI接口测试脚本
用于测试GUI与核心工作流的集成
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

def test_workflow_service():
    """测试工作流服务"""
    print("=" * 50)
    print("测试工作流服务")
    print("=" * 50)
    
    try:
        from GUI.services.workflow_service import WorkflowService, WorkflowStatus
        
        # 创建服务实例
        service = WorkflowService()
        print("✅ 工作流服务创建成功")
        
        # 测试创建会话
        user_requirements = "测试需求：请帮我研究人工智能的最新发展"
        session_id = service.create_session(user_requirements)
        print(f"✅ 会话创建成功，ID: {session_id}")
        
        # 测试获取状态
        status = service.get_session_status(session_id)
        print(f"✅ 获取状态成功: {status['status']}")
        
        # 测试获取所有会话
        all_sessions = service.get_all_sessions()
        print(f"✅ 获取所有会话成功，共 {len(all_sessions)} 个会话")
        
        return True
        
    except Exception as e:
        print(f"❌ 工作流服务测试失败: {e}")
        return False

def test_data_models():
    """测试数据模型"""
    print("=" * 50)
    print("测试数据模型")
    print("=" * 50)
    
    try:
        from Data.mcp_models import MCP, WorkingMemory, StrategyPlan, SubGoal, ExecutableCommand
        
        # 测试MCP模型
        mcp = MCP(
            session_id="test_session",
            user_requirements="测试需求"
        )
        print("✅ MCP模型创建成功")
        
        # 测试WorkingMemory模型
        memory = WorkingMemory()
        memory.data["test_key"] = "test_value"
        print("✅ WorkingMemory模型创建成功")
        
        # 测试StrategyPlan模型
        strategy = StrategyPlan(description="测试策略")
        print(f"✅ StrategyPlan模型创建成功，ID: {strategy.id}")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据模型测试失败: {e}")
        return False

def test_llm_interface():
    """测试LLM接口"""
    print("=" * 50)
    print("测试LLM接口")
    print("=" * 50)
    
    try:
        from Interfaces.llm_api_interface import LLMAPIInterface, OpenAIInterface
        
        print("✅ LLM接口类导入成功")
        
        # 注意：这里不实际创建OpenAI客户端，因为可能没有API密钥
        print("✅ LLM接口测试完成（跳过API调用）")
        
        return True
        
    except Exception as e:
        print(f"❌ LLM接口测试失败: {e}")
        return False

def test_entities():
    """测试实体模块"""
    print("=" * 50)
    print("测试实体模块")
    print("=" * 50)
    
    try:
        from Entities.base_llm_entity import BaseLLMEntity
        from Entities.strategy_planner import LLMStrategyPlanner
        from Entities.task_planner import LLMTaskPlanner
        
        print("✅ 实体类导入成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 实体模块测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始GUI接口集成测试")
    print(f"项目根目录: {project_root}")
    
    tests = [
        ("数据模型", test_data_models),
        ("LLM接口", test_llm_interface),
        ("实体模块", test_entities),
        ("工作流服务", test_workflow_service),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📝 执行测试: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ 测试 {test_name} 出现异常: {e}")
            results.append((test_name, False))
    
    # 总结
    print("\n" + "=" * 50)
    print("测试结果总结")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！GUI接口集成成功！")
        print("\n📖 下一步操作:")
        print("1. 确保Redis服务正在运行")
        print("2. 设置必要的环境变量（OPENAI_API_KEY等）")
        print("3. 运行: cd GUI && streamlit run app.py")
    else:
        print("⚠️  部分测试失败，请检查相关模块")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)