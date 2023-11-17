from app.converter.platforms.base.lucene.mapping import LuceneMappings


class OpenSearchMappings(LuceneMappings):
    pass


opensearch_mappings = OpenSearchMappings(platform_dir="opensearch")
