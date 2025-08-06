"""
ScholarSort Basic Usage Examples

This example demonstrates how to use ScholarSort for basic academic search and analysis
"""

from scholarsort import ScholarlySearch, ImpactFactorAnalyzer, AuthorAnalyzer, JournalAnalyzer


def main():
    print("=== ScholarSort Basic Usage Examples ===\n")
    
    # 1. Publication Search
    print("1. Academic Publication Search")
    print("-" * 40)
    
    searcher = ScholarlySearch()
    publications = searcher.search_publications("artificial intelligence", num_results=5)
    
    for i, pub in enumerate(publications, 1):
        print(f"{i}. {pub['title']}")
        print(f"   Authors: {pub['authors']}")
        print(f"   Citations: {pub['citations']}")
        print()
    
    # 2. Author Search
    print("2. Author Information Search")
    print("-" * 40)
    
    author_info = searcher.search_author("Geoffrey Hinton")
    if author_info:
        print(f"Author: {author_info['name']}")
        print(f"Affiliation: {author_info['affiliation']}")
        print(f"Total Citations: {author_info['total_citations']}")
    print()
    
    # 3. Impact Factor Analysis
    print("3. Journal Impact Factor Analysis")
    print("-" * 40)
    
    if_analyzer = ImpactFactorAnalyzer()
    
    journals = ["Nature", "Science", "Cell"]
    for journal in journals:
        metrics = if_analyzer.get_journal_impact_factor(journal)
        if metrics:
            print(f"{journal}:")
            print(f"  Impact Factor: {metrics['impact_factor']}")
            print(f"  CiteScore: {metrics['citescore']}")
            print(f"  Quartile: {metrics['quartile']}")
    print()
    
    # 4. Journal Comparison
    print("4. Journal Comparison Analysis")
    print("-" * 40)
    
    comparison = if_analyzer.compare_journals(journals)
    if comparison is not None:
        print(comparison.to_string(index=False))
    print()
    
    # 5. Author Detailed Analysis
    print("5. Author Detailed Analysis")
    print("-" * 40)
    
    author_analyzer = AuthorAnalyzer()
    
    # Mock author profile data for demonstration
    # In real usage, this would be retrieved from Google Scholar
    sample_publications = [
        {'title': 'Deep Learning', 'citations': 50000, 'year': '2016'},
        {'title': 'Neural Networks', 'citations': 25000, 'year': '2018'},
        {'title': 'Machine Learning', 'citations': 15000, 'year': '2020'},
    ]
    
    metrics = author_analyzer.calculate_author_metrics(sample_publications)
    print("Author Metrics:")
    print(f"  Publications: {metrics['total_publications']}")
    print(f"  Total Citations: {metrics['total_citations']}")
    print(f"  H-Index: {metrics['h_index']}")
    print(f"  Average Citations: {metrics['avg_citations_per_paper']}")
    print()
    
    # 6. Journal Recommendations
    print("6. Journal Recommendations")
    print("-" * 40)
    
    journal_analyzer = JournalAnalyzer()
    
    keywords = ["machine learning", "artificial intelligence"]
    recommendations = journal_analyzer.recommend_journals(
        keywords=keywords,
        min_if=2.0,
        max_if=8.0,
        open_access=True
    )
    
    print(f"Journal recommendations based on keywords {keywords}:")
    for i, rec in enumerate(recommendations[:5], 1):
        print(f"{i}. {rec['journal_name']}")
        print(f"   Impact Factor: {rec['impact_factor']}")
        print(f"   Relevance Score: {rec['relevance_score']:.2f}")
        print(f"   Open Access: {'Yes' if rec['open_access'] else 'No'}")
    
    # Clean up resources
    searcher.close()
    if_analyzer.close()
    author_analyzer.close()
    journal_analyzer.close()
    
    print("\n=== Examples Complete ===")


if __name__ == "__main__":
    main()