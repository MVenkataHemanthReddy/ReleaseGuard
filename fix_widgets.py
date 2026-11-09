import re

# Read the file
with open(r'C:\Users\mitta\OneDrive\Documents\Default Project\apps\dashboard\views.py', 'r') as f:
    content = f.read()

# Find and replace the widget methods
old_widgets = '''    def _get_default_overview_widgets(self):
        return [
            {'widget_type': 'health_summary', 'size': {'w': 12, 'h': 4}, 'config': {}},
            {'widget_type': 'recent_releases', 'size': {'w': 12, 'h': 6}, 'config': {'limit': 10}},
            {'widget_type': 'key_metrics', 'size': {'w': 6, 'h': 4}, 'config': {}},
            {'widget_type': 'trend_chart', 'size': {'w': 6, 'h': 4}, 'config': {'metric': 'pass_rate', 'days': 30}},
        ]

    def _get_default_release_detail_widgets(self):
        return [
            {'widget_type': 'release_header', 'size': {'w': 12, 'h': 3}, 'config': {}},
            {'widget_type': 'test_summary', 'size': {'w': 6, 'h': 4}, 'config': {}},
            {'widget_type': 'comparison_chart', 'size': {'w': 6, 'h': 4}, 'config': {}},
            {'widget_type': 'policy_explanation', 'size': {'w': 12, 'h': 4}, 'config': {}},
            {'widget_type': 'failure_breakdown', 'size': {'w': 12, 'h': 6}, 'config': {}},
        ]

    def _get_default_api_health_widgets(self):
        return [
            {'widget_type': 'api_check_list', 'size': {'w': 12, 'h': 6}, 'config': {}},
            {'widget_type': 'latency_chart', 'size': {'w': 6, 'h': 4}, 'config': {'days': 7}},
            {'widget_type': 'uptime_chart', 'size': {'w': 6, 'h': 4}, 'config': {'days': 30}},
            {'widget_type': 'status_timeline', 'size': {'w': 12, 'h': 4}, 'config': {'hours': 24}},
        ]

    def _get_default_test_intelligence_widgets(self):
        return [
            {'widget_type': 'test_trends', 'size': {'w': 12, 'h': 5}, 'config': {'days': 30}},
            {'widget_type': 'flaky_tests', 'size': {'w': 6, 'h': 5}, 'config': {'limit': 20}},
            {'widget_type': 'duration_trends', 'size': {'w': 6, 'h': 5}, 'config': {}},
            {'widget_type': 'new_failures', 'size': {'w': 12, 'h': 4}, 'config': {'limit': 10}},
        ]

    def _get_default_issues_widgets(self):
        return [
            {'widget_type': 'issue_list', 'size': {'w': 12, 'h': 6}, 'config': {'limit': 20}},
            {'widget_type': 'issue_trend', 'size': {'w': 12, 'h': 4}, 'config': {'days': 30}},
            {'widget_type': 'top_errors', 'size': {'w': 6, 'h': 4}, 'config': {'limit': 10}},
            {'widget_type': 'regression_alerts', 'size': {'w': 6, 'h': 4}, 'config': {'limit': 10}},
        ]'''

new_widgets = '''# ==================== Default Widget Configurations ====================

    WIDGET_CONFIGS = {
        'overview': [
            {'widget_type': 'health_summary', 'size': {'w': 12, 'h': 4}, 'config': {}},
            {'widget_type': 'recent_releases', 'size': {'w': 12, 'h': 6}, 'config': {'limit': 10}},
            {'widget_type': 'key_metrics', 'size': {'w': 6, 'h': 4}, 'config': {}},
            {'widget_type': 'trend_chart', 'size': {'w': 6, 'h': 4}, 'config': {'metric': 'pass_rate', 'days': 30}},
        ],
        'release_detail': [
            {'widget_type': 'release_header', 'size': {'w': 12, 'h': 3}, 'config': {}},
            {'widget_type': 'test_summary', 'size': {'w': 6, 'h': 4}, 'config': {}},
            {'widget_type': 'comparison_chart', 'size': {'w': 6, 'h': 4}, 'config': {}},
            {'widget_type': 'policy_explanation', 'size': {'w': 12, 'h': 4}, 'config': {}},
            {'widget_type': 'failure_breakdown', 'size': {'w': 12, 'h': 6}, 'config': {}},
        ],
        'api_health': [
            {'widget_type': 'api_check_list', 'size': {'w': 12, 'h': 6}, 'config': {}},
            {'widget_type': 'latency_chart', 'size': {'w': 6, 'h': 4}, 'config': {'days': 7}},
            {'widget_type': 'uptime_chart', 'size': {'w': 6, 'h': 4}, 'config': {'days': 30}},
            {'widget_type': 'status_timeline', 'size': {'w': 12, 'h': 4}, 'config': {'hours': 24}},
        ],
        'test_intelligence': [
            {'widget_type': 'test_trends', 'size': {'w': 12, 'h': 5}, 'config': {'days': 30}},
            {'widget_type': 'flaky_tests', 'size': {'w': 6, 'h': 5}, 'config': {'limit': 20}},
            {'widget_type': 'duration_trends', 'size': {'w': 6, 'h': 5}, 'config': {}},
            {'widget_type': 'new_failures', 'size': {'w': 12, 'h': 4}, 'config': {'limit': 10}},
        ],
        'issues': [
            {'widget_type': 'issue_list', 'size': {'w': 12, 'h': 6}, 'config': {'limit': 20}},
            {'widget_type': 'issue_trend', 'size': {'w': 12, 'h': 4}, 'config': {'days': 30}},
            {'widget_type': 'top_errors', 'size': {'w': 6, 'h': 4}, 'config': {'limit': 10}},
            {'widget_type': 'regression_alerts', 'size': {'w': 6, 'h': 4}, 'config': {'limit': 10}},
        ],
    }

    def _get_widgets(self, view_type):
        """Get default widget configuration for a dashboard view type."""
        return self.WIDGET_CONFIGS.get(view_type, [])

    def _get_default_overview_widgets(self):
        return self._get_widgets('overview')

    def _get_default_release_detail_widgets(self):
        return self._get_widgets('release_detail')

    def _get_default_api_health_widgets(self):
        return self._get_widgets('api_health')

    def _get_default_test_intelligence_widgets(self):
        return self._get_widgets('test_intelligence')

    def _get_default_issues_widgets(self):
        return self._get_widgets('issues')'''

content = content.replace(old_widgets, new_widgets)

with open(r'C:\Users\mitta\OneDrive\Documents\Default Project\apps\dashboard\views.py', 'w') as f:
    f.write(content)

print("Widget methods updated successfully!")