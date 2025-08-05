"""
Enhanced Binary Sniffer analyzer with improved detection
"""

import logging
from pathlib import Path
from typing import Union, Optional, List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed

from .config import Config
from .results import AnalysisResult, ComponentMatch
from ..extractors.factory import ExtractorFactory
from ..matchers.progressive import ProgressiveMatcher
from ..matchers.direct import DirectMatcher
from ..storage.database import SignatureDatabase
from ..signatures.manager import SignatureManager


logger = logging.getLogger(__name__)


class EnhancedBinarySniffer:
    """
    Enhanced main analyzer class with improved detection capabilities.
    Uses both progressive and direct matching for better results.
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the analyzer.
        
        Args:
            config: Configuration object (uses default if not provided)
        """
        self.config = config or Config()
        
        # Initialize components
        self.db = SignatureDatabase(self.config.db_path)
        self.extractor_factory = ExtractorFactory()
        self.progressive_matcher = ProgressiveMatcher(self.config)
        self.direct_matcher = DirectMatcher(self.config)
        self.signature_manager = SignatureManager(self.config, self.db)
        # Updater is handled by regular analyzer if needed
        
        # Check if database needs initialization
        if not self.db.is_initialized():
            logger.info("Initializing signature database...")
            self._initialize_database()
    
    def analyze_file(
        self, 
        file_path: Union[str, Path],
        confidence_threshold: Optional[float] = None,
        deep_analysis: bool = False
    ) -> AnalysisResult:
        """
        Analyze a single file for OSS components using enhanced detection.
        
        Args:
            file_path: Path to the file to analyze
            confidence_threshold: Minimum confidence score (0.0-1.0)
            deep_analysis: Enable deep analysis mode
            
        Returns:
            AnalysisResult object containing matches and metadata
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        logger.info(f"Analyzing file: {file_path}")
        
        # Extract features from file
        extractor = self.extractor_factory.get_extractor(file_path)
        features = extractor.extract(file_path)
        
        # Use lower default threshold for better detection
        threshold = confidence_threshold or 0.3
        
        # Try progressive matching first
        progressive_matches = self.progressive_matcher.match(
            features, 
            threshold=threshold,
            deep=deep_analysis
        )
        
        # Always use direct matching for better detection
        direct_matches = self.direct_matcher.match(
            features,
            threshold=threshold,
            deep=deep_analysis
        )
        
        # Merge matches, keeping highest confidence for each component
        merged_matches = self._merge_matches(progressive_matches, direct_matches)
        
        # Build result
        total_time = self.progressive_matcher.last_analysis_time + self.direct_matcher.last_analysis_time
        
        return AnalysisResult(
            file_path=str(file_path),
            file_size=file_path.stat().st_size,
            file_type=features.file_type,
            matches=merged_matches,
            analysis_time=total_time,
            features_extracted=len(features.strings) + len(features.symbols),
            confidence_threshold=threshold
        )
    
    def _merge_matches(
        self,
        progressive_matches: List[ComponentMatch],
        direct_matches: List[ComponentMatch]
    ) -> List[ComponentMatch]:
        """Merge matches from different matchers, keeping highest confidence"""
        component_map = {}
        
        # Process all matches
        for match in progressive_matches + direct_matches:
            key = match.component
            
            if key not in component_map:
                component_map[key] = match
            else:
                # Keep match with higher confidence
                if match.confidence > component_map[key].confidence:
                    component_map[key] = match
                elif match.confidence == component_map[key].confidence:
                    # Merge evidence
                    existing_evidence = component_map[key].evidence or {}
                    new_evidence = match.evidence or {}
                    
                    # Combine evidence
                    if 'signature_count' in existing_evidence and 'signature_count' in new_evidence:
                        existing_evidence['signature_count'] += new_evidence['signature_count']
                    
                    existing_evidence.update(new_evidence)
                    component_map[key].evidence = existing_evidence
        
        # Sort by confidence
        matches = list(component_map.values())
        matches.sort(key=lambda m: m.confidence, reverse=True)
        
        return matches
    
    def analyze_directory(
        self,
        directory_path: Union[str, Path],
        recursive: bool = True,
        file_patterns: Optional[List[str]] = None,
        confidence_threshold: Optional[float] = None,
        parallel: bool = True
    ) -> Dict[str, AnalysisResult]:
        """
        Analyze all files in a directory.
        
        Args:
            directory_path: Path to directory
            recursive: Analyze subdirectories
            file_patterns: List of glob patterns (e.g., ["*.exe", "*.so"])
            confidence_threshold: Minimum confidence score
            parallel: Use parallel processing
            
        Returns:
            Dictionary mapping file paths to results
        """
        directory_path = Path(directory_path)
        if not directory_path.is_dir():
            raise NotADirectoryError(f"Not a directory: {directory_path}")
        
        # Collect files
        files = self._collect_files(directory_path, recursive, file_patterns)
        logger.info(f"Found {len(files)} files to analyze")
        
        results = {}
        
        if parallel and len(files) > 1:
            # Parallel processing
            with ThreadPoolExecutor(max_workers=self.config.parallel_workers) as executor:
                future_to_file = {
                    executor.submit(
                        self.analyze_file, 
                        file, 
                        confidence_threshold
                    ): file 
                    for file in files
                }
                
                for future in as_completed(future_to_file):
                    file_path = future_to_file[future]
                    try:
                        result = future.result()
                        results[str(file_path)] = result
                    except Exception as e:
                        logger.error(f"Error analyzing {file_path}: {e}")
                        results[str(file_path)] = AnalysisResult.create_error(
                            str(file_path), str(e)
                        )
        else:
            # Sequential processing
            for file_path in files:
                try:
                    results[str(file_path)] = self.analyze_file(
                        file_path, 
                        confidence_threshold
                    )
                except Exception as e:
                    logger.error(f"Error analyzing {file_path}: {e}")
                    results[str(file_path)] = AnalysisResult.create_error(
                        str(file_path), str(e)
                    )
        
        return results
    
    def _collect_files(
        self,
        directory: Path,
        recursive: bool,
        patterns: Optional[List[str]] = None
    ) -> List[Path]:
        """Collect files from directory"""
        files = []
        
        if patterns:
            # Use glob patterns
            for pattern in patterns:
                if recursive:
                    files.extend(directory.rglob(pattern))
                else:
                    files.extend(directory.glob(pattern))
        else:
            # Get all files
            if recursive:
                files = [f for f in directory.rglob('*') if f.is_file()]
            else:
                files = [f for f in directory.iterdir() if f.is_file()]
        
        return sorted(set(files))
    
    def _initialize_database(self):
        """Initialize signature database with packaged signatures"""
        try:
            self.signature_manager.auto_import()
        except Exception as e:
            logger.error(f"Failed to initialize signature database: {e}")
    
    def get_signature_stats(self) -> Dict[str, any]:
        """Get signature database statistics"""
        return self.db.get_statistics()
    
    def check_updates(self) -> bool:
        """Check if signature updates are available"""
        # Update functionality not implemented in enhanced analyzer
        return False
    
    def update_signatures(self, force: bool = False) -> bool:
        """Update signature database"""
        # Update functionality not implemented in enhanced analyzer
        return False