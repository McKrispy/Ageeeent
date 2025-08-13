from Entities.base_llm_entity import BaseLLMEntity
from Data.mcp_models import MCP

class UserProfileDrawer(BaseLLMEntity):
    def __init__(self, llm_interface, db_interface, entity_id=None):
        super().__init__(llm_interface, db_interface, entity_id)

    def process(self, mcp: MCP, user_requirement: str) -> str:
        """
        处理原始数据，生成摘要。
        :param mcp: MCP对象，用于状态更新。
        :param raw_data: 来自工具的原始数据字符串。
        :return: 返回生成的摘要字符串。
        """

        print("UserProfileDrawer: Summarizing raw data into a lightweight summary.")
        
        if not self.prompt_template or not user_requirement:
            print("Warning: No prompt or raw data for summary.")
            return ""

        # 限制输入长度，防止超出模型限制
        prompt = self.prompt_template.replace('{{user_requirement}}', str(user_requirement)[:8000])
        
        summary = self.llm_interface.get_completion(prompt, model="gpt-3.5-turbo")
        
        if summary:
            print(f"Generated summary: {summary}")
        else:
            print("Error: UserProfileDrawer received no response.")
            summary = "" #确保返回字符串
        
        return summary