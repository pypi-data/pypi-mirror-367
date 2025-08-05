import json
from typing import List

from queryrewrite.llm.base import LLMBase
from queryrewrite.utils.data_models import Query, RewrittenQuery
from queryrewrite.utils.super_json import SuperJSON

class LLMRewriter:
    """Rewrites a query using a large language model."""

    def __init__(self, llm: LLMBase,thinking:str=''):
        self.llm = llm
        self.thinking = thinking
        self.response_parser = SuperJSON()
        self.system_prompt = '''
def 资深测试开发专家():
    """
    你是一名从业20年的资深测试开发工程师，一直从事NLP、LLM相关技术的测试，你曾经参与过ChatGPT的测试，非常了解如何测试一个大模型应用。
    """
    能力=["测试分析", "测试设计","NLP性能指标","LLM的性能指标","RAG","向量数据库","embedding model","知识图谱","大模型应用测试相关的实践"]
    工作内容=["query rewrite","评测","测试数据标注","对齐","python","评价测试用数据","选择性能参数"]

def query_rewrite(用户输入):
    """
    分析用户的输入的测试数据，依据数据进行改写并返回，返回格式json
    """
    new_data = []
    new_query_list = one_query_rewrite(用户输入["query"])
    for one_new_query in new_query_list:
        new_data.append({"query":one_new_query,"reference":用户输入["reference"]})


def one_query_rewrite(query):
    """
    依据reference的上下文，完成query改写，返回一个list，包含10条新query。
    """
    new_list = 生成一个包含10条和query语义相同的，文字结构有区别的query的list
    


if __name__ == "__main__":
    # 必须按照如下的运行规则来运行你的程序：    
    # 1 设定system role
    资深测试开发专家()
    print("请输入你改写的query数据，数据格式：{\"query\":\"\",\"reference\":\"\"}：")
    # 2 调取query_write改写
    query_rewrite(用户输入)
    # 3 严格遵守函数的调关系
    # 4 输出 json格式，格式为[{"query":"","reference":""}]

'''

    def rewrite(self, query: Query) -> List[RewrittenQuery]:
        """ 
        Rewrites the query using the LLM.

        Args:
            query: The query to rewrite.

        Returns:
            A list of rewritten queries.
        """
        prompt = f'{self.thinking}\n\n{self.system_prompt}\n\n{{"query":"{query["query"]}","reference":"{query["reference"]}"}}'
        # print(f"llm_rewriter prompt: {prompt}")
        response = self.llm.invoke(prompt)
        # print(f"llm_rewriter response: {response}")
        
        # Use the response parser to extract JSON
        parsed_response = self.response_parser.loads(response)
        
        # Handle the parsed response
        if "response" in parsed_response and len(parsed_response) == 1:
            # No JSON found, return the raw response as a single query
            return [{"query": response, "reference": query["reference"]}]
        else:
            return parsed_response
            