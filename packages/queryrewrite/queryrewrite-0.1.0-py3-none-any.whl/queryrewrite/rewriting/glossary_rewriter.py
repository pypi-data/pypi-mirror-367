import jieba
import itertools
from typing import List

from queryrewrite.utils.data_models import Query, RewrittenQuery, Glossary

class GlossaryRewriter:
    """Rewrites a query using a glossary of synonyms."""

    def __init__(self, glossary: Glossary):
        self.glossary = glossary
        self.synonym_map = self._create_synonym_map()

    def _create_synonym_map(self) -> dict:
        synonym_map = {}
        for word_list in self.glossary:
            for word in word_list:
                synonym_map[word] = word_list
        return synonym_map

    def rewrite(self, query: Query) -> List[RewrittenQuery]:
        """
        Rewrites the query using the glossary.

        Args:
            query: The query to rewrite.

        Returns:
            A list of rewritten queries.
        """
        for word_list in self.glossary:
            for word in word_list:
                jieba.add_word(word)

        words = list(jieba.cut(query["query"]))
        rewritten_word_lists = []
        for word in words:
            rewritten_word_lists.append(self.synonym_map.get(word, [word]))

        rewritten_queries = []
        for combination in itertools.product(*rewritten_word_lists):
            rewritten_queries.append(
                {"query": "".join(combination), "reference": query["reference"]}
            )

        return rewritten_queries
