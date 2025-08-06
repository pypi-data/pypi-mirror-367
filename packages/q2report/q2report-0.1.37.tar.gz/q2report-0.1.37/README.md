# The light Python report builder.
Converts data into formatted text (**HTML**, **DOCX**, **XLSX**):
```python
data = {'data_source1':[{'col1': 'value row1', ....}, ...],
        'data_source2':[{'col_1': 'valie_row1', ....}, ...],
        }
```
Available formatting (styling options):
```json  
"style": {
    "font-family": "Arial",
    "font-size": "10pt",
    "font-weight": "normal",
    "border-width": "0 0 0 0",
    "padding": "0.05cm 0.05cm 0.05cm 0.05cm",
    "text-align": "left",
    "vertical-align": "top"
  }

```
## Concept
The report definition consists of sections (Report, Pages, Columns, Rows, Cells).  
Each section inherits style from previous and may override some styling options.  
*see examples in folder **test_data***
```python
Report:  # contains basic style
    Pages:  # page & margins sizes
        Columns:  # columns widths - exact, % or autowidth
            Rows:  # rows heights - auto, exact, min or max
                   # can be linked to data and then have header, footer and grouping subsections
                   # 
                Cells  # contains simple text and data links - {col1}
                       # and aggregate functions - {sum:coll}
                       # support html formatting with <b> <i> <u> <br>
                       # cells may be merged (span)
            Rows:
                Cells
            ....
        Columns:
            ....
    Pages:
        ....
    ....
```