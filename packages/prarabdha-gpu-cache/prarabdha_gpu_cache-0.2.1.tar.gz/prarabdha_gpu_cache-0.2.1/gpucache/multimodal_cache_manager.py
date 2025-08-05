#!/usr/bin/env python3
"""
Unified Multimodal Cache Manager
Coordinates caching across text, video, audio, and image modalities
"""

import time
import threading
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
import numpy as np
from .core.hash import stable_hash
from .core.vector_index import SemanticVectorIndex
from .normalizer.semantic_input_cache import SemanticInputCache
from .video.video_cache import VideoSegmentCache
from .audio.audio_cache import AudioSegmentCache


@dataclass
class MultimodalEntry:
    """Unified multimodal cache entry."""
    modality: str  # 'text', 'video', 'audio', 'image'
    content_id: str
    original_content: Any
    normalized_content: str
    embedding: np.ndarray
    response: str
    metadata: Dict[str, Any]
    created_at: float
    last_accessed: float
    access_count: int
    cluster_id: Optional[str]


class MultimodalCacheManager:
    """Unified cache manager for all modalities."""
    
    def __init__(
        self,
        similarity_threshold: float = 0.85,
        max_entries_per_modality: int = 10000,
        enable_cross_modal_search: bool = True
    ):
        self.similarity_threshold = similarity_threshold
        self.max_entries_per_modality = max_entries_per_modality
        self.enable_cross_modal_search = enable_cross_modal_search
        
        # Modality-specific caches
        self.text_cache = SemanticInputCache(similarity_threshold=similarity_threshold)
        self.video_cache = VideoSegmentCache(similarity_threshold=similarity_threshold)
        self.audio_cache = AudioSegmentCache(similarity_threshold=similarity_threshold)
        
        # Unified storage
        self.entries: Dict[str, MultimodalEntry] = {}
        self.unified_vector_index = SemanticVectorIndex(dimension=768)
        self.lock = threading.RLock()
        
        # Cross-modal search
        self.cross_modal_embeddings: Dict[str, np.ndarray] = {}
        
        # Statistics
        self.stats = {
            'text_hits': 0,
            'video_hits': 0,
            'audio_hits': 0,
            'cross_modal_hits': 0,
            'misses': 0,
            'total_entries': 0
        }
    
    def _create_cross_modal_embedding(self, content: Any, modality: str) -> np.ndarray:
        """Create unified embedding for cross-modal search."""
        # Simple hash-based embedding for demo
        # In production, use proper multimodal models
        content_str = str(content)
        hash_value = stable_hash(f"{modality}:{content_str}")
        embedding = np.zeros(768, dtype=np.float32)
        
        for i in range(768):
            embedding[i] = (hash_value >> (i % 32)) & 1
        
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        
        return embedding
    
    def _generate_entry_id(self, content: Any, modality: str) -> str:
        """Generate unique entry ID."""
        content_str = str(content)
        return stable_hash(f"{modality}:{content_str}")
    
    def cache_text(self, prompt: str, response: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Cache text content."""
        with self.lock:
            # Cache in text-specific cache
            text_result = self.text_cache.put(prompt, response, metadata)
            
            # Create unified entry
            entry_id = self._generate_entry_id(prompt, 'text')
            cross_modal_embedding = self._create_cross_modal_embedding(prompt, 'text')
            
            entry = MultimodalEntry(
                modality='text',
                content_id=text_result['entry_id'],
                original_content=prompt,
                normalized_content=self.text_cache.normalizer.normalize(prompt),
                embedding=cross_modal_embedding,
                response=response,
                metadata=metadata or {},
                created_at=time.time(),
                last_accessed=time.time(),
                access_count=1,
                cluster_id=text_result.get('cluster_id')
            )
            
            self.entries[entry_id] = entry
            self.cross_modal_embeddings[entry_id] = cross_modal_embedding
            self.stats['total_entries'] += 1
            
            return {
                'success': True,
                'entry_id': entry_id,
                'modality': 'text',
                'text_cache_id': text_result['entry_id']
            }
    
    def cache_video_frame(self, frame: np.ndarray, description: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Cache video frame."""
        with self.lock:
            # Cache in video-specific cache
            video_result = self.video_cache.put_frame(frame, description)
            
            # Create unified entry
            entry_id = self._generate_entry_id(frame.tobytes(), 'video')
            cross_modal_embedding = self._create_cross_modal_embedding(frame.tobytes(), 'video')
            
            entry = MultimodalEntry(
                modality='video',
                content_id=video_result['frame_id'],
                original_content=frame,
                normalized_content=description,
                embedding=cross_modal_embedding,
                response=description,
                metadata=metadata or {},
                created_at=time.time(),
                last_accessed=time.time(),
                access_count=1,
                cluster_id=None
            )
            
            self.entries[entry_id] = entry
            self.cross_modal_embeddings[entry_id] = cross_modal_embedding
            self.stats['total_entries'] += 1
            
            return {
                'success': True,
                'entry_id': entry_id,
                'modality': 'video',
                'video_cache_id': video_result['frame_id']
            }
    
    def cache_audio_segment(self, waveform: np.ndarray, sample_rate: int, description: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Cache audio segment."""
        with self.lock:
            # Cache in audio-specific cache
            audio_result = self.audio_cache.put_segment(waveform, sample_rate, description)
            
            # Create unified entry
            entry_id = self._generate_entry_id(waveform.tobytes(), 'audio')
            cross_modal_embedding = self._create_cross_modal_embedding(waveform.tobytes(), 'audio')
            
            entry = MultimodalEntry(
                modality='audio',
                content_id=audio_result['segment_id'],
                original_content=waveform,
                normalized_content=description,
                embedding=cross_modal_embedding,
                response=description,
                metadata=metadata or {},
                created_at=time.time(),
                last_accessed=time.time(),
                access_count=1,
                cluster_id=None
            )
            
            self.entries[entry_id] = entry
            self.cross_modal_embeddings[entry_id] = cross_modal_embedding
            self.stats['total_entries'] += 1
            
            return {
                'success': True,
                'entry_id': entry_id,
                'modality': 'audio',
                'audio_cache_id': audio_result['segment_id']
            }
    
    def get_text(self, prompt: str) -> Optional[str]:
        """Get text response."""
        with self.lock:
            # Try text-specific cache first
            response = self.text_cache.get(prompt)
            if response:
                self.stats['text_hits'] += 1
                return response
            
            # Try cross-modal search
            if self.enable_cross_modal_search:
                cross_modal_result = self._cross_modal_search(prompt, 'text')
                if cross_modal_result:
                    self.stats['cross_modal_hits'] += 1
                    return cross_modal_result['response']
            
            self.stats['misses'] += 1
            return None
    
    def get_video_frame(self, frame: np.ndarray) -> Optional[str]:
        """Get video frame description."""
        with self.lock:
            # Try video-specific cache first
            description = self.video_cache.get_similar_frame(frame)
            if description:
                self.stats['video_hits'] += 1
                return description
            
            # Try cross-modal search
            if self.enable_cross_modal_search:
                cross_modal_result = self._cross_modal_search(frame.tobytes(), 'video')
                if cross_modal_result:
                    self.stats['cross_modal_hits'] += 1
                    return cross_modal_result['response']
            
            self.stats['misses'] += 1
            return None
    
    def get_audio_segment(self, waveform: np.ndarray, sample_rate: int) -> Optional[str]:
        """Get audio segment description."""
        with self.lock:
            # Try audio-specific cache first
            description = self.audio_cache.get_similar_segment(waveform, sample_rate)
            if description:
                self.stats['audio_hits'] += 1
                return description
            
            # Try cross-modal search
            if self.enable_cross_modal_search:
                cross_modal_result = self._cross_modal_search(waveform.tobytes(), 'audio')
                if cross_modal_result:
                    self.stats['cross_modal_hits'] += 1
                    return cross_modal_result['response']
            
            self.stats['misses'] += 1
            return None
    
    def _cross_modal_search(self, query_content: Any, target_modality: str) -> Optional[Dict[str, Any]]:
        """Search across modalities."""
        query_embedding = self._create_cross_modal_embedding(query_content, target_modality)
        
        best_match = None
        best_similarity = 0.0
        
        for entry_id, entry in self.entries.items():
            if entry.modality == target_modality:
                similarity = np.dot(query_embedding, entry.embedding)
                if similarity > best_similarity and similarity >= self.similarity_threshold:
                    best_similarity = similarity
                    best_match = entry
        
        if best_match:
            best_match.last_accessed = time.time()
            best_match.access_count += 1
            
            return {
                'response': best_match.response,
                'modality': best_match.modality,
                'similarity': best_similarity,
                'metadata': best_match.metadata
            }
        
        return None
    
    def cross_modal_search(self, query: str, modality: str = 'all') -> List[Dict[str, Any]]:
        """Search across all modalities or specific modality."""
        with self.lock:
            query_embedding = self._create_cross_modal_embedding(query, 'text')
            
            results = []
            for entry_id, entry in self.entries.items():
                if modality == 'all' or entry.modality == modality:
                    similarity = np.dot(query_embedding, entry.embedding)
                    if similarity >= self.similarity_threshold:
                        results.append({
                            'entry_id': entry_id,
                            'modality': entry.modality,
                            'content': entry.normalized_content,
                            'response': entry.response,
                            'similarity': similarity,
                            'metadata': entry.metadata
                        })
            
            # Sort by similarity
            results.sort(key=lambda x: x['similarity'], reverse=True)
            return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get unified cache statistics."""
        with self.lock:
            total_hits = (self.stats['text_hits'] + self.stats['video_hits'] + 
                         self.stats['audio_hits'] + self.stats['cross_modal_hits'])
            total_requests = total_hits + self.stats['misses']
            hit_rate = total_hits / total_requests if total_requests > 0 else 0.0
            
            # Get modality-specific stats
            text_stats = self.text_cache.get_stats()
            video_stats = self.video_cache.get_stats()
            audio_stats = self.audio_cache.get_stats()
            
            return {
                'total_entries': self.stats['total_entries'],
                'hit_rate': hit_rate,
                'text_hits': self.stats['text_hits'],
                'video_hits': self.stats['video_hits'],
                'audio_hits': self.stats['audio_hits'],
                'cross_modal_hits': self.stats['cross_modal_hits'],
                'misses': self.stats['misses'],
                'text_cache_stats': text_stats,
                'video_cache_stats': video_stats,
                'audio_cache_stats': audio_stats,
                'cross_modal_search_enabled': self.enable_cross_modal_search
            }
    
    def clear(self):
        """Clear all cache entries."""
        with self.lock:
            self.entries.clear()
            self.cross_modal_embeddings.clear()
            self.text_cache.clear()
            self.video_cache.clear()
            self.audio_cache.clear()
            self.stats = {
                'text_hits': 0,
                'video_hits': 0,
                'audio_hits': 0,
                'cross_modal_hits': 0,
                'misses': 0,
                'total_entries': 0
            }
    
    def export_cache_data(self, format: str = 'json') -> Dict[str, Any]:
        """Export cache data for analysis."""
        with self.lock:
            export_data = {
                'metadata': {
                    'export_time': time.time(),
                    'total_entries': len(self.entries),
                    'modalities': list(set(entry.modality for entry in self.entries.values())),
                    'stats': self.stats
                },
                'entries': []
            }
            
            for entry_id, entry in self.entries.items():
                export_entry = {
                    'entry_id': entry_id,
                    'modality': entry.modality,
                    'content_id': entry.content_id,
                    'normalized_content': entry.normalized_content,
                    'response': entry.response,
                    'metadata': entry.metadata,
                    'created_at': entry.created_at,
                    'last_accessed': entry.last_accessed,
                    'access_count': entry.access_count,
                    'cluster_id': entry.cluster_id
                }
                export_data['entries'].append(export_entry)
            
            return export_data 