from typing import List

from queryrewrite.utils.data_models import RewrittenQuery
from .metrics import calculate_rouge_l, calculate_bleu
from queryrewrite.llm.base import LLMBase
from queryrewrite.utils.super_float import SuperFloat

def no_validation(rewritten_queries: List[RewrittenQuery], original_query: str) -> List[RewrittenQuery]:
    """Returns the rewritten queries without any validation."""
    return rewritten_queries

def rouge_l_bleu_normalized(rewritten_queries: List[RewrittenQuery], original_query: str) -> List[RewrittenQuery]:
    """Calculates ROUGE-L and BLEU scores and returns the query with the highest ROUGE-L and lowest BLEU."""
    if not rewritten_queries:
        return []

    scores = []
    for rq in rewritten_queries:
        rouge_l = calculate_rouge_l(rq["query"], original_query)
        bleu = calculate_bleu(rq["query"], original_query)
        scores.append((rouge_l, bleu, rq))
        # print(f"Query: {rq['query']}, ROUGE-L: {rouge_l}, BLEU: {bleu}")

    # Normalize scores (assuming higher is better for ROUGE-L, lower is better for BLEU)
    max_rouge_l = max(s[0] for s in scores)
    min_bleu = min(s[1] for s in scores)
    
    # Avoid division by zero
    if max_rouge_l == 0: max_rouge_l = 1
    if min_bleu == 0: min_bleu = 1


    normalized_scores = [
        (s[0] / max_rouge_l - s[1] / min_bleu, s[2]) for s in scores
    ]

    return [max(normalized_scores, key=lambda item: item[0])[1]]

def filter_by_rouge_l_bleu_thresholds(rewritten_queries: List[RewrittenQuery], original_query: str, 
                        rouge_l_threshold: float = 0.4, bleu_threshold: float = 0.3) -> List[RewrittenQuery]:
    """
    Filters queries based on ROUGE-L and BLEU score thresholds.
    
    Returns queries where:
    - ROUGE-L score > rouge_l_threshold (higher is better)
    - BLEU score < bleu_threshold (lower is better)
    
    Args:
        rewritten_queries: List of rewritten queries to filter
        original_query: The original query for comparison
        rouge_l_threshold: Minimum ROUGE-L score threshold (default: 0.4)
        bleu_threshold: Maximum BLEU score threshold (default: 0.3)
        
    Returns:
        List of queries that meet both threshold criteria
    """
    if not rewritten_queries:
        return []

    optimal_queries = []
    
    for rq in rewritten_queries:
        rouge_l_score = calculate_rouge_l(rq["query"], original_query)
        bleu_score = calculate_bleu(rq["query"], original_query)
        # print(f"Query: {rq['query']}, ROUGE-L: {rouge_l_score}, BLEU: {bleu_score}")
        # Check if query meets both criteria:
        # - ROUGE-L score >= threshold (higher semantic similarity)
        # - BLEU score < threshold (lower lexical similarity)
        if rouge_l_score >= rouge_l_threshold and bleu_score < bleu_threshold:
            optimal_queries.append(rq)
    
    return optimal_queries

def pareto_optimal(rewritten_queries: List[RewrittenQuery], original_query: str) -> List[RewrittenQuery]:
    """Finds the Pareto optimal set of rewritten queries based on ROUGE-L and BLEU scores."""
    if not rewritten_queries:
        return []

    scores = []
    for rq in rewritten_queries:
        rouge_l = calculate_rouge_l(rq["query"], original_query)
        bleu = calculate_bleu(rq["query"], original_query)
        scores.append((rouge_l, bleu, rq))

    pareto_front = []
    for i, (r1, b1, q1) in enumerate(scores):
        is_dominated = False
        for j, (r2, b2, q2) in enumerate(scores):
            if i == j: continue
            # A query is dominated if another query is better or equal in all objectives
            # and strictly better in at least one objective.
            if (r2 >= r1 and b2 <= b1) and (r2 > r1 or b2 < b1):
                is_dominated = True
                break
        if not is_dominated:
            pareto_front.append(q1)
            
    return pareto_front

def most_detailed(rewritten_queries: List[RewrittenQuery], original_query: str) -> List[RewrittenQuery]:
    """Returns the query that is longest compared to the original query."""
    detailed_queries = [rq for rq in rewritten_queries if len(rq["query"]) > len(original_query)]
    if not detailed_queries:
        return []
    # Return the longest query
    return [max(detailed_queries, key=lambda rq: len(rq["query"]))]

def llm_semantic_similarity(rewritten_queries: List[RewrittenQuery], original_query: str, llm: LLMBase,thinking:str='') -> List[RewrittenQuery]:
    """Uses an LLM to find the query with the highest semantic similarity and lowest BLEU score."""
    if not rewritten_queries:
        return []

    best_query = None
    highest_similarity = -1
    lowest_bleu_at_highest_sim = 2.0  # BLEU scores are between 0 and 1

    for rq in rewritten_queries:
        prompt = f'{thinking}\n\n评估以下两个查询的语义相似度，\n查询1: {original_query}\n查询2: {rq["query"]}，返回一个0到1之间的浮点数，semantic_similarity=。'
        response = llm.invoke(prompt)
        try:
            similarity = SuperFloat(response)
            bleu_score = calculate_bleu(rq["query"], original_query)
            # print(f"prompt: {prompt},response: {response},similarity: {similarity}, bleu_score: {bleu_score}")
            
            if similarity > highest_similarity and 1.0-bleu_score>0.00000001:
                highest_similarity = similarity
                lowest_bleu_at_highest_sim = bleu_score
                best_query = rq
            elif similarity == highest_similarity:
                if bleu_score < lowest_bleu_at_highest_sim:
                    lowest_bleu_at_highest_sim = bleu_score
                    best_query = rq
        except ValueError:
            continue

    return [best_query] if best_query else []