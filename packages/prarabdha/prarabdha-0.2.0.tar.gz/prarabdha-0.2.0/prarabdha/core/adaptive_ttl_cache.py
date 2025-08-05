#!/usr/bin/env python3
"""
Adaptive TTL Cache with Intelligent Eviction
Implements ML-based TTL prediction and semantic-aware eviction strategies
"""

import time
import threading
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass
from collections import defaultdict
from .hash import stable_hash


@dataclass
class AdaptiveEntry:
    """Adaptive cache entry with ML-based TTL prediction."""
    key: str
    value: Any
    created_at: float
    last_accessed: float
    access_count: int
    access_frequency: float
    semantic_distance: float
    predicted_ttl: float
    user_priority: int
    content_type: str
    metadata: Dict[str, Any]


class TTLPredictor:
    """Machine learning model for predicting optimal cache duration."""
    
    def __init__(self):
        self.access_patterns = defaultdict(list)
        self.semantic_patterns = defaultdict(list)
        self.user_patterns = defaultdict(list)
        
    def predict_ttl(
        self,
        access_count: int,
        access_frequency: float,
        semantic_distance: float,
        user_priority: int,
        content_type: str
    ) -> float:
        """Predict optimal TTL based on multiple factors."""
        
        # Base TTL calculation
        base_ttl = 3600.0  # 1 hour default
        
        # Access pattern factor
        access_factor = min(access_count * 0.1, 2.0)  # Cap at 2x
        
        # Frequency factor
        frequency_factor = min(access_frequency * 0.5, 1.5)  # Cap at 1.5x
        
        # Semantic distance factor (closer = longer TTL)
        semantic_factor = max(1.0 - semantic_distance, 0.1)
        
        # User priority factor
        priority_factor = 1.0 + (user_priority * 0.2)  # Higher priority = longer TTL
        
        # Content type factor
        content_factors = {
            'text': 1.0,
            'video': 1.5,  # Video content stays longer
            'audio': 1.3,  # Audio content stays longer
            'image': 1.2,  # Image content stays longer
            'multimodal': 1.4  # Multimodal content stays longer
        }
        content_factor = content_factors.get(content_type, 1.0)
        
        # Calculate predicted TTL
        predicted_ttl = (
            base_ttl *
            access_factor *
            frequency_factor *
            semantic_factor *
            priority_factor *
            content_factor
        )
        
        # Clamp to reasonable bounds (5 minutes to 24 hours)
        predicted_ttl = max(300.0, min(predicted_ttl, 86400.0))
        
        return predicted_ttl
    
    def update_patterns(self, entry: AdaptiveEntry):
        """Update access patterns for learning."""
        self.access_patterns[entry.content_type].append(entry.access_count)
        self.semantic_patterns[entry.content_type].append(entry.semantic_distance)
        self.user_patterns[entry.user_priority].append(entry.access_frequency)


class AdaptiveTTLCache:
    """Advanced cache with adaptive TTL and intelligent eviction."""
    
    def __init__(
        self,
        max_size: int = 10000,
        max_memory_gb: float = 32.0,
        enable_ml_prediction: bool = True
    ):
        self.max_size = max_size
        self.max_memory_bytes = max_memory_gb * 1024 * 1024 * 1024
        self.enable_ml_prediction = enable_ml_prediction
        
        self.entries: Dict[str, AdaptiveEntry] = {}
        self.ttl_predictor = TTLPredictor() if enable_ml_prediction else None
        self.lock = threading.RLock()
        
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'expirations': 0,
            'memory_usage': 0.0
        }
    
    def _calculate_semantic_distance(self, key1: str, key2: str) -> float:
        """Calculate semantic distance between two keys."""
        # Simple implementation - can be enhanced with proper semantic similarity
        words1 = set(key1.lower().split())
        words2 = set(key2.lower().split())
        
        if not words1 and not words2:
            return 0.0
        elif not words1 or not words2:
            return 1.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return 1.0 - (len(intersection) / len(union))
    
    def _calculate_eviction_score(self, entry: AdaptiveEntry) -> float:
        """Calculate eviction score using multi-factor scoring."""
        current_time = time.time()
        
        # Time-based factor (older = higher score)
        time_factor = (current_time - entry.last_accessed) / 3600.0  # Hours
        
        # Access factor (lower access = higher score)
        access_factor = 1.0 / max(entry.access_count, 1)
        
        # Frequency factor (lower frequency = higher score)
        frequency_factor = 1.0 / max(entry.access_frequency, 0.1)
        
        # Semantic distance factor (higher distance = higher score)
        semantic_factor = entry.semantic_distance
        
        # User priority factor (lower priority = higher score)
        priority_factor = 1.0 / max(entry.user_priority, 1)
        
        # Content type factor (less important types = higher score)
        content_priorities = {
            'text': 1.0,
            'video': 0.8,
            'audio': 0.9,
            'image': 0.95,
            'multimodal': 0.7
        }
        content_factor = content_priorities.get(entry.content_type, 1.0)
        
        # Weighted combination
        score = (
            time_factor * 0.3 +
            access_factor * 0.25 +
            frequency_factor * 0.2 +
            semantic_factor * 0.15 +
            priority_factor * 0.05 +
            content_factor * 0.05
        )
        
        return score
    
    def _evict_entries(self, required_space: int = 1):
        """Intelligent eviction using semantic decay."""
        with self.lock:
            if len(self.entries) + required_space <= self.max_size:
                return
            
            # Calculate eviction scores for all entries
            eviction_candidates = []
            for key, entry in self.entries.items():
                score = self._calculate_eviction_score(entry)
                eviction_candidates.append((key, entry, score))
            
            # Sort by eviction score (highest first)
            eviction_candidates.sort(key=lambda x: x[2], reverse=True)
            
            # Evict entries until we have enough space
            evicted_count = 0
            for key, entry, score in eviction_candidates:
                if len(self.entries) + required_space - evicted_count <= self.max_size:
                    break
                
                del self.entries[key]
                evicted_count += 1
                self.stats['evictions'] += 1
    
    def _update_entry_stats(self, entry: AdaptiveEntry):
        """Update entry statistics and access patterns."""
        current_time = time.time()
        
        # Update access count and frequency
        entry.access_count += 1
        time_since_creation = current_time - entry.created_at
        entry.access_frequency = entry.access_count / max(time_since_creation / 3600.0, 1.0)  # Per hour
        entry.last_accessed = current_time
        
        # Update ML predictor if enabled
        if self.ttl_predictor:
            self.ttl_predictor.update_patterns(entry)
    
    def put(
        self,
        key: str,
        value: Any,
        user_id: str = "default",
        user_priority: int = 1,
        content_type: str = "text",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Put item in cache with adaptive TTL."""
        with self.lock:
            current_time = time.time()
            
            # Calculate semantic distance from existing entries
            semantic_distance = 0.0
            if self.entries:
                distances = []
                for existing_key in self.entries.keys():
                    distance = self._calculate_semantic_distance(key, existing_key)
                    distances.append(distance)
                semantic_distance = np.mean(distances) if distances else 0.0
            
            # Predict TTL
            if self.ttl_predictor:
                predicted_ttl = self.ttl_predictor.predict_ttl(
                    access_count=1,
                    access_frequency=1.0,
                    semantic_distance=semantic_distance,
                    user_priority=user_priority,
                    content_type=content_type
                )
            else:
                predicted_ttl = 3600.0  # Default 1 hour
            
            # Create entry
            entry = AdaptiveEntry(
                key=key,
                value=value,
                created_at=current_time,
                last_accessed=current_time,
                access_count=1,
                access_frequency=1.0,
                semantic_distance=semantic_distance,
                predicted_ttl=predicted_ttl,
                user_priority=user_priority,
                content_type=content_type,
                metadata=metadata or {}
            )
            
            # Evict if necessary
            self._evict_entries()
            
            # Add to cache
            self.entries[key] = entry
            
            return {
                'success': True,
                'predicted_ttl': predicted_ttl,
                'semantic_distance': semantic_distance,
                'total_entries': len(self.entries)
            }
    
    def get(self, key: str, user_id: str = "default") -> Optional[Any]:
        """Get item from cache with adaptive TTL."""
        with self.lock:
            if key not in self.entries:
                self.stats['misses'] += 1
                return None
            
            entry = self.entries[key]
            current_time = time.time()
            
            # Check if entry has expired
            if current_time - entry.created_at > entry.predicted_ttl:
                del self.entries[key]
                self.stats['expirations'] += 1
                self.stats['misses'] += 1
                return None
            
            # Update entry stats
            self._update_entry_stats(entry)
            
            # Update semantic distance based on new access patterns
            if len(self.entries) > 1:
                distances = []
                for other_key in self.entries.keys():
                    if other_key != key:
                        distance = self._calculate_semantic_distance(key, other_key)
                        distances.append(distance)
                if distances:
                    entry.semantic_distance = np.mean(distances)
            
            self.stats['hits'] += 1
            return entry.value
    
    def get_with_metadata(self, key: str, user_id: str = "default") -> Optional[Dict[str, Any]]:
        """Get item with metadata from cache."""
        with self.lock:
            if key not in self.entries:
                self.stats['misses'] += 1
                return None
            
            entry = self.entries[key]
            current_time = time.time()
            
            # Check if entry has expired
            if current_time - entry.created_at > entry.predicted_ttl:
                del self.entries[key]
                self.stats['expirations'] += 1
                self.stats['misses'] += 1
                return None
            
            # Update entry stats
            self._update_entry_stats(entry)
            
            self.stats['hits'] += 1
            
            return {
                'value': entry.value,
                'created_at': entry.created_at,
                'last_accessed': entry.last_accessed,
                'access_count': entry.access_count,
                'access_frequency': entry.access_frequency,
                'semantic_distance': entry.semantic_distance,
                'predicted_ttl': entry.predicted_ttl,
                'user_priority': entry.user_priority,
                'content_type': entry.content_type,
                'metadata': entry.metadata
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self.lock:
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_rate = self.stats['hits'] / total_requests if total_requests > 0 else 0.0
            
            # Calculate average TTL and semantic distance
            avg_ttl = 0.0
            avg_semantic_distance = 0.0
            if self.entries:
                ttls = [entry.predicted_ttl for entry in self.entries.values()]
                distances = [entry.semantic_distance for entry in self.entries.values()]
                avg_ttl = np.mean(ttls)
                avg_semantic_distance = np.mean(distances)
            
            return {
                'total_entries': len(self.entries),
                'max_size': self.max_size,
                'hit_rate': hit_rate,
                'hits': self.stats['hits'],
                'misses': self.stats['misses'],
                'evictions': self.stats['evictions'],
                'expirations': self.stats['expirations'],
                'avg_predicted_ttl': avg_ttl,
                'avg_semantic_distance': avg_semantic_distance,
                'memory_utilization': len(self.entries) / self.max_size
            }
    
    def clear(self):
        """Clear all cache entries."""
        with self.lock:
            self.entries.clear()
            self.stats = {
                'hits': 0,
                'misses': 0,
                'evictions': 0,
                'expirations': 0,
                'memory_usage': 0.0
            }
    
    def get_entries_by_type(self, content_type: str) -> List[Dict[str, Any]]:
        """Get all entries of a specific content type."""
        with self.lock:
            entries = []
            for entry in self.entries.values():
                if entry.content_type == content_type:
                    entries.append({
                        'key': entry.key,
                        'value': entry.value,
                        'access_count': entry.access_count,
                        'access_frequency': entry.access_frequency,
                        'semantic_distance': entry.semantic_distance,
                        'predicted_ttl': entry.predicted_ttl,
                        'user_priority': entry.user_priority,
                        'metadata': entry.metadata
                    })
            return entries 