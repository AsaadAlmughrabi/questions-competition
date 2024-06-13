from http.server import BaseHTTPRequestHandler
import requests  # type: ignore
import json
from urllib import parse

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        s = self.path
        url_comp = parse.urlsplit(s)
        query_string_list = parse.parse_qsl(url_comp.query)
        my_dic = dict(query_string_list)

        if 'category' in my_dic:
            self.getCategory(my_dic)
        else:
            self.getAmount(my_dic)

    def getAmount(self, my_dic):
        amount = my_dic.get('amount', '20')
        try:
            amount = int(amount)
            if amount > 50:
                amount = 50
        except ValueError:
            amount = 20

        # Build the URL for the API request
        url = f"https://opentdb.com/api.php?amount={amount}"

        # Make the request to the Open Trivia Database API
        req = requests.get(url)
        if req.status_code != 200:
            self.send_error(req.status_code, f'Failed to fetch questions for amount {amount}')
            return

        rec_question = req.json()

        # Prepare the output
        output = ""
        count = 0
        for item in rec_question.get("results", []):
            count += 1
            question = item["question"]
            correct_answer = item["correct_answer"]
            output += f"Question {count}: {question}\nAnswer: {correct_answer}\n\n"

        # Send HTTP status 200 (OK)
        self.send_response(200)

        # Set the Content-type to 'text/plain'
        self.send_header("Content-type", "text/plain")

        # End headers
        self.end_headers()

        # Write the output to the response
        self.wfile.write(output.encode())

    def getCategory(self, my_dic):
        category = my_dic.get('category', '9')

        try:
            category_id = int(category)
            if category_id < 9 or category_id > 32:
                raise ValueError("Invalid category")
        except ValueError:
            self.send_response(400)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write("Invalid category. Category must be between 9 and 32.".encode())
            return

        # Fetch questions from Open Trivia Database API
        url = f"https://opentdb.com/api.php?amount=10&category={category_id}"
        req = requests.get(url)
        if req.status_code != 200:
            self.send_error(req.status_code, f'Failed to fetch questions for category {category_id}')
            return

        rec_question = req.json()

        # Prepare the output
        output = f"Category: {category_id}\n\n"
        count = 0
        for item in rec_question.get("results", []):
            count += 1
            question = item["question"]
            correct_answer = item["correct_answer"]
            category=item['category']
            output += f"Question {count}: category:{category}\n {question}\nAnswer: {correct_answer}\n\n"

        # Send HTTP status 200 (OK)
        self.send_response(200)

        # Set the Content-type to 'text/plain'
        self.send_header("Content-type", "text/plain")

        # End headers
        self.end_headers()

        # Write the output to the response
        self.wfile.write(output.encode())
