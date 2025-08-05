#!/usr/bin/env python3
"""
Semantic Input Cache with Enhanced Prompt Normalization
Implements advanced noise removal and paraphrase detection for input-level caching
"""

import re
import threading
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import numpy as np
from ..core.hash import stable_hash
from ..core.vector_index import SemanticVectorIndex
import time


@dataclass
class SemanticEntry:
    """Semantic cache entry with enhanced normalization."""
    original_prompt: str
    normalized_prompt: str
    response: str
    embedding: np.ndarray
    cluster_id: Optional[str]
    created_at: float
    access_count: int
    metadata: Dict[str, Any]


class EnhancedPromptNormalizer:
    """Advanced prompt normalization with domain-specific rules."""
    
    def __init__(self):
        # Common noise patterns
        self.noise_patterns = [
            r'\b(please|can you|could you|would you|will you)\b',
            r'\b(i want to|i need to|i would like to)\b',
            r'\b(tell me|show me|give me|help me)\b',
            r'\b(thanks|thank you|thx)\b',
            r'\b(hi|hello|hey)\b',
            r'\b(bye|goodbye|see you)\b',
            r'\s+',  # Multiple spaces
            r'[^\w\s]',  # Punctuation (keep some)
        ]
        
        # Domain-specific synonyms
        self.synonym_groups = {
            'explain': ['explain', 'describe', 'tell me about', 'what is', 'define'],
            'summarize': ['summarize', 'sum up', 'brief', 'overview', 'summary'],
            'compare': ['compare', 'difference', 'versus', 'vs', 'contrast'],
            'analyze': ['analyze', 'examine', 'study', 'investigate', 'look at'],
            'create': ['create', 'make', 'generate', 'build', 'develop'],
            'find': ['find', 'search', 'locate', 'discover', 'get'],
            'show': ['show', 'display', 'present', 'demonstrate', 'illustrate'],
            'help': ['help', 'assist', 'support', 'guide', 'aid']
        }
        
        # Compile patterns
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.noise_patterns]
    
    def normalize(self, prompt: str) -> str:
        """Enhanced prompt normalization."""
        normalized = prompt.lower().strip()
        
        # Remove noise patterns
        for pattern in self.compiled_patterns:
            normalized = pattern.sub(' ', normalized)
        
        # Normalize whitespace
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        # Apply synonym normalization
        normalized = self._apply_synonym_normalization(normalized)
        
        return normalized
    
    def _apply_synonym_normalization(self, text: str) -> str:
        """Apply synonym group normalization."""
        words = text.split()
        normalized_words = []
        
        for word in words:
            # Find if word belongs to any synonym group
            normalized_word = word
            for group_name, synonyms in self.synonym_groups.items():
                if word in synonyms:
                    normalized_word = group_name
                    break
            normalized_words.append(normalized_word)
        
        return ' '.join(normalized_words)


class ParaphraseDetector:
    """Multi-strategy paraphrase detection engine."""
    
    def __init__(self, similarity_threshold: float = 0.85):
        self.similarity_threshold = similarity_threshold
        self.normalizer = EnhancedPromptNormalizer()
        
        # Paraphrase patterns
        self.paraphrase_patterns = [
            (r'\b(what is|what\'s)\b', 'define'),
            (r'\b(how to|how do i)\b', 'explain'),
            (r'\b(give me|show me)\b', 'explain'),
            (r'\b(tell me about|describe)\b', 'explain'),
            (r'\b(make|create|generate)\b', 'create'),
            (r'\b(find|search|get)\b', 'find'),
            (r'\b(compare|difference|vs)\b', 'compare'),
            (r'\b(analyze|examine|study)\b', 'analyze'),
        ]
        
        self.compiled_paraphrase_patterns = [
            (re.compile(pattern, re.IGNORECASE), replacement)
            for pattern, replacement in self.paraphrase_patterns
        ]
    
    def detect_paraphrase(self, prompt1: str, prompt2: str) -> Tuple[bool, float]:
        """Detect if two prompts are paraphrases."""
        # Normalize both prompts
        norm1 = self.normalizer.normalize(prompt1)
        norm2 = self.normalizer.normalize(prompt2)
        
        # Exact match after normalization
        if norm1 == norm2:
            return True, 1.0
        
        # Apply paraphrase patterns
        norm1_paraphrased = self._apply_paraphrase_patterns(norm1)
        norm2_paraphrased = self._apply_paraphrase_patterns(norm2)
        
        if norm1_paraphrased == norm2_paraphrased:
            return True, 0.95
        
        # Calculate word overlap similarity
        words1 = set(norm1.split())
        words2 = set(norm2.split())
        
        if not words1 and not words2:
            return True, 1.0
        elif not words1 or not words2:
            return False, 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        similarity = len(intersection) / len(union)
        
        return similarity >= self.similarity_threshold, similarity
    
    def _apply_paraphrase_patterns(self, text: str) -> str:
        """Apply paraphrase patterns to text."""
        for pattern, replacement in self.compiled_paraphrase_patterns:
            text = pattern.sub(replacement, text)
        return text


