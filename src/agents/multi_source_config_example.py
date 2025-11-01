"""
多源数据配置示例

展示如何配置EnhancedLiteratureAgent使用不同的数据源组合。
"""

# 示例1：基础配置 - 只使用Web搜索和本地知识库
BASIC_CONFIG = {
    "web_search": {
        "type": "web_search",
        "timeout": 30,
        "max_retries": 3,
        "engines": ["semantic_scholar", "arxiv"]
    },
    "local_knowledge": {
        "type": "local_knowledge",
        "rag_system_path": "src/rag",
        "collection_name": "literature",
        "top_k": 10
    }
}

# 示例2：完整配置 - 包含所有数据源
FULL_CONFIG = {
    "web_search": {
        "type": "web_search",
        "timeout": 30,
        "max_retries": 3,
        "engines": ["semantic_scholar", "arxiv", "crossref"]
    },
    "zotero_personal": {
        "type": "zotero",
        "api_key": "your_zotero_api_key_here",
        "user_id": "your_user_id_here",
        "timeout": 30
    },
    "zotero_group": {
        "type": "zotero",
        "api_key": "your_zotero_api_key_here", 
        "group_id": "your_group_id_here",
        "timeout": 30
    },
    "local_knowledge": {
        "type": "local_knowledge",
        "rag_system_path": "src/rag",
        "collection_name": "literature",
        "top_k": 15
    }
}

# 示例3：学术研究配置 - 专注于学术搜索
ACADEMIC_CONFIG = {
    "semantic_scholar": {
        "type": "web_search",
        "timeout": 45,
        "max_retries": 5,
        "engines": ["semantic_scholar"]
    },
    "arxiv": {
        "type": "web_search", 
        "timeout": 30,
        "max_retries": 3,
        "engines": ["arxiv"]
    },
    "local_papers": {
        "type": "local_knowledge",
        "rag_system_path": "src/rag",
        "collection_name": "academic_papers"
    }
}

# 示例4：机构配置 - 包含机构Zotero库
INSTITUTIONAL_CONFIG = {
    "web_search": {
        "type": "web_search",
        "timeout": 30,
        "engines": ["semantic_scholar", "crossref"]
    },
    "institution_library": {
        "type": "zotero",
        "api_key": "institution_api_key",
        "group_id": "institution_group_id",
        "timeout": 60
    },
    "local_repository": {
        "type": "local_knowledge",
        "rag_system_path": "src/rag",
        "collection_name": "institution_papers"
    }
}


def get_config_by_name(config_name: str):
    """根据名称获取配置"""
    configs = {
        "basic": BASIC_CONFIG,
        "full": FULL_CONFIG,
        "academic": ACADEMIC_CONFIG,
        "institutional": INSTITUTIONAL_CONFIG
    }
    return configs.get(config_name)


def create_custom_config(**kwargs):
    """创建自定义配置"""
    config = {}
    
    # Web搜索配置
    if kwargs.get("enable_web_search", True):
        config["web_search"] = {
            "type": "web_search",
            "timeout": kwargs.get("web_timeout", 30),
            "max_retries": kwargs.get("web_retries", 3),
            "engines": kwargs.get("web_engines", ["semantic_scholar", "arxiv"])
        }
    
    # Zotero配置
    if kwargs.get("zotero_api_key") and kwargs.get("zotero_user_id"):
        config["zotero"] = {
            "type": "zotero",
            "api_key": kwargs["zotero_api_key"],
            "user_id": kwargs["zotero_user_id"],
            "timeout": kwargs.get("zotero_timeout", 30)
        }
    
    # 本地知识库配置
    if kwargs.get("enable_local_knowledge", True):
        config["local_knowledge"] = {
            "type": "local_knowledge",
            "rag_system_path": kwargs.get("rag_path", "src/rag"),
            "collection_name": kwargs.get("collection_name", "literature"),
            "top_k": kwargs.get("local_top_k", 10)
        }
    
    return config