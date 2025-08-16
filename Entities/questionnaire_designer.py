from Entities.base_llm_entity import BaseLLMEntity
from Data.mcp_models import MCP
from Interfaces.llm_api_interface import OpenAIInterface
from Interfaces.database_interface import RedisClient
import json

class QuestionnaireDesigner(BaseLLMEntity):
    def __init__(self, llm_interface, db_interface, entity_id=None):
        super().__init__(llm_interface, db_interface, entity_id)

    def process(self, mcp: MCP) -> dict:
        """
        处理原始数据，生成摘要。
        :param mcp: MCP对象，用于状态更新。
        :param raw_data: 来自工具的原始数据字符串。
        :return: 返回生成的摘要字符串。
        """

        print("QuestionnaireDesigner: Summarizing raw data into a lightweight summary.")
        
        if not self.prompt_template or not mcp.user_requirements:
            print("Warning: No prompt or raw data for summary.")
            return ""

        # 限制输入长度，防止超出模型限制
        prompt = self.prompt_template.replace('{{user_requirement}}', str(mcp.user_requirements)[:8000])
        
        questionnaire_str = self.llm_interface.get_completion(prompt, response_format={"type": "json_object"})

        questionnaire = json.loads(questionnaire_str)
        
        if questionnaire:
            print(f"Generated questionnaire: {questionnaire} based on user requirement: {mcp.user_requirements}")
        else:
            print("Error: QuestionnaireDesigner received no response.")
            questionnaire = "Error: QuestionnaireDesigner received no response." 
        
        return questionnaire

if __name__ == "__main__":
    mcp = MCP(session_id="test", user_requirements="如何填高考志愿")
    llm_interface = OpenAIInterface()
    db_interface = RedisClient()
    questionnaire_designer = QuestionnaireDesigner(llm_interface, db_interface)
    questionnaire_designer.process(mcp)