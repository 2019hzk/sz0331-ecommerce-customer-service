from typing import Any

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import  JsonOutputParser

from atguigu.domain.state import DialogueState
from atguigu.prompt.loader import load_prompt_template_content
from atguigu.infrastructure.llm_client import  llm_client


class TurnPlanner:
    async def predict(self, dialogue_state: DialogueState):
        """
        职责：利用轮次规划器进行路由分析
        Args:
            dialogue_state:

        Returns:

        """

        # 1. 构建LLM执行路由分析时需要的提示词模版中变量的内容

        prompt_inputs: dict[str, Any] = self._build_prompt_inputs(dialogue_state)

        # 2. 调用LLM
        llm_result = self._invoke(prompt_inputs)

        # 3. 返回LLM结果
        return llm_result

    def _build_prompt_inputs(self, dialogue_state: DialogueState) -> dict[str, Any]:
        user_message_str = ""
        current_conversation_str = ""
        focused_object_json = ""
        interrupted_tasks_json = ""
        active_task_json = ""
        knowledge_intents_json = ""
        available_flows_json = ""

        return {
            "user_message": user_message_str,
            "current_conversation": current_conversation_str,
            "focused_object_json": focused_object_json,
            "interrupted_tasks_json": interrupted_tasks_json,
            "active_task_json": active_task_json,
            "knowledge_intents_json": knowledge_intents_json,
            "available_flows_json": available_flows_json

        }

     async def _invoke(self, prompt_inputs: dict[str, Any]):
        """
        职责：调用LLM进行路由分析
        Args:
            prompt_inputs:

        Returns:

        """
        # 1. 加载提示词模版(模版有变量)
        prompt_template_str = load_prompt_template_content("turn_plan")

        # 2. 提示词模版对象
        prompt_template = PromptTemplate.from_template(template=prompt_template_str, template_format="jinja2")


        # 3. 构建chain
        chain= prompt_template | llm_client | JsonOutputParser()

        # 4. 执行chain
        result = await chain.ainvoke(prompt_inputs)

        # 5. 返回chain执行后的结果
        return  result





