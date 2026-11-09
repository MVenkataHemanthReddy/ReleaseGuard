"""
Background worker management command for ReleaseGuard.

Usage:
    python manage.py runworker                    # Run with default settings
    python manage.py runworker --interval 5       # Poll every 5 seconds
    python manage.py runworker --jobs parse_junit_xml,generate_release_analysis  # Only specific jobs
    python manage.py runworker --once             # Run one iteration and exit (for testing)
    python manage.py runworker --recover-stale    # Recover stale jobs and exit
"""

import logging
import signal
import sys
import time
import uuid
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Run background worker to process queued jobs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=5,
            help='Polling interval in seconds (default: 5)',
        )
        parser.add_argument(
            '--jobs',
            type=str,
            default='',
            help='Comma-separated list of job names to process (default: all)',
        )
        parser.add_argument(
            '--once',
            action='store_true',
            help='Run one iteration and exit (for testing)',
        )
        parser.add_argument(
            '--recover-stale',
            action='store_true',
            help='Recover stale jobs and exit',
        )
        parser.add_argument(
            '--stale-threshold',
            type=int,
            default=10,
            help='Minutes before a job is considered stale (default: 10)',
        )
        parser.add_argument(
            '--max-jobs-per-cycle',
            type=int,
            default=10,
            help='Maximum jobs to process per polling cycle (default: 10)',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.worker_id = f'worker-{uuid.uuid4().hex[:8]}'
        self.running = True
        self.jobs_processed = 0
        self.jobs_failed = 0

        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        self.stdout.write(self.style.WARNING(f'\nReceived signal {signum}, shutting down gracefully...'))
        self.running = False

    def handle(self, *args, **options):
        self.interval = options['interval']
        self.job_names = [j.strip() for j in options['jobs'].split(',') if j.strip()] if options['jobs'] else None
        self.once = options['once']
        self.recover_stale = options['recover_stale']
        self.stale_threshold = options['stale_threshold']
        self.max_jobs_per_cycle = options['max_jobs_per_cycle']

        self.stdout.write(self.style.SUCCESS(f'Starting ReleaseGuard worker: {self.worker_id}'))
        self.stdout.write(f'Poll interval: {self.interval}s')
        self.stdout.write(f'Job filter: {self.job_names or "all"}')
        self.stdout.write(f'Max jobs/cycle: {self.max_jobs_per_cycle}')

        if self.recover_stale:
            self._recover_stale_jobs()
            return

        if self.once:
            self._run_one_cycle()
            self._print_summary()
            return

        self._run_loop()

    def _run_loop(self):
        """Main worker loop."""
        self.stdout.write(self.style.SUCCESS('Worker loop started. Press Ctrl+C to stop.'))

        while self.running:
            try:
                self._run_one_cycle()
            except Exception as e:
                logger.exception('Error in worker loop')
                self.stdout.write(self.style.ERROR(f'Worker error: {e}'))
                # Don't exit on error, just wait and retry
                time.sleep(self.interval)

            if self.running:
                time.sleep(self.interval)

        self._print_summary()
        self.stdout.write(self.style.SUCCESS('Worker stopped gracefully.'))

    def _run_one_cycle(self):
        """Run one polling cycle: claim and process jobs."""
        from apps.core.models import BackgroundJob

        # Recover stale jobs periodically
        if self.jobs_processed % 50 == 0:
            recovered = BackgroundJob.recover_stale_jobs(self.stale_threshold)
            if recovered:
                self.stdout.write(f'Recovered {recovered} stale jobs')

        # Process jobs up to max per cycle
        for _ in range(self.max_jobs_per_cycle):
            if not self.running:
                break

            job = BackgroundJob.claim_next_job(self.worker_id, self.job_names)
            if not job:
                break  # No more jobs available

            self._process_job(job)

    def _process_job(self, job):
        """Process a single job."""
        from apps.core.models import BackgroundJob
        from apps.releases.services import TestRunProcessingService, ReleaseAnalysisService

        self.stdout.write(f'Processing job {job.id}: {job.name}')
        job.mark_running()

        try:
            if job.name == 'generate_release_analysis':
                self._handle_analysis_job(job)
            elif job.name == 'parse_junit_xml':
                self._handle_parse_job(job)
            elif job.name == 'run_api_check':
                self._handle_api_check_job(job)
            else:
                raise ValueError(f'Unknown job type: {job.name}')

            job.mark_completed({'status': 'success'})
            self.jobs_processed += 1
            self.stdout.write(self.style.SUCCESS(f'  Completed: {job.id}'))

        except Exception as e:
            logger.exception('Job %s failed', job.id)
            error_msg = str(e)
            will_retry = job.can_retry()
            job.mark_failed(error_msg, will_retry=will_retry)

            if will_retry:
                self.stdout.write(self.style.WARNING(f'  Failed (will retry): {job.id} - {error_msg}'))
            else:
                self.stdout.write(self.style.ERROR(f'  Failed (dead): {job.id} - {error_msg}'))
                self.jobs_failed += 1

    def _handle_analysis_job(self, job):
        """Handle generate_release_analysis job."""
        release_id = job.payload.get('release_id')
        policy_version = job.payload.get('policy_version', '1.0')

        if not release_id:
            raise ValueError('release_id required in payload')

        from apps.releases.models import Release
        release = Release.objects.get(pk=release_id)

        analysis_service = ReleaseAnalysisService()
        analysis_service.analyze(release, policy_version)

    def _handle_parse_job(self, job):
        """Handle parse_junit_xml job."""
        # This is handled inline during upload, but could be queued for large files
        test_run_id = job.payload.get('test_run_id')
        if not test_run_id:
            raise ValueError('test_run_id required in payload')

        from apps.releases.models import TestRun
        test_run = TestRun.objects.get(pk=test_run_id)

        # Processing already done at upload time
        # This job type reserved for future async parsing of large files
        pass

    def _handle_api_check_job(self, job):
        """Handle run_api_check job."""
        # TODO: Implement in Phase 4
        api_check_id = job.payload.get('api_check_id')
        if not api_check_id:
            raise ValueError('api_check_id required in payload')

        # Placeholder for Phase 4
        raise NotImplementedError('API check execution not yet implemented')

    def _recover_stale_jobs(self):
        """Recover stale jobs and exit."""
        from apps.core.models import BackgroundJob

        self.stdout.write(f'Recovering stale jobs (threshold: {self.stale_threshold} minutes)...')
        recovered = BackgroundJob.recover_stale_jobs(self.stale_threshold)
        self.stdout.write(self.style.SUCCESS(f'Recovered {recovered} stale jobs'))

    def _print_summary(self):
        """Print worker summary."""
        self.stdout.write('')
        self.stdout.write(self.style.NOTICE('=== Worker Summary ==='))
        self.stdout.write(f'Worker ID: {self.worker_id}')
        self.stdout.write(f'Jobs processed: {self.jobs_processed}')
        self.stdout.write(f'Jobs failed: {self.jobs_failed}')