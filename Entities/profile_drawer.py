from Entities.base_llm_entity import BaseLLMEntity
from Data.mcp_models import MCP, CompletionRequirement

class ProfileDrawer(BaseLLMEntity):
    def __init__(self, llm_interface, db_interface, entity_id=None):
        super().__init__(llm_interface, db_interface, entity_id)

    def process(self, mcp: MCP, supplementary_info: str, *args, **kwargs) -> MCP:
        """
        Generate user profile based on user's original input and supplementary information, and update MCP.
        :param mcp: MCP object containing user's original requirements.
        :param supplementary_info: User's supplementary answers to questions.
        :return: Updated MCP object.
        """

        print("ProfileDrawer: Analyzing user profile based on supplementary info.")
        
        if not self.prompt_template or not supplementary_info:
            print("Warning: No prompt or supplementary info for profile drawing.")
            return mcp

        combined_input = f"Original requirement: {mcp.user_requirements}\n\nSupplementary information: {supplementary_info}"
        prompt = self.prompt_template.replace('{{user_response}}', combined_input[:8000])
        profile_summary = self.llm_interface.get_completion(prompt)

        if profile_summary:
            print(f"ProfileDrawer: Profile summary generated successfully.")
        else:
            print("ProfileDrawer Error: No response.")
            profile_summary = ""

        mcp.completion_requirement = CompletionRequirement(
            original_input=mcp.user_requirements,
            supplementary_content=supplementary_info,
            profile_analysis=profile_summary
        )

        print("MCP's completion_requirement has been updated.")
        
        return mcp