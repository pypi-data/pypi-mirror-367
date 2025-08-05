"""Example problem definition for remote browser environment."""

from ..problems import problem


@problem("navigate_and_verify", description="Navigate to a URL and verify the page contains text")
class NavigateAndVerifyProblem:
    """Problem that navigates to a URL and verifies page content."""

    def get_setup(self):
        """Get the setup configuration for this problem."""
        return {
            "function": "navigate_to_url",
            "args": {"url": "https://example.com", "wait_for_load_state": "networkidle"},
        }

    def get_evaluation(self):
        """Get the evaluation configuration for this problem."""
        return {
            "function": "page_contains",
            "args": {
                "search_terms": [
                    "Example Domain",
                    "This domain is for use in illustrative examples",
                ],
                "partial_rewarding": True,
            },
        }
