"""Form interaction problem for testing input elements."""

from ..problems import problem


@problem("form_fill_and_submit", description="Fill out a form and verify submission")
class FormFillAndSubmitProblem:
    """Problem that fills out a form and verifies the interaction."""

    def get_setup(self):
        """Set up a form page."""
        return {
            "function": "navigate_to_url",
            "args": {
                "url": "https://httpbin.org/forms/post",
                "wait_for_load_state": "domcontentloaded",
            },
        }

    def get_evaluation(self):
        """Verify form elements are present."""
        return {
            "function": "page_contains",
            "args": {
                "search_terms": ["Customer name:", "Pizza Size", "Submit order"],
                "partial_rewarding": False,
            },
        }