class SemanticInputCache:
    """Advanced semantic input cache with enhanced normalization."""
    
    def __init__(
        self,
        similarity_threshold: float = 0.85,
        max_size: int = 10000,
        enable_clustering: bool = True
    ):
        self.similarity_threshold = similarity_threshold
        self.max_size = max_size
        self.enable_clustering = enable_clustering
        
        self.entries: Dict[str, SemanticEntry] = {}
        self.normalizer = EnhancedPromptNormalizer()
        self.paraphrase_detector = ParaphraseDetector(similarity_threshold)
        self.vector_index = SemanticVectorIndex(dimension=768)
        self.lock = threading.RLock()
        
        # Clustering
        self.clusters: Dict[str, List[str]] = {}
        self.cluster_embeddings: Dict[str, np.ndarray] = {}
        
        self.stats = {
            'hits': 0,
            'misses': 0,
            'paraphrase_hits': 0,
            'clusters': 0
        }
    
    def _create_vector_embedding(self, text: str) -> np.ndarray:
        """Create vector embedding for text."""
        # Simple hash-based embedding for demo
        # In production, use proper sentence transformers
        hash_value = stable_hash(text)
        embedding = np.zeros(768, dtype=np.float32)
        
        # Distribute hash across embedding dimensions
        for i in range(768):
            embedding[i] = (hash_value >> (i % 32)) & 1
        
        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        
        return embedding
    
    def _find_similar_cluster(self, embedding: np.ndarray) -> Optional[str]:
        """Find similar cluster for embedding."""
        if not self.clusters:
            return None
        
        best_cluster = None
        best_similarity = 0.0
        
        for cluster_id, cluster_embedding in self.cluster_embeddings.items():
            similarity = np.dot(embedding, cluster_embedding)
            if similarity > best_similarity and similarity >= self.similarity_threshold:
                best_similarity = similarity
                best_cluster = cluster_id
        
        return best_cluster
    
    def _create_or_update_cluster(self, entry_id: str, embedding: np.ndarray):
        """Create or update cluster for entry."""
        if not self.enable_clustering:
            return None
        
        # Find similar cluster
        cluster_id = self._find_similar_cluster(embedding)
        
        if cluster_id:
            # Add to existing cluster
            self.clusters[cluster_id].append(entry_id)
            
            # Update cluster embedding (average)
            cluster_entries = [self.entries[entry_id] for entry_id in self.clusters[cluster_id]]
            cluster_embeddings = [entry.embedding for entry in cluster_entries]
            self.cluster_embeddings[cluster_id] = np.mean(cluster_embeddings, axis=0)
            
            return cluster_id
        else:
            # Create new cluster
            cluster_id = f"cluster_{len(self.clusters)}"
            self.clusters[cluster_id] = [entry_id]
            self.cluster_embeddings[cluster_id] = embedding
            self.stats['clusters'] += 1
            
            return cluster_id
    
    def _evict_entries(self, required_space: int = 1):
        """Evict entries when cache is full."""
        if len(self.entries) + required_space <= self.max_size:
            return
        
        # Simple LRU eviction
        # In production, use more sophisticated eviction strategies
        entries_to_remove = len(self.entries) + required_space - self.max_size
        
        # Sort by access count (least accessed first)
        sorted_entries = sorted(
            self.entries.items(),
            key=lambda x: x[1].access_count
        )
        
        for i in range(entries_to_remove):
            if i < len(sorted_entries):
                entry_id, entry = sorted_entries[i]
                del self.entries[entry_id]
                
                # Remove from clusters
                if entry.cluster_id and entry.cluster_id in self.clusters:
                    if entry_id in self.clusters[entry.cluster_id]:
                        self.clusters[entry.cluster_id].remove(entry_id)
    
    def put(self, prompt: str, response: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Cache prompt with semantic normalization."""
        with self.lock:
            # Normalize prompt
            normalized_prompt = self.normalizer.normalize(prompt)
            
            # Create embedding
            embedding = self._create_vector_embedding(normalized_prompt)
            
            # Generate entry ID
            entry_id = stable_hash(normalized_prompt)
            
            # Check if already exists
            if entry_id in self.entries:
                # Update existing entry
                entry = self.entries[entry_id]
                entry.response = response
                entry.access_count += 1
                entry.metadata.update(metadata or {})
                
                return {
                    'success': True,
                    'entry_id': entry_id,
                    'action': 'updated',
                    'cluster_id': entry.cluster_id
                }
            
            # Evict if necessary
            self._evict_entries()
            
            # Create new entry
            entry = SemanticEntry(
                original_prompt=prompt,
                normalized_prompt=normalized_prompt,
                response=response,
                embedding=embedding,
                cluster_id=None,
                created_at=time.time(),
                access_count=1,
                metadata=metadata or {}
            )
            
            # Add to cache
            self.entries[entry_id] = entry
            
            # Create or update cluster
            cluster_id = self._create_or_update_cluster(entry_id, embedding)
            entry.cluster_id = cluster_id
            
            return {
                'success': True,
                'entry_id': entry_id,
                'action': 'created',
                'cluster_id': cluster_id,
                'normalized_prompt': normalized_prompt
            }
    
    def get(self, prompt: str) -> Optional[str]:
        """Get response for prompt with paraphrase detection."""
        with self.lock:
            # Normalize prompt
            normalized_prompt = self.normalizer.normalize(prompt)
            
            # First, try exact match
            entry_id = stable_hash(normalized_prompt)
            if entry_id in self.entries:
                entry = self.entries[entry_id]
                entry.access_count += 1
                self.stats['hits'] += 1
                return entry.response
            
            # Try paraphrase detection
            best_match = None
            best_similarity = 0.0
            
            for existing_entry in self.entries.values():
                is_paraphrase, similarity = self.paraphrase_detector.detect_paraphrase(
                    prompt, existing_entry.original_prompt
                )
                
                if is_paraphrase and similarity > best_similarity:
                    best_match = existing_entry
                    best_similarity = similarity
            
            if best_match:
                best_match.access_count += 1
                self.stats['paraphrase_hits'] += 1
                return best_match.response
            
            # Try vector similarity search
            query_embedding = self._create_vector_embedding(normalized_prompt)
            
            # Search in vector index
            similar_entries = self.vector_index.search(query_embedding, k=5)
            
            for entry_id, similarity in similar_entries:
                if entry_id in self.entries and similarity >= self.similarity_threshold:
                    entry = self.entries[entry_id]
                    entry.access_count += 1
                    self.stats['hits'] += 1
                    return entry.response
            
            self.stats['misses'] += 1
            return None
    
    def get_with_metadata(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Get response with metadata."""
        with self.lock:
            # Normalize prompt
            normalized_prompt = self.normalizer.normalize(prompt)
            
            # First, try exact match
            entry_id = stable_hash(normalized_prompt)
            if entry_id in self.entries:
                entry = self.entries[entry_id]
                entry.access_count += 1
                self.stats['hits'] += 1
                
                return {
                    'response': entry.response,
                    'original_prompt': entry.original_prompt,
                    'normalized_prompt': entry.normalized_prompt,
                    'cluster_id': entry.cluster_id,
                    'access_count': entry.access_count,
                    'metadata': entry.metadata,
                    'match_type': 'exact'
                }
            
            # Try paraphrase detection
            best_match = None
            best_similarity = 0.0
            
            for existing_entry in self.entries.values():
                is_paraphrase, similarity = self.paraphrase_detector.detect_paraphrase(
                    prompt, existing_entry.original_prompt
                )
                
                if is_paraphrase and similarity > best_similarity:
                    best_match = existing_entry
                    best_similarity = similarity
            
            if best_match:
                best_match.access_count += 1
                self.stats['paraphrase_hits'] += 1
                
                return {
                    'response': best_match.response,
                    'original_prompt': best_match.original_prompt,
                    'normalized_prompt': best_match.normalized_prompt,
                    'cluster_id': best_match.cluster_id,
                    'access_count': best_match.access_count,
                    'metadata': best_match.metadata,
                    'match_type': 'paraphrase',
                    'similarity': best_similarity
                }
            
            self.stats['misses'] += 1
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self.lock:
            total_requests = self.stats['hits'] + self.stats['paraphrase_hits'] + self.stats['misses']
            hit_rate = (self.stats['hits'] + self.stats['paraphrase_hits']) / total_requests if total_requests > 0 else 0.0
            
            return {
                'total_entries': len(self.entries),
                'total_clusters': len(self.clusters),
                'hit_rate': hit_rate,
                'exact_hits': self.stats['hits'],
                'paraphrase_hits': self.stats['paraphrase_hits'],
                'misses': self.stats['misses'],
                'memory_utilization': len(self.entries) / self.max_size
            }
    
    def clear(self):
        """Clear all cache entries."""
        with self.lock:
            self.entries.clear()
            self.clusters.clear()
            self.cluster_embeddings.clear()
            self.vector_index.clear()
            self.stats = {
                'hits': 0,
                'misses': 0,
                'paraphrase_hits': 0,
                'clusters': 0
            }
    
    def get_cluster_info(self) -> Dict[str, Any]:
        """Get information about clusters."""
        with self.lock:
            cluster_info = {}
            for cluster_id, entry_ids in self.clusters.items():
                cluster_info[cluster_id] = {
                    'size': len(entry_ids),
                    'entries': [
                        {
                            'prompt': self.entries[entry_id].original_prompt,
                            'normalized': self.entries[entry_id].normalized_prompt,
                            'access_count': self.entries[entry_id].access_count
                        }
                        for entry_id in entry_ids
                    ]
                }
            
            return cluster_info 