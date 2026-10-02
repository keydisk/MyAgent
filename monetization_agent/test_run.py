"""네트워크 없이 실행: python3 -m unittest monetization_agent.test_run"""

import json
import subprocess
import tempfile
import unittest
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from . import run
from .schedule import schedule_config


class MonetizationTests(unittest.TestCase):
    def report(self, status='business_day'):
        return dict(status=status, calendar_reason='영업일 확인',
                    calendar_source='https://www.kasi.re.kr/calendar',
                    summary='유료 템플릿 실험', next_action='전환율 측정',
                    sections=[dict(heading='후보 비교', body='<script> 실행 금지 & 한글')],
                    sources=[dict(title=str(i), url=f'https://example.org/{i}') for i in range(3)])

    def test_unverified_and_unsafe_sources_fail(self):
        with self.assertRaises(ValueError):
            run.validate_report(self.report('unverified'))
        report = self.report()
        report['sources'][0]['url'] = 'javascript:alert(1)'
        with self.assertRaises(ValueError):
            run.validate_report(report)

    def test_holiday_and_once_per_day(self):
        @contextmanager
        def snapshot(project):
            yield project
        with tempfile.TemporaryDirectory() as temp, patch.object(run, 'datetime') as clock, \
                patch.object(run, 'project_worktree', snapshot), \
                patch.object(run, 'research', return_value=self.report('holiday')) as research, \
                patch.object(run, 'render_pdf') as render, patch.object(run, 'notify') as notify:
            clock.now.return_value = datetime(2026, 10, 5, 11, tzinfo=run.SEOUL)
            self.assertIsNone(run.run_monetization(output=temp))
            self.assertIsNone(run.run_monetization(output=temp))
            self.assertEqual(research.call_count, 1)
            render.assert_not_called()
            notify.assert_not_called()

    def test_weekend_does_not_call_model(self):
        with patch.object(run, 'datetime') as clock, patch.object(run, 'research') as research:
            clock.now.return_value = datetime(2026, 10, 3, 11, tzinfo=run.SEOUL)
            run.run_monetization()
            research.assert_not_called()

    def test_pdf_retry_reuses_successful_research(self):
        def render(report, day, output):
            pdf = output / f'PaceSnap-{day.isoformat()}.pdf'
            pdf.write_bytes(b'%PDF-test')
            return pdf
        with tempfile.TemporaryDirectory() as temp, patch.object(run, 'datetime') as clock, \
                patch.object(run, 'research') as research, patch.object(run, 'render_pdf', render):
            clock.now.return_value = datetime(2026, 10, 2, 11, tzinfo=run.SEOUL)
            folder = Path(temp)
            (folder / 'PaceSnap-2026-10-02.json').write_text(json.dumps(self.report()), encoding='utf-8')
            self.assertTrue(run.run_monetization(no_gui=True, output=folder).is_file())
            research.assert_not_called()

    def test_cli_uses_selected_model_medium_and_live_search(self):
        def execute(command, **kwargs):
            result = Path(command[command.index('--output-last-message') + 1])
            result.write_text(json.dumps(self.report()), encoding='utf-8')
            self.assertIn('--search', command)
            self.assertEqual(command[command.index('--model') + 1], 'gpt-6-luna')
            self.assertIn('model_reasoning_effort="medium"', command)
            self.assertIn('read-only', command)
        with tempfile.TemporaryDirectory() as temp, patch.object(run.shutil, 'which', return_value='/bin/codex'), \
                patch.object(run.subprocess, 'run', side_effect=execute):
            folder = Path(temp)
            (folder / 'README.md').write_text('사진과 운동 기록', encoding='utf-8')
            report = run.research(datetime(2026, 10, 2).date(), folder, folder)
            self.assertEqual(report['summary'], '유료 템플릿 실험')

    def test_failed_pdf_preserves_escaped_html_without_pdf(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(run.subprocess, 'run',
                side_effect=subprocess.CalledProcessError(1, 'pdf')):
            folder = Path(temp)
            with self.assertRaises(subprocess.CalledProcessError):
                run.render_pdf(self.report(), datetime(2026, 10, 2).date(), folder)
            content = next(folder.glob('*.html')).read_text(encoding='utf-8')
            self.assertIn('&lt;script&gt;', content)
            self.assertEqual(list(folder.glob('*.pdf')), [])

    def test_schedule_calls_main_on_weekdays_at_eleven(self):
        config = schedule_config()
        self.assertEqual(config['ProgramArguments'][-1], 'monetization')
        self.assertTrue(config['ProgramArguments'][-2].endswith('/main.py'))
        self.assertEqual(config['StartCalendarInterval'],
                         [{'Weekday': day, 'Hour': 11, 'Minute': 0} for day in range(1, 6)])


if __name__ == '__main__':
    unittest.main()
