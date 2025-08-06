#    Copyright © 2021 Andrei Puchko
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.


import json
from copy import deepcopy
import re
import os
import html
import base64
import datetime
from q2report.q2utils import num


from q2report.q2printer.q2printer import Q2Printer, get_printer
from q2report.q2utils import num, Q2Heap, int_, today, float_

re_calc = re.compile(r"\{.*?\}")
re_q2image = re.compile(r"\{q2image\s*\(\s*.*?\s*\)\}")
re_dec = re.compile(r"[^\d]")

engine_name = None

# TODO: before_print, after_print


def q2image(image, width=0, height=0):
    def load_image_data(image):
        if isinstance(image, str) and os.path.isfile(image):
            with open(image, "rb") as f:
                raw = f.read()
            return raw, base64.b64encode(raw).decode()
        else:
            b64 = image
            raw = base64.b64decode(b64)
            return raw, b64

    def get_png_size(data):
        if data[:8] != b"\x89PNG\r\n\x1a\n":
            raise ValueError("Not a PNG image")
        return int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")

    def get_jpg_size(data):
        i = 2  # Skip initial 0xFFD8
        while i < len(data):
            if data[i] != 0xFF:
                raise ValueError("Invalid JPEG marker")
            while data[i] == 0xFF:
                i += 1
            marker = data[i]
            i += 1
            if marker in (0xC0, 0xC2):  # SOF0 / SOF2
                i += 3  # skip length and precision
                height = int.from_bytes(data[i : i + 2], "big")
                width = int.from_bytes(data[i + 2 : i + 4], "big")
                return width, height
            else:
                length = int.from_bytes(data[i : i + 2], "big")
                i += length
        raise ValueError("JPEG size not found")

    raw, image_b64 = load_image_data(image)

    if raw[:8] == b"\x89PNG\r\n\x1a\n":
        fmt = "PNG"
        w, h = get_png_size(raw)
    elif raw[:2] == b"\xff\xd8":
        fmt = "JPEG"
        w, h = get_jpg_size(raw)
    else:
        raise ValueError("Unsupported image format")

    return f"{image_b64}:{width}:{height}:{w}:{h}:{fmt}"


image = q2image


def set_engine(engine2="PyQt6"):
    """_summary_

    Args:
        engine2 (str, optional): _description_. Defaults to "PyQt6".
    """
    global engine
    engine = engine2


roles = ["free", "table", "table_header", "table_footer", "group_header", "group_footer", "header", "footer"]


