import unittest
from unittest.mock import patch, MagicMock
from requests.models import Response
import json

# Import your APIRequest class here
from gdmo import APIRequest

class TestAPIRequest(unittest.TestCase):
    def setUp(self):
        self.url = "https://example.com/api"
        self.api = APIRequest(self.url)

    def test_set_header(self):
        self.api.set_header("Authorization", "Bearer token")
        self.assertEqual(self.api._headers["Authorization"], "Bearer token")

    def test_set_headers(self):
        headers = [("X-Test-1", "Value1"), ("X-Test-2", "Value2")]
        self.api.set_headers(headers)
        self.assertEqual(self.api._headers["X-Test-1"], "Value1")
        self.assertEqual(self.api._headers["X-Test-2"], "Value2")

    def test_set_param(self):
        self.api.set_param("query", "test")
        self.assertEqual(self.api._params["query"], "test")

    def test_set_parameters(self):
        params = {"key1": "value1", "key2": "value2"}
        self.api.set_parameters(params)
        self.assertEqual(self.api._params["key1"], "value1")
        self.assertEqual(self.api._params["key2"], "value2")

    def test_set_content_type_valid(self):
        self.api.set_content_type("application/json")
        self.assertEqual(self.api._headers["Content-Type"], "application/json")

    def test_set_content_type_invalid(self):
        with self.assertRaises(ValueError):
            self.api.set_content_type("invalid/type")

    def test_set_method_valid(self):
        self.api.set_method("GET")
        self.assertEqual(self.api._method, "GET")

    def test_set_method_invalid(self):
        with self.assertRaises(ValueError):
            self.api.set_method("DELETE")

    def test_set_data(self):
        data = {"key": "value"}
        self.api.set_data(data)
        self.assertEqual(self.api._data, data)

    def test_set_json_valid(self):
        json_data = json.dumps({"key": "value"})
        self.api.set_json(json_data)
        self.assertEqual(self.api._json, json_data)

    def test_set_json_invalid(self):
        with self.assertRaises(ValueError):
            self.api.set_json("invalid json")

    @patch("requests.post")
    def test_make_request_success(self, mock_post):
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_post.return_value = mock_response

        self.api.set_method("POST").set_json(json.dumps({"key": "value"})).get_response()
        self.assertEqual(self.api._response.status_code, 200)
        self.assertEqual(self.api.get_json_response(), {"success": True})

    @patch("requests.post")
    def test_make_request_failure_with_retries(self, mock_post):
        mock_response = MagicMock(spec=Response)
        mock_response.raise_for_status.side_effect = Exception("HTTP Error")
        mock_post.return_value = mock_response
        self.api.set_method("POST").set_json(json.dumps({"key": "value"})).set_max_retries(2).get_response()
        self.assertIsNotNone(self.api._response)

    def test_get_raw_response_none(self):
        self.assertIsNone(self.api.get_raw_response())

if __name__ == "__main__":
    unittest.main()
