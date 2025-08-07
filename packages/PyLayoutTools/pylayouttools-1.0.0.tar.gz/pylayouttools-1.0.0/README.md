<img width="2100" alt="pylayouttools" src="https://github.com/user-attachments/assets/d3ec7f95-d69f-4a8f-be60-102e45c5144c" />

# PyLayoutTools (PLT)
Simple library for organising text into boxes and tables.

## Boxes
Wrap strings of text in a simple ASCII box. Define the max width to have the text automatically confine to any terminal width.

**Example Code**
```python
from PyLayoutTools import pltBox

box = pltBox(
  "This is a box.",
  "It holds a lot of text.",
  "If the text is wider than the maxwidth limit (default 80) it'll wrap the text.",
  "Neat, huh?")
box.maxwidth = 40

print(box())
```
<img width="400" alt="carbon" src="https://github.com/user-attachments/assets/1e2bdeaf-5edd-45fc-969e-da63b07f8992" />

## Tables
Collate data into a table, with headers.

**Example Code**
```python
from PyLayoutTools import pltTable

tbl = pltTable(["First Name", "Last Name", "Employee", "Salary"],
  ["Bart", "Simpson", "12345", "$4,500"], 
  ["John", "Smith", "12346", "$5,000"], 
  ["Steven", "Goldfish", "12347", "$5,000"],
  ["Paula", "Brown", "12348", "$3,500"],
  ["James", "Smith", "12349", "$4,500"])

print(tbl())
```
<img width="400" alt="carbon-2" src="https://github.com/user-attachments/assets/95ccc701-186f-4284-816e-3093d837d75c" />