class Q2Report_rows:
    def __init__(
        self,
        rows=None,
        heights=[0],
        style={},
        role="free",
        data_source=[],
        groupby="",
        table_groups=[],
        print_when=None,
        print_after=None,
        new_page_before=False,
        new_page_after=False,
        table_header=None,
        table_footer=None,
    ):
        if isinstance(rows, Q2Report_rows):
            self.rows = rows.rows
        elif rows is not None:
            self.rows = self._get_rows(rows)
        else:
            self.rows = deepcopy(Q2Report.default_rows)
            self.rows["heights"] = heights
            self.rows["style"] = Q2Report.check_style(style)
            self.rows["role"] = role
            self.rows["data_source"] = data_source
            self.rows["groupby"] = groupby
            self.rows["table_groups"] = table_groups
            self.rows["print_when"] = print_when
            self.rows["print_after"] = print_after
            self.rows["new_page_before"] = new_page_before
            self.rows["new_page_after"] = new_page_after
            if table_header is not None:
                self.rows["table_header"] = self.set_table_header(table_header)
            if table_footer is not None:
                self.rows["table_footer"] = self.set_table_footer(table_footer)

        if self.rows["role"] not in roles:
            raise Exception(f'Bad role {self.rows["role"]}')

    def _get_rows(self, rows):
        if isinstance(rows, Q2Report_rows):
            _rows = rows.rows
        elif isinstance(rows, dict):
            _rows = rows
        else:
            _rows = None
        return _rows

    def set_cell(self, row, col, data, style=None, rowspan=None, colspan=None, format=None, name=None):
        if row == -1:
            row = len(self.rows.get("heights", [])) - 1
            row = 0 if row < 0 else row
        self.extend_rows(row)
        cell = deepcopy(Q2Report.default_cell)
        cell["data"] = data
        cell["style"] = self.check_style(style)
        rowspan = int_(rowspan)
        colspan = int_(colspan)
        if rowspan != 0 or colspan != 0:
            cell["rowspan"] = 1 if rowspan == 0 else rowspan
            cell["colspan"] = 1 if colspan == 0 else colspan
        if format is not None:
            cell["format"] = format
        if isinstance(name, str):
            cell["name"] = name
        self.rows["cells"][f"{row},{col}"] = cell

    def set_row_height(self, row=0, height=0):
        self.extend_rows(row)
        self.rows["heights"][row] = height

    def set_table_header(self, rows):
        rows.rows["role"] = "table_header"
        self.rows["table_header"] = self._get_rows(rows)

    def set_table_footer(self, rows):
        # rows.rows["role"] = "table_footer"
        self.rows["table_footer"] = self._get_rows(rows)

    def add_table_group(self, groupby, header, footer):
        header = self._get_rows(header)
        header["groupby"] = groupby
        footer = self._get_rows(footer)
        footer["groupby"] = groupby
        self.rows["table_groups"].append({"group_header": header, "group_footer": footer})

    def check_style(self, style):
        if isinstance(style, dict):
            # return {x: style[x] for x in style if x in Q2Report.default_style}
            return {x: style[x] for x in style }
        elif isinstance(style, str):
            if style.endswith("}") and style.startswith("{"):
                style = style[1:-1]
            return {x.split(":")[0]: x.split(":")[1].strip() for x in style.split(";") if ":" in x}
        else:
            return {}

    def extend_rows(self, row):
        while row + 1 > len(self.rows["heights"]):
            self.rows["heights"].append("0")


class mydata(dict):
    def __init__(self, q2report):
        super().__init__()
        self.rep = self.q2report = q2report

    def __getitem__(self, key):
        if key in self.__dict__:
            return self.__dict__[key]

        if self.q2report.use_prevrowdata:
            data = self.q2report.prevrowdata
        else:
            data = self.q2report.data

        if key in data:
            return data[key]
        elif key in globals():
            return globals()[key]
        elif key in __builtins__:
            return __builtins__[key]
        else:
            return ""


class Q2Report:
    default_style = {
        "font-family": "Arial",
        "font-size": "10pt",
        "font-weight": "normal",  # bold
        "text-decoration": "",  # underline
        "font-style": "",  # italic
        "color": "black",  # font color
        "background": "white",  # background color
        "border-color": "black",  # border color
        "border-width": "1 1 1 1",
        "padding": "0.05cm 0.05cm 0.05cm 0.05cm",
        "text-align": "left",
        "vertical-align": "top",
    }

    default_page = {
        "tag": "",
        "page_width": 21,
        "page_height": 29.7,
        "page_margin_left": 2,
        "page_margin_right": 1,
        "page_margin_top": 1,
        "page_margin_bottom": 1,
        "columns": [],
    }

    default_columns = {"widths": [], "rows": [], "style": {}}

    default_rows = {
        "heights": [],
        "style": {},
        "role": "free",
        "data_source": "",
        "groupby": "",
        "table_groups": [],
        "print_when": "",
        "print_after": "",
        "new_page_before": "",
        "new_page_after": "",
        "cells": {},
    }

    default_cell = {
        "data": "",
        "style": {},
        "rowspan": 0,
        "colspan": 0,
    }

    def __init__(self, style={}):
        self.report_content = {}
        if style:
            self.set_style(style)
        self.printer = None
        self.params = {}
        self.prevrowdata = {}
        self.use_prevrowdata = False
        self.mydata = mydata(self)
        self.table_aggregators = {}
        self.table_group_aggregators = []
        self.outline_level = 0
        self.currency = "€"

        self.data = {}  # current data
        self.data_sets = {}
        self.current_data_set_name = ""
        self.current_data_set_row_number = 0
        self.heap = Q2Heap()
        self.d = D(self)

    def set_data(self, data, name=None):
        if hasattr(data, "__name__") and name is None:
            self.data[data.__name__] = data
        elif isinstance(name, str):
            self.data[name] = data

    @staticmethod
    def check_style(style):
        if isinstance(style, dict):
            return {x: style[x] for x in style if x in Q2Report.default_style}
        else:
            return {}

    @staticmethod
    def make_style(
        font_family=None,
        font_size=None,
        font_weight=None,
        border_width=None,
        padding=None,
        text_align=None,
        vertical_align=None,
        alignment=None,
    ):
        """_summary_

        Args:
            font_family (str, optional): e.g. "Arial". Defaults to None.
            font_size (str, int, float, optional): font size in pt, e.g. 12, 12.5, "12.5" . Defaults to None.
            font_weight str, optional): "bold" or "". Defaults to None.
            border_width (_type_, optional): _description_. Defaults to None.
            padding (_type_, optional): _description_. Defaults to None.
            text_align (_type_, optional): _description_. Defaults to None.
            vertical_align (_type_, optional): _description_. Defaults to None.

        Returns:
            dict: _description_
        """
        style = {}
        if font_family:
            style["font-family"] = font_family
        if font_size:
            style["font-size"] = f"{font_size}"
        if font_weight:
            style["font-weight"] = font_weight
        if border_width:
            style["border-width"] = border_width
        if padding:
            style["padding"] = padding
        if text_align:
            style["text-align"] = text_align
        if vertical_align:
            style["vertical-align"] = vertical_align
        if alignment is not None:
            alignment = num(alignment)
            if alignment in (7, 4, 1, 0, -1):
                style["text-align"] = "left"
            elif alignment in (9, 6, 3):
                style["text-align"] = "right"
            else:
                style["text-align"] = "center"

            if alignment in (7, 8, 9, 0, -1):
                style["vertical-align"] = "top"
            elif alignment in (1, 2, 3):
                style["vertical-align"] = "bottom"
            else:
                style["vertical-align"] = "middle"

        return style

    def set_style(self, style=None):
        if style is None or not isinstance(style, dict):
            return
        if "style" not in self.report_content:
            self.report_content["style"] = deepcopy(self.default_style)
        self.report_content["style"].update(self.check_style(style))

    def add_page(
        self,
        page_width=None,
        page_height=None,
        page_margin_left=None,
        page_margin_right=None,
        page_margin_top=None,
        page_margin_bottom=None,
        style={},
    ):
        if "pages" not in self.report_content:
            self.report_content["pages"] = []

        page = deepcopy(self.default_page)
        if page_width:
            page["page_width"] = page_width
        if page_height:
            page["page_height"] = page_height
        if page_margin_left:
            page["page_margin_left"] = page_margin_left
        if page_margin_right:
            page["page_margin_right"] = page_margin_right
        if page_margin_top:
            page["page_margin_top"] = page_margin_top
        if page_margin_bottom:
            page["page_margin_bottom"] = page_margin_bottom
        if style != {}:
            page["style"] = deepcopy(style)
        self.report_content["pages"].append(page)

    def check_page_index(self, page_index):
        if page_index is None:
            page_index = len(self.report_content.get("pages", [])) - 1
        if page_index < 0:
            # self.report_content["pages"] = []
            page_index = 0
        while page_index > len(self.report_content.get("pages", [])) - 1:
            self.add_page()
        return page_index

    def add_columns(self, page_index=None, widths=[], style={}):
        page_index = self.check_page_index(page_index)
        columns = deepcopy(self.default_columns)

        if widths != []:
            columns["widths"] = [f"{x}" for x in widths]
        if style != {}:
            columns["style"] = deepcopy(style)

        self.report_content["pages"][page_index]["columns"].append(columns)

    def check_columns_index(self, page_index, columns_index):
        if columns_index is None:
            columns_index = len(self.report_content["pages"][page_index]["columns"]) - 1
        if columns_index < 0:
            columns_index = 0
        page_index = self.check_page_index(page_index)
        while columns_index > len(self.report_content["pages"][page_index]["columns"]) - 1:
            self.add_columns(page_index)
        return columns_index

    def check_rows_index(self, page_index, columns_index, rows_index):
        if rows_index is None:
            rows_index = len(self.report_content["pages"][page_index]["columns"][columns_index]["rows"]) - 1
        if rows_index < 0:
            rows_index = 0
        while (
            rows_index > len(self.report_content["pages"][page_index]["columns"][columns_index]["rows"]) - 1
        ):
            self.add_rows(page_index, columns_index)
        return rows_index

    def add_column(self, page_index=None, columns_index=None, width=0):
        page_index = self.check_page_index(page_index)
        columns_index = self.check_columns_index(page_index, columns_index)
        self.report_content["pages"][page_index]["columns"][columns_index]["widths"].append(f"{width}")

    def add_rows(self, page_index=None, columns_index=None, heights=None, style=None, rows=None):
        page_index = self.check_page_index(page_index)
        columns_index = self.check_columns_index(page_index, columns_index)
        if isinstance(rows, Q2Report_rows):
            rows = rows.rows
        else:
            rows = deepcopy(self.default_rows)
            if heights and isinstance(heights, list):
                rows["heights"] = list(heights)
            rows["style"].update(self.check_style(style))
        self.report_content["pages"][page_index]["columns"][columns_index]["rows"].append(rows)
        return Q2Report_rows(rows)

    def add_row(self, page_index=None, columns_index=None, rows_index=None, height=0):
        page_index = self.check_page_index(page_index)
        columns_index = self.check_columns_index(page_index, columns_index)
        rows_index = self.check_rows_index(page_index, columns_index, rows_index)

        if height is not None:
            self.report_content["pages"][page_index]["columns"][columns_index]["rows"][rows_index][
                "heights"
            ].append(f"{height}")

    def get_rows(self, page_index=None, columns_index=None, rows_index=None):
        page_index = self.check_page_index(page_index)
        columns_index = self.check_columns_index(page_index, columns_index)
        rows_index = self.check_rows_index(page_index, columns_index, rows_index)
        return Q2Report_rows(
            self.report_content["pages"][page_index]["columns"][columns_index]["rows"][rows_index]
        )

    def set_col_width(self, page_index=None, columns_index=None, column=0, width=0):
        page_index = self.check_page_index(page_index)
        columns_index = self.check_columns_index(page_index, columns_index)
        columns = self.report_content["pages"][page_index]["columns"][columns_index]
        while column > len(columns["widths"]) - 1:
            self.add_column(page_index, columns_index)
        self.report_content["pages"][page_index]["columns"][columns_index]["widths"][column] = width
        1 + 1

    def set_cell(
        self,
        row,
        col,
        data,
        page_index=None,
        columns_index=None,
        rows_index=None,
        style=None,
        rowspan=None,
        colspan=None,
        format=None,
        name=None,
    ):
        rows = self.get_rows(page_index, columns_index, rows_index)
        rows.set_cell(row, col, data, style, rowspan, colspan, format, name)
        return rows

    def load(self, content):
        if os.path.isfile(content):
            self.report_content = json.load(open(content))
        else:
            if content != "":
                self.report_content = json.loads(content)
        self.params = self.report_content.get("params", {})

    def data_start(self):
        self.current_data_set_row_number = 0

    def data_step(self):
        self.current_data_set_row_number += 1

    def data_stop(self):
        self.current_data_set_name = ""

    def formulator(self, formula):
        formula = formula[0][1:-1]
        if self.use_prevrowdata:
            data = self.prevrowdata
        else:
            data = self.data
        if formula in data:
            rez = str(data[formula])
        else:
            rez = self.evaluator(formula)
        return html.escape(rez)

    def evaluator(self, formula):
        try:
            rez = str(eval(formula, self.mydata))
        except BaseException:
            rez = f"Evaluating error: {formula}"
        return rez

    def format(self, cell):
        format = cell.get("format", "")
        dec = re_dec.sub("", format)
        if format == "D":
            try:
                cell["data"] = datetime.datetime.strptime(cell["data"], "%Y-%m-%d").strftime("%d.%m.%Y")
            except Exception:
                pass
        elif "F" in format.upper():
            cell["xlsx_data"] = num(cell["data"])
            cell["numFmtId"] = "165"
            if dec and dec != "":
                fmt = "{:,.%sf}" % int(dec)
            else:
                fmt = "{:,.2f}"
            cell["data"] = (fmt.format(num(cell["data"]))).replace(",", " ")
        elif "N" in format.upper():
            if dec and dec != "":
                fmt = "{:.%sf}" % int(dec)
                cell["data"] = (fmt.format(num(cell["data"]))).replace(",", " ")
            cell["xlsx_data"] = num(cell["data"])
            cell["numFmtId"] = "164"

        if format.startswith("$"):
            cell["data"] = self.currency + cell["data"]
        elif format.endswith("$"):
            cell["data"] += self.currency

    def render_rows_section(self, rows_section, column_style, aggregator=None):
        if aggregator is None:
            self.use_prevrowdata = False
            self.data.update({x: self.table_aggregators[x]["v"] for x in self.table_aggregators})
            self.data.update(self.params)
            if self.table_group_aggregators:
                self.data["_grow_number"] = self.table_group_aggregators[-1]["aggr"]["_grow_number"]["v"]
        else:
            self.prevrowdata.update({x: aggregator[x]["v"] for x in aggregator})
            self.prevrowdata.update(self.params)
            self.use_prevrowdata = True

        rows_section_style = dict(column_style)
        rows_section_style.update(rows_section.get("style", {}))
        rows_section = deepcopy(rows_section)
        # rows_section["style"] = rows_section_style
        for cell in rows_section["cells"]:
            cell_text = rows_section["cells"][cell].get("data")
            cell_style = dict(rows_section_style)
            cell_style.update(rows_section["cells"][cell].get("style", {}))
            rows_section["cells"][cell]["style"] = cell_style
            if cell_text:
                #  images
                cell_text, rows_section["cells"][cell]["images"] = self.extract_images(cell_text)
                #  text data
                rows_section["cells"][cell]["data"] = html.unescape(re_calc.sub(self.formulator, cell_text))
                if rows_section["cells"][cell].get("name"):
                    self.data[rows_section["cells"][cell].get("name")] = rows_section["cells"][cell]["data"]
                self.format(rows_section["cells"][cell])

        self.printer.render_rows_section(rows_section, rows_section_style, self.outline_level)

    def extract_images(self, cell_data):
        images_list = []

        def extract_image(formula):
            image_data = self.formulator(formula).split(":")
            if len(image_data) == 6:
                images_list.append(
                    {
                        "image": image_data[0],
                        "width": num(image_data[1]),
                        "height": num(image_data[2]),
                        "pixel_width": num(image_data[3]),
                        "pixel_height": num(image_data[4]),
                    }
                )
            return ""

        cell_data = re_q2image.sub(extract_image, cell_data)
        return cell_data, images_list

    def before_run_check(self):
        for page_index, page in enumerate(self.report_content.get("pages", [])):
            for columns_index, columns in enumerate(page.get("columns", [])):
                for row_index, rows_section in enumerate(columns.get("rows", [])):
                    if len(rows_section["cells"]) == 0:
                        continue
                    max_row = max(
                        [
                            int_(x.split(",")[0])
                            + (
                                int_(rows_section["cells"][x]["rowspan"]) - 1
                                if int_(rows_section["cells"][x].get("rowspan", 0))
                                else 0
                            )
                            for x in rows_section["cells"]
                        ]
                    )
                    max_col = max(
                        [
                            int_(x.split(",")[1])
                            + (
                                int_(rows_section["cells"][x]["colspan"]) - 1
                                if int_(rows_section["cells"][x].get("colspan", 0))
                                else 0
                            )
                            for x in rows_section["cells"]
                        ]
                    )
                    # extend cols
                    while max_col > len(columns["widths"]) - 1:
                        self.add_column(page_index, columns_index)
                    # extend rows
                    while max_row > len(rows_section["heights"]) - 1:
                        self.add_row(page_index, columns_index, rows_index=row_index)

    def run(self, output_file="temp/repo.html", output_type=None, data={}, open_output_file=True):
        if data:
            self.data_sets.update(data)
        self.before_run_check()
        self.printer: Q2Printer = get_printer(output_file, output_type)
        self.printer.q2report = self
        report_style = dict(self.report_content.get("style", self.default_style))

        pages = self.report_content.get("pages", [])
        for index, page in enumerate(pages):
            self.printer.reset_page(**{x: page[x] for x in page if x.startswith("page_")})

            page_style = dict(report_style)
            page_style.update(page.get("style", {}))

            for column in page.get("columns", []):
                if len(column["widths"]) == 0:
                    continue
                column_style = dict(page_style)
                column_style.update(column.get("style", {}))
                self.printer.reset_columns(column["widths"])

                for rows_section in column.get("rows", []):
                    data_set = self.data_sets.get(rows_section["data_source"], [])
                    if rows_section["role"] == "table":
                        if not data_set:
                            continue
                        # table rows
                        self.current_data_set_name = rows_section["data_source"]
                        self.aggregators_reset(rows_section)
                        # if hasattr(data_set, "len"):
                        self.data["_row_count"] = len(data_set)
                        self.render_table_header(rows_section, column_style)

                        # self.current_data_set += 1
                        self.data_start()
                        for data_row in data_set:
                            self.data["_row_number"] = self.current_data_set_row_number + 1
                            self.data.update(data_row)

                            self.render_table_groups(rows_section, column_style)
                            self.aggregators_calc()
                            self.outline_level += 1
                            self.render_rows_section(rows_section, column_style)
                            self.outline_level -= 1
                            self.prevrowdata.update(data_row)

                            if self.data_step():
                                break
                        self.data_stop()

                        self.render_table_groups(rows_section, column_style, True)
                        self.render_table_footer(rows_section, column_style)
                    else:  # Free rows
                        self.render_rows_section(rows_section, column_style)
        # print(json.dumps(self.report_content, indent=2))
        self.printer.save()
        if open_output_file:
            self.printer.show()
        return self.printer.output_file

    def render_table_header(self, rows_section, column_style):
        if rows_section.get("table_header"):
            self.render_rows_section(rows_section["table_header"], column_style)

    def render_table_groups(self, rows_section, column_style, end_of_table=False):
        reset_index = None
        for index, group_set in enumerate(rows_section["table_groups"]):
            agg = self.table_group_aggregators[index]
            group_value = []
            for group in agg["groupby_list"]:
                group_value.append(self.evaluator(group))
            if agg["groupby_values"] != group_value and agg["groupby_values"] != [] or end_of_table:
                reset_index = index
                break
        if reset_index is not None:
            for index in range(len(rows_section["table_groups"]) - 1, index - 1, -1):
                agg = self.table_group_aggregators[index]
                agg["aggr"]["_group_number"] = {"v": agg["_group_number"], "f": ""}
                self.render_rows_section(
                    rows_section["table_groups"][index]["group_footer"],
                    column_style,
                    aggregator=agg["aggr"],
                )
                self.outline_level -= 1
                # clear group aggregator
                agg["groupby_values"] = []
                agg["_group_number"] += 1
                for cell in agg["aggr"]:
                    agg["aggr"][cell]["v"] = num(0)
                agg["aggr"]["_grow_number"]["v"] = num(0)
        if end_of_table:
            return
        for index, group_set in enumerate(rows_section["table_groups"]):
            agg = self.table_group_aggregators[index]
            group_value = []
            for group in agg["groupby_list"]:
                group_value.append(self.evaluator(group))
            if agg["groupby_values"] != group_value:
                self.outline_level += 1
                self.data["_group_number"] = agg["_group_number"]
                self.render_rows_section(group_set["group_header"], column_style)

    def render_table_footer(self, rows_section, column_style):
        if rows_section.get("table_footer"):
            self.render_rows_section(rows_section["table_footer"], column_style)

    def aggregators_detect(self, rows_section, aggregator):
        if not rows_section:
            return
        formulas = []
        for cell_data in rows_section.get("cells").items():
            cell_data = cell_data[1].get("data", "")
            for x in re_calc.findall(cell_data):
                f = x[1:-1]
                if f not in formulas:
                    formulas.append(f)
        for cell_data in formulas:
            for mode in ["sum"]:
                if cell_data.lower().startswith(f"{mode}:"):
                    aggregator[cell_data] = {
                        "a": mode,  # aggregate function - sum, avg and etc
                        "f": cell_data[1 + len(mode) :],  # cell formula  # noqa: E203
                        "v": num(0),  # initial value
                    }

        aggregator["_grow_number"] = {
            "a": "sum",  # aggregate function - sum, avg and etc
            "f": "",  # cell formula
            "v": num(0),  # initial value
        }

    def aggregators_reset(self, rows_section):
        self.table_aggregators = {}
        self.table_group_aggregators = []
        self.aggregators_detect(rows_section.get("table_footer", {}), self.table_aggregators)
        grouper = []
        for group in rows_section["table_groups"]:
            grouper.append(group["group_footer"]["groupby"])
            aggr = {
                "groupby_list": grouper[:],
                "groupby_values": [],
                "_group_number": 1,
                "aggr": {},
            }
            self.aggregators_detect(group.get("group_footer", {}), aggr["aggr"])
            self.table_group_aggregators.append(aggr)

    def aggregators_calc(self):
        for y, x in self.table_aggregators.items():
            x["v"] += num(self.evaluator(x["f"]))

        for x in self.table_group_aggregators:
            x["groupby_values"] = []
            for y in x["groupby_list"]:
                x["groupby_values"].append(self.evaluator(y))
            for cell in x["aggr"]:
                x["aggr"][cell]["v"] += num(self.evaluator(x["aggr"][cell]["f"]))
            x["aggr"]["_grow_number"]["v"] += 1


class D:
    class R:
        def __init__(self, data_set, row_number=0):
            self.data_set = data_set
            self.row_number = row_number

        def __getattr__(self, atr):
            if atr in self.__dict__:
                return self.__dict__[atr]
            elif atr == "r":
                return self.getrow
            elif self.row_number < len(self.data_set) and atr in self.data_set[self.row_number]:
                return self.data_set[self.row_number][atr]
            return ""

        def getrow(self, row_number):
            if row_number >= 0 and row_number < len(self.data_set):
                self.row_number = row_number
            else:
                self.row_number = 0
            return self

    def __init__(self, q2report):
        self.q2report: Q2Report = q2report

    def __getattr__(self, atr):
        if atr in self.q2report.data_sets:
            return self.R(self.q2report.data_sets[atr])
        return None
