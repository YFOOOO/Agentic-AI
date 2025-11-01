"""
文档处理器

负责文档的分割、清理、标准化和元数据提取
"""

import re
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    logging.warning("tiktoken未安装，将使用简单的字符计数")

class DocumentProcessor:
    """文档处理和分割类"""
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        encoding_name: str = "cl100k_base"
    ):
        """
        初始化文档处理器
        
        Args:
            chunk_size: 文档块大小（token数）
            chunk_overlap: 块之间的重叠大小
            encoding_name: 编码器名称
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # 初始化tokenizer
        if TIKTOKEN_AVAILABLE:
            try:
                self.tokenizer = tiktoken.get_encoding(encoding_name)
            except Exception as e:
                logging.warning(f"无法加载tiktoken编码器: {e}，使用字符计数")
                self.tokenizer = None
        else:
            self.tokenizer = None
    
    def clean_text(self, text: str) -> str:
        """
        清理文本内容
        
        Args:
            text: 原始文本
            
        Returns:
            清理后的文本
        """
        if not text:
            return ""
        
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 移除特殊字符（保留基本标点）
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\"\']+', '', text)
        
        # 移除过短的行
        lines = text.split('\n')
        lines = [line.strip() for line in lines if len(line.strip()) > 10]
        
        return '\n'.join(lines).strip()
    
    def count_tokens(self, text: str) -> int:
        """
        计算文本的token数量
        
        Args:
            text: 文本内容
            
        Returns:
            token数量
        """
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        else:
            # 简单估算：平均每个token约4个字符
            return len(text) // 4
    
    def split_text(self, text: str) -> List[str]:
        """
        将文本分割成块
        
        Args:
            text: 要分割的文本
            
        Returns:
            文本块列表
        """
        if not text:
            return []
        
        # 清理文本
        text = self.clean_text(text)
        
        # 如果文本很短，直接返回
        if self.count_tokens(text) <= self.chunk_size:
            return [text]
        
        # 按段落分割
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # 检查当前块加上新段落是否超过大小限制
            test_chunk = current_chunk + "\n\n" + paragraph if current_chunk else paragraph
            
            if self.count_tokens(test_chunk) <= self.chunk_size:
                current_chunk = test_chunk
            else:
                # 保存当前块
                if current_chunk:
                    chunks.append(current_chunk)
                
                # 如果单个段落太长，需要进一步分割
                if self.count_tokens(paragraph) > self.chunk_size:
                    sub_chunks = self._split_long_paragraph(paragraph)
                    chunks.extend(sub_chunks)
                    current_chunk = ""
                else:
                    current_chunk = paragraph
        
        # 添加最后一个块
        if current_chunk:
            chunks.append(current_chunk)
        
        # 添加重叠
        return self._add_overlap(chunks)
    
    def _split_long_paragraph(self, paragraph: str) -> List[str]:
        """分割过长的段落"""
        sentences = re.split(r'[.!?]+', paragraph)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            test_chunk = current_chunk + ". " + sentence if current_chunk else sentence
            
            if self.count_tokens(test_chunk) <= self.chunk_size:
                current_chunk = test_chunk
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def _add_overlap(self, chunks: List[str]) -> List[str]:
        """为文档块添加重叠"""
        if len(chunks) <= 1 or self.chunk_overlap <= 0:
            return chunks
        
        overlapped_chunks = []
        
        for i, chunk in enumerate(chunks):
            if i == 0:
                overlapped_chunks.append(chunk)
                continue
            
            # 获取前一个块的结尾部分作为重叠
            prev_chunk = chunks[i-1]
            prev_words = prev_chunk.split()
            
            # 估算重叠的单词数
            overlap_words = min(len(prev_words), self.chunk_overlap // 4)
            
            if overlap_words > 0:
                overlap_text = " ".join(prev_words[-overlap_words:])
                overlapped_chunk = overlap_text + " " + chunk
                overlapped_chunks.append(overlapped_chunk)
            else:
                overlapped_chunks.append(chunk)
        
        return overlapped_chunks
    
    def extract_metadata(self, text: str, source: str = "") -> Dict[str, Any]:
        """
        提取文档元数据
        
        Args:
            text: 文档文本
            source: 文档来源
            
        Returns:
            元数据字典
        """
        metadata = {
            "source": source,
            "length": len(text),
            "token_count": self.count_tokens(text),
            "word_count": len(text.split()),
            "paragraph_count": len(text.split('\n\n')),
        }
        
        # 提取可能的标题
        lines = text.split('\n')
        for line in lines[:5]:  # 检查前5行
            line = line.strip()
            if line and (line.isupper() or line.startswith('#')):
                metadata["title"] = line.replace('#', '').strip()
                break
        
        # 提取关键词（简单实现）
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # 获取最频繁的词作为关键词
        keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        metadata["keywords"] = ", ".join([word for word, freq in keywords])  # 转换为字符串
        
        return metadata
    
    def process_document(
        self, 
        text: str, 
        source: str = "",
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        处理完整文档，返回分割后的块和元数据
        
        Args:
            text: 文档文本
            source: 文档来源
            additional_metadata: 额外的元数据
            
        Returns:
            处理后的文档块列表，每个包含text和metadata
        """
        if not text:
            return []
        
        # 分割文档
        chunks = self.split_text(text)
        
        # 提取基础元数据
        base_metadata = self.extract_metadata(text, source)
        
        # 合并额外元数据
        if additional_metadata:
            base_metadata.update(additional_metadata)
        
        # 为每个块创建元数据
        processed_chunks = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = base_metadata.copy()
            chunk_metadata.update({
                "chunk_index": i,
                "chunk_count": len(chunks),
                "chunk_length": len(chunk),
                "chunk_token_count": self.count_tokens(chunk)
            })
            
            processed_chunks.append({
                "text": chunk,
                "metadata": chunk_metadata
            })
        
        return processed_chunks