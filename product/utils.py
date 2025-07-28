from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile

def generate_order_receipt_pdf(order):
    items = order.items.all
    html_string = render_to_string("order_receipt.html", {"order": order,"items":items})
    html = HTML(string=html_string)

    result = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    html.write_pdf(result.name)
    return result.name  # return file path
