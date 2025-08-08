import pandas as pd
from fpdf import FPDF
import glob, os
from pathlib import Path

def generate(invoices_path, pdfs_path, product_id, product_name, amount_purchased,
             price_per_unit, total_price, image_path):
    """
    This function converts invoice Excel files into PDF invoices.
    :param invoices_path:
    :param pdfs_path:
    :param product_id:
    :param product_name:
    :param amount_purchased:
    :param price_per_unit:
    :param total_price:
    :param image_path:
    :return:
    """

    filepaths = glob.glob(f"{invoices_path}/*.xlsx")

    for filepath in filepaths:
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.add_page()

        filename = Path(filepath).stem
        invoice_number, date = filename.split("-")

        pdf.set_font('Times', 'B', 16)
        pdf.cell(w=50, h=8, txt=f"Invoice nr. {invoice_number}",ln=1)

        pdf.set_font('Times', 'B', 16)
        pdf.cell(w=50, h=8, txt=f"Date: {date}", ln=1)

        df = pd.read_excel(filepath,sheet_name="Sheet 1")

        # Add a header
        columns = [item.replace("_"," ").title() for item in df.columns]
        pdf.set_font(family='Times', style="B", size=10)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(w=30, h=8, txt=str(columns[0]), border=1)
        pdf.cell(w=70, h=8, txt=str(columns[1]), border=1)
        pdf.cell(w=30, h=8, txt=str(columns[2]), border=1)
        pdf.cell(w=30, h=8, txt=str(columns[3]), border=1)
        pdf.cell(w=30, h=8, txt=str(columns[4]), ln=1, border=1)

        # Add rows to the table
        for index, row in df.iterrows():
            pdf.set_font(family='Times', size=10)
            pdf.set_text_color(80, 80, 80)
            pdf.cell(w=30, h=8, txt=str(row[product_id]), border=1)
            pdf.cell(w=70, h=8, txt=str(row[product_name]), border=1)
            pdf.cell(w=30, h=8, txt=str(row[amount_purchased]), border=1)
            pdf.cell(w=30, h=8, txt=str(row[price_per_unit]), border=1)
            pdf.cell(w=30, h=8, txt=str(row[total_price]), ln=1, border=1)

        total_sum = df[total_price].sum()
        pdf.set_font(family='Times', size=10)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(w=30, h=8, txt="", border=1)
        pdf.cell(w=70, h=8, txt="", border=1)
        pdf.cell(w=30, h=8, txt="", border=1)
        pdf.cell(w=30, h=8, txt="", border=1)
        pdf.cell(w=30, h=8, txt=str(total_sum), ln=1, border=1)

        # Adding total sum sentence
        pdf.set_font(family='Times', style="B", size=10)
        pdf.cell(w=30, h=8, txt=f"The total price is {total_sum}", ln=1)

        # Add company name and logo
        pdf.set_font(family='Times', style="B", size=14)
        pdf.cell(w=25, h=8, txt="PythonHow")
        pdf.image(image_path, w=8)

        if not os.path.exists(pdfs_path):
            os.makedirs(pdfs_path)
        pdf.output(f"{pdfs_path}/{filename}.pdf")