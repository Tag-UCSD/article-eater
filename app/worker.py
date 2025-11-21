#!/usr/bin/env python3
"""
Article Eater v18.4 - Queue Worker
Minimal in-process worker that polls processing_queue and executes L0-L5 jobs
"""

import time
import logging
import json
import sys
from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SimpleWorker:
    """
    In-process worker for Article Eater v18.4
    Polls processing_queue database table and executes L0-L5 operations
    
    Production note: For distributed processing, replace with Celery/Redis/RQ
    """
    
    def __init__(self, poll_interval: int = 5, db_path: str = "./ae.db"):
        self.poll_interval = poll_interval
        self.running = False
        self.db_path = db_path
        self.processed_count = 0
        self.error_count = 0
        
    def start(self):
        """Main worker loop - polls queue and processes jobs"""
        self.running = True
        logger.info(f"Worker starting (poll_interval={self.poll_interval}s, db={self.db_path})")
        
        while self.running:
            try:
                job = self.fetch_next_job()
                if job:
                    self.process_job(job)
                    self.processed_count += 1
                else:
                    time.sleep(self.poll_interval)
                    
            except KeyboardInterrupt:
                logger.info(f"Worker stopping... (processed={self.processed_count}, errors={self.error_count})")
                self.running = False
            except Exception as e:
                logger.error(f"Worker error: {e}", exc_info=True)
                self.error_count += 1
                time.sleep(self.poll_interval)
    
    def fetch_next_job(self) -> Optional[Dict[str, Any]]:
        """
        Poll processing_queue for highest priority pending job
        
        Returns:
            Job dict with keys: job_id, job_type, params, priority
            None if queue empty
        """
        try:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get highest priority pending job (with lock)
            cursor.execute("""
                SELECT job_id, job_type, params, priority, created_at
                FROM processing_queue
                WHERE status = 'pending'
                ORDER BY priority DESC, created_at ASC
                LIMIT 1
            """)
            
            row = cursor.fetchone()
            if not row:
                conn.close()
                return None
            
            job = dict(row)
            
            # Mark as running
            cursor.execute("""
                UPDATE processing_queue
                SET status = 'running', started_at = ?
                WHERE job_id = ?
            """, (datetime.utcnow().isoformat(), job['job_id']))
            
            conn.commit()
            conn.close()
            
            return job
            
        except Exception as e:
            logger.error(f"Error fetching job: {e}")
            return None
    
    def process_job(self, job: Dict[str, Any]):
        """Route job to appropriate handler based on job_type"""
        job_id = job['job_id']
        job_type = job['job_type']
        
        logger.info(f"Processing job {job_id} (type={job_type}, priority={job.get('priority', 0)})")
        
        try:
            # Parse params if JSON string
            params = job.get('params', '{}')
            if isinstance(params, str):
                params = json.loads(params) if params else {}
            
            # Route to handler
            if job_type == 'L0_harvest':
                self.run_l0_harvest(job_id, params)
            elif job_type == 'L1_cluster':
                self.run_l1_clustering(job_id, params)
            elif job_type == 'L2_extract':
                self.run_l2_extraction(job_id, params)
            elif job_type == 'L3_synthesize':
                self.run_l3_synthesis(job_id, params)
            elif job_type == 'L4_expand':
                self.run_l4_expansion(job_id, params)
            else:
                logger.warning(f"Unknown job type: {job_type}")
                self.mark_job_failed(job_id, f"Unknown job type: {job_type}")
                return
            
            # Mark success
            self.mark_job_complete(job_id)
            
        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}", exc_info=True)
            self.mark_job_failed(job_id, str(e))
    
    def run_l0_harvest(self, job_id: str, params: Dict[str, Any]):
        """
        L0: Semantic Scholar metadata harvest
        Input: query terms
        Output: candidate articles with metadata
        """
        logger.info(f"L0 harvest: {params.get('query', 'no query')}")
        
        query = params.get('query', '')
        if not query:
            raise ValueError("L0 requires 'query' parameter")
        
        # TODO: Call Semantic Scholar API
        # For now, stub implementation
        logger.info(f"L0: Would query Semantic Scholar for: {query}")
        
        # Placeholder: pretend we found 10 papers
        results = {
            'job_id': job_id,
            'query': query,
            'papers_found': 10,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Store results
        self._store_job_results(job_id, 'L0_harvest', results)
    
    def run_l1_clustering(self, job_id: str, params: Dict[str, Any]):
        """
        L1: Abstract-based clustering and triage
        Input: list of article IDs
        Output: keep/drop decisions with rationale
        """
        logger.info(f"L1 clustering: {len(params.get('article_ids', []))} articles")
        
        article_ids = params.get('article_ids', [])
        if not article_ids:
            raise ValueError("L1 requires 'article_ids' parameter")
        
        # TODO: Load abstracts, compute embeddings, cluster, score relevance
        # Call scripts/triage_score.py
        logger.info(f"L1: Would cluster {len(article_ids)} abstracts")
        
        # Placeholder: keep 70% of articles
        kept_count = int(len(article_ids) * 0.7)
        results = {
            'job_id': job_id,
            'total_articles': len(article_ids),
            'kept': kept_count,
            'dropped': len(article_ids) - kept_count,
            'recall_estimate': 0.95,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self._store_job_results(job_id, 'L1_cluster', results)
    
    def run_l2_extraction(self, job_id: str, params: Dict[str, Any]):
        """
        L2: 7-panel extraction from full text
        Input: article ID
        Output: structured 7-panel JSON
        """
        logger.info(f"L2 extraction: article {params.get('article_id', 'unknown')}")
        
        article_id = params.get('article_id')
        if not article_id:
            raise ValueError("L2 requires 'article_id' parameter")
        
        # TODO: Load PDF, extract text, run 7-panel prompt
        # Use prompts/7panel_*.md
        logger.info(f"L2: Would extract 7-panel from article {article_id}")
        
        # Placeholder
        results = {
            'job_id': job_id,
            'article_id': article_id,
            'findings_extracted': 3,
            'mechanisms_identified': 2,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self._store_job_results(job_id, 'L2_extract', results)
    
    def run_l3_synthesis(self, job_id: str, params: Dict[str, Any]):
        """
        L3: Multi-document rule synthesis
        Input: cluster of findings
        Output: synthesized rule with confidence
        """
        logger.info(f"L3 synthesis: cluster {params.get('cluster_id', 'unknown')}")
        
        cluster_id = params.get('cluster_id')
        if not cluster_id:
            raise ValueError("L3 requires 'cluster_id' parameter")
        
        # TODO: Load findings from cluster, run synthesis prompt
        # Use prompts/rule_synthesis_multi_doc.md
        logger.info(f"L3: Would synthesize rule from cluster {cluster_id}")
        
        # Placeholder
        results = {
            'job_id': job_id,
            'cluster_id': cluster_id,
            'rule_generated': True,
            'confidence': 0.82,
            'triangulation_score': 0.75,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self._store_job_results(job_id, 'L3_synthesize', results)
    
    def run_l4_expansion(self, job_id: str, params: Dict[str, Any]):
        """
        L4: Related article expansion
        Input: existing articles
        Output: new candidate articles
        """
        logger.info(f"L4 expansion: from {len(params.get('seed_articles', []))} seeds")
        
        seed_articles = params.get('seed_articles', [])
        if not seed_articles:
            raise ValueError("L4 requires 'seed_articles' parameter")
        
        # TODO: Find related papers via citations, semantic search
        logger.info(f"L4: Would expand from {len(seed_articles)} seed articles")
        
        # Placeholder
        results = {
            'job_id': job_id,
            'new_candidates': 5,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self._store_job_results(job_id, 'L4_expand', results)
    
    def _store_job_results(self, job_id: str, job_type: str, results: Dict[str, Any]):
        """Store job results in database for retrieval"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Store as JSON in job_results table (would need to create this table)
            # For now, just log
            logger.info(f"Job {job_id} results: {json.dumps(results, indent=2)}")
            
            conn.close()
        except Exception as e:
            logger.error(f"Failed to store results for {job_id}: {e}")
    
    def mark_job_complete(self, job_id: str):
        """Update job status to complete"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE processing_queue
                SET status = 'complete',
                    completed_at = ?
                WHERE job_id = ?
            """, (datetime.utcnow().isoformat(), job_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✓ Job {job_id} marked complete")
            
        except Exception as e:
            logger.error(f"Failed to mark job {job_id} complete: {e}")
    
    def mark_job_failed(self, job_id: str, error: str):
        """Update job status to failed with error message"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE processing_queue
                SET status = 'failed',
                    error = ?,
                    completed_at = ?
                WHERE job_id = ?
            """, (error, datetime.utcnow().isoformat(), job_id))
            
            conn.commit()
            conn.close()
            
            logger.error(f"✗ Job {job_id} marked failed: {error}")
            
        except Exception as e:
            logger.error(f"Failed to mark job {job_id} as failed: {e}")


def main():
    """Entry point for worker"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Article Eater Queue Worker')
    parser.add_argument('--db', default='./ae.db', help='Database path')
    parser.add_argument('--poll-interval', type=int, default=5, help='Seconds between polls')
    
    args = parser.parse_args()
    
    worker = SimpleWorker(
        poll_interval=args.poll_interval,
        db_path=args.db
    )
    
    try:
        worker.start()
    except KeyboardInterrupt:
        logger.info("Worker stopped by user")
        sys.exit(0)


if __name__ == '__main__':
    main()
