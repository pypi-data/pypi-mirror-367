# ScholarSort

A powerful Python library for academic research with integrated impact factor analysis, similar to the scholarly package but with enhanced features.

## Features

- 🔍 **Academic Search**: Search academic papers, authors, and journals
- 📊 **Impact Factor Analysis**: Get journal impact factors, CiteScore, SJR and other metrics
- 👨‍🎓 **Author Analysis**: Analyze researcher metrics and publication history
- 📖 **Journal Analysis**: Journal rankings, metric trends, and recommendation system
- 🚀 **Async Support**: Asynchronous operations for improved performance
- 💾 **Caching**: Built-in caching to reduce duplicate requests

## Installation

```bash
pip install scholarsort
```

## Quick Start

### Basic Search

```python
from scholarsort import ScholarlySearch

# Create search instance
searcher = ScholarlySearch()

# Search publications
publications = searcher.search_publications("machine learning", num_results=10)
for pub in publications:
    print(f"Title: {pub['title']}")
    print(f"Citations: {pub['citations']}")
    print(f"Authors: {pub['authors']}")
    print("-" * 50)

# Search author
author_info = searcher.search_author("Geoffrey Hinton")
if author_info:
    print(f"Author: {author_info['name']}")
    print(f"Affiliation: {author_info['affiliation']}")
    print(f"Total Citations: {author_info['total_citations']}")
```

### Impact Factor Analysis

```python
from scholarsort import ImpactFactorAnalyzer

# Create impact factor analyzer
if_analyzer = ImpactFactorAnalyzer()

# Get journal impact factor
journal_metrics = if_analyzer.get_journal_impact_factor("Nature")
if journal_metrics:
    print(f"Journal: {journal_metrics['journal_name']}")
    print(f"Impact Factor: {journal_metrics['impact_factor']}")
    print(f"CiteScore: {journal_metrics['citescore']}")
    print(f"Quartile: {journal_metrics['quartile']}")

# Compare multiple journals
journals = ["Nature", "Science", "Cell"]
comparison = if_analyzer.compare_journals(journals)
print(comparison)

# Get top journals in specific field
top_journals = if_analyzer.get_journal_ranking("Computer Science", limit=20)
for i, journal in enumerate(top_journals, 1):
    print(f"{i}. {journal['journal_name']} (IF: {journal['impact_factor']})")
```

### Author Deep Analysis

```python
from scholarsort import AuthorAnalyzer

# Create author analyzer
author_analyzer = AuthorAnalyzer()

# Get detailed author profile
profile = author_analyzer.get_author_profile("Yann LeCun")
if profile:
    print(f"H-Index: {profile['h_index']}")
    print(f"i10-Index: {profile['i10_index']}")
    print(f"Research Interests: {', '.join(profile['interests'])}")
    
    # Analyze publications
    publications = profile['publications']
    metrics = author_analyzer.calculate_author_metrics(publications)
    print(f"Total Publications: {metrics['total_publications']}")
    print(f"Average Citations: {metrics['avg_citations_per_paper']}")

# Compare multiple authors
authors = ["Geoffrey Hinton", "Yann LeCun", "Yoshua Bengio"]
comparison = author_analyzer.compare_authors(authors)
print(comparison)
```

### Journal Analysis and Recommendation

```python
from scholarsort import JournalAnalyzer

# Create journal analyzer
journal_analyzer = JournalAnalyzer()

# Get journal detailed information
journal_info = journal_analyzer.get_journal_info("Nature Machine Intelligence")
if journal_info:
    print(f"Journal: {journal_info['title']}")
    print(f"Publisher: {journal_info['publisher']}")
    print(f"Open Access: {journal_info.get('open_access', False)}")

# Search journals by subject
ai_journals = journal_analyzer.search_journals_by_subject("Artificial Intelligence")
for journal in ai_journals[:5]:
    print(f"- {journal['title']} ({journal['publisher']})")

# Journal recommendations
keywords = ["machine learning", "artificial intelligence"]
recommendations = journal_analyzer.recommend_journals(
    keywords=keywords,
    min_if=2.0,
    max_if=8.0,
    open_access=True
)

print("Recommended Journals:")
for rec in recommendations[:5]:
    print(f"- {rec['journal_name']} (IF: {rec['impact_factor']}, Relevance: {rec['relevance_score']:.2f})")
```

### Advanced Features

```python
import asyncio
from scholarsort import ScholarlySearch, ImpactFactorAnalyzer

async def advanced_analysis():
    # Async search
    searcher = ScholarlySearch()
    results = await searcher.async_search_publications("deep learning")
    
    # Impact factor trend analysis
    if_analyzer = ImpactFactorAnalyzer()
    years = [2020, 2021, 2022, 2023, 2024]
    trend_data = if_analyzer.analyze_journal_trend("Nature", years)
    
    if trend_data is not None:
        print("Nature Journal Impact Factor Trends:")
        print(trend_data)

# Run async analysis
# asyncio.run(advanced_analysis())
```

## Data Sources

- **Google Scholar**: Paper search, author information, citation data
- **Scopus**: CiteScore and journal metrics
- **Journal Citation Reports (JCR)**: Impact factor data
- **ScimagoJR**: SJR rankings and journal metrics
- **DOAJ**: Open access journal information
- **Crossref**: Journal metadata

## Important Notes

1. **Request Rate**: Built-in request delay mechanism to avoid being blocked by search engines
2. **Data Accuracy**: Metrics may vary between different data sources
3. **API Limitations**: Some features require appropriate API access permissions
4. **Cache Usage**: Automatic result caching to reduce duplicate requests

## License

MIT License

## Contributing

Issues and feature requests are welcome!

## Changelog

### v0.1.0a1 (2025)
- Initial pre-release version
- Basic academic search functionality
- Impact factor analysis
- Author and journal analysis
- Async support

## Contact

- Homepage: https://github.com/scholarsort-team/scholarsort
- Documentation: https://scholarsort.readthedocs.io/
- Issues: https://github.com/scholarsort-team/scholarsort/issues
- Team Email: team@scholarsort.org


