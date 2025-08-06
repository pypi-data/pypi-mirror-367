from typing import Dict, Any, List, AsyncGenerator
from agents.base_agent import BaseAgent
from utils.llm_basics import LLMMessage
from agents.research.research_prompts import (
    get_current_date,
    query_writer_instructions,
    web_searcher_instructions,
    reflection_instructions,
    answer_instructions
)
import json

class GeminiResearchDemo(BaseAgent):
    """Research agent specialized for multi-step research tasks."""
    
    def __init__(self, config, cli_console=None):
        super().__init__(config, cli_console)
        
        self.type = "GeminiResearchDemo"
        # Research state
        self.research_state = {
            "topic": "",
            "queries": [],
            "summaries": [],
            "current_step": "query_generation",
            "iteration": 0
        }
    
    def _build_system_prompt(self) -> str:
        """构建研究专用的系统提示"""
        current_date = get_current_date()
        
        return f"""You are an expert research assistant conducting comprehensive research. Today's date is {current_date}.

You have access to these tools:
- web_search: Search the web for information
- web_fetch: Fetch and read content from specific URLs  
- write_file: Save research findings and reports
- read_file: Read previously saved research files

Follow the research process step by step and use the appropriate prompts for each stage."""

    def _get_query_writer_prompt(self, topic: str, number_queries: int = 3) -> str:
        """生成查询生成提示"""
        return query_writer_instructions.format(
            current_date=get_current_date(),
            research_topic=topic,
            number_queries=number_queries
        )

    def _get_web_searcher_prompt(self, topic: str) -> str:
        """生成网络搜索提示"""
        return web_searcher_instructions.format(
            current_date=get_current_date(),
            research_topic=topic
        )

    def _get_reflection_prompt(self, topic: str) -> str:
        """生成反思提示"""
        summaries = "\n".join(self.research_state.get("summaries", []))
        
        return reflection_instructions.format(
            research_topic=topic,
            summaries=summaries if summaries else "No summaries available yet. This indicates we need to conduct initial research."
        )

    def _get_answer_prompt(self, topic: str) -> str:
        """生成最终答案提示"""
        summaries = "\n".join(self.research_state.get("summaries", []))
        
        return answer_instructions.format(
            current_date=get_current_date(),
            research_topic=topic,
            summaries=summaries
        )

    # TODO:
    async def run(self, user_message: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Run research agent with multi-step research workflow."""
        
        # 初始化研究状态
        self.research_state["topic"] = user_message
        self.research_state["iteration"] = 0
        
        # 1. 首次生成查询
        yield {"type": "step", "data": {"step": "generating_initial_queries"}}
        query_prompt = self._get_query_writer_prompt(user_message)
        query_response = await self.llm_client.generate_response([LLMMessage(role="user", content=query_prompt)],stream=False)
        # 输出JSON格式的
        # ```json
        # {{
        #     "rationale": "To answer this comparative growth question accurately, we need specific data points on Apple's stock performance and iPhone sales metrics. These queries target the precise financial information needed: company revenue trends, product-specific unit sales figures, and stock price movement over the same fiscal period for direct comparison.",
        #     "query": ["Apple total revenue growth fiscal year 2024", "iPhone unit sales growth fiscal year 2024", "Apple stock price growth fiscal year 2024"],
        # }}
        # ```
        # 提取查询生成响应中的JSON数据
        query_data = json.loads(query_response.content)
        search_queries = query_data.get("query", [])

        # 将查询添加到research_state中
        self.research_state["queries"] = search_queries

        # 2. 搜索
        search_prompt = self._get_web_searcher_prompt(search_queries)
        search_response = await self.llm_client.generate_response([LLMMessage(role="user", content=search_prompt)])
        
        if search_response.tool_calls:
            async for result in self._process_tool_calls(search_response.tool_calls):
                yield result

        self.research_state["summaries"] = search_response.content

        while True:
            try:
                
                # 3. 反思搜索结果
                yield {"type": "step", "data": {"step": "reflecting"}}
                reflection_prompt = self._get_reflection_prompt(self.research_state["summaries"])
                reflection_response = await self.llm_client.generate_response([LLMMessage(role="user", content=reflection_prompt)])
                # ```json输出格式
                # {{
                #     "is_sufficient": true, // or false
                #     "knowledge_gap": "The summary lacks information about performance metrics and benchmarks", // "" if is_sufficient is true
                #     "follow_up_queries": ["What are typical performance benchmarks and metrics used to evaluate [specific technology]?"] // [] if is_sufficient is true
                # }}
                # ```

                # 添加reflection结果到对话历史
                self.conversation_history.append(LLMMessage(
                    role="assistant", 
                    content=reflection_response.content
                ))

                # 提取反思生成响应中的JSON数据
                reflection_data = json.loads(reflection_response.content)
                is_sufficient = reflection_data.get("is_sufficient", False)
                # 4.检查研究是否充分，如果充分就退出循环
                # _is_research_sufficient() 会自动将follow_up_queries添加到research_state["queries"]
                if is_sufficient:
                    break
                else:
                    ###重新处理follow_up_queries的搜索内容
                    follow_up_queries = reflection_data.get("follow_up_queries", [])
                    search_prompt = self._get_web_searcher_prompt(follow_up_queries)
                    search_response = await self.llm_client.generate_response([LLMMessage(role="user", content=search_prompt)])
                    
                    if search_response.tool_calls:
                        async for result in self._process_tool_calls(search_response.tool_calls):
                            yield result


            except Exception as e:
                yield {"type": "error", "data": {"error": str(e)}}
                break
        
        # 5. 提交最终答案
        yield {"type": "step", "data": {"step": "generating_final_answer"}}
        final_prompt = self._get_answer_prompt(user_message)
        final_response = await self.llm_client.generate_response([LLMMessage(role="user", content=final_prompt)])
        
        yield {"type": "final_answer", "data": {"content": final_response.content}}

    
    async def _process_tool_calls(self, tool_calls):
        """处理工具调用"""
        # 执行工具
        results = await self.tool_executor.execute_tools(tool_calls) #ToolResult
        
        async for result in results:
            yield {"type": "tool_result", "data": {"result": result}}
            # 添加工具结果到对话历史
            self.conversation_history.append(LLMMessage(
                role= "tool",
                content= str(result),
                tool_call_id= result.tool_call_id
            ))

    def get_enabled_tools(self) -> List[str]:
        """Return list of enabled tool names for ResearchAgent."""
        return [
            'web_search',
            'web_fetch', 
            'write_file',
            'read_file'
        ]
