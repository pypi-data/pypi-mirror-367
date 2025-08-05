import jieba.posseg as pseg
from typing import List
from queryrewrite.utils.super_list import SuperList
import itertools

from queryrewrite.llm.base import LLMBase
from queryrewrite.utils.data_models import Query, RewrittenQuery

class SynonymRewriter:
    """Rewrites a query by generating synonyms for its words using an LLM."""

    def __init__(self, llm: LLMBase,thinking:str=''):
        self.llm = llm
        self.thinking = thinking

    def rewrite(self, query: Query) -> List[RewrittenQuery]:
        """
        Rewrites the query by generating synonyms for its words.

        Args:
            query: The query to rewrite.

        Returns:
            A list of rewritten queries.
        """
        words = list(pseg.cut(query["query"]))
        rewritten_word_lists = []
        for word, flag in words:
            # if flag not in ["x"]:
            prompt = f"{self.thinking}\n\n生成‘{word}’的最多10个同义词，以json list的格式返回。"
            response = self.llm.invoke(prompt)
            
            try:
                synonyms = SuperList(response)
                rewritten_word_lists.append(synonyms)
                # print(f"words:{words},response:{response},synonyms:{synonyms},rewritten_word_lists:{rewritten_word_lists}")
            except Exception as e:
                rewritten_word_lists.append([word]) # Fallback to original word
            # else:
            #     rewritten_word_lists.append([word])

        rewritten_queries = []
        for combination in itertools.product(*rewritten_word_lists):
            rewritten_queries.append(
                {"query": "".join(combination), "reference": query["reference"]}
            )

        return rewritten_queries
