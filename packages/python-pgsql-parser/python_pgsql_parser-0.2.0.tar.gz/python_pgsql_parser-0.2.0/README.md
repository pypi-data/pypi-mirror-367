# PostgreSQL SQL Parser

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI Version](https://img.shields.io/pypi/v/python-pgsql-parser.svg)](https://pypi.org/project/python-pgsql-parser/)

# SQLParser Project

## Overview
SQLParser is a Python library designed to parse and analyze SQL scripts, focusing on Data Definition Language (DDL) statements and SELECT queries. It processes SQL statements to extract structured information about tables, columns, constraints, and query elements, providing a robust foundation for database schema analysis and query processing.

## Features
- **DDL Parsing**: Supports parsing of `CREATE TABLE`, `ALTER TABLE`, and `CREATE INDEX` statements to extract table structures, columns, primary keys, foreign keys, and constraints.
- **SELECT Query Parsing**: Handles `SELECT` statements, including those with Common Table Expressions (CTEs), to identify query structure and column expressions.
- **Tokenization**: Utilizes an `AdvancedSQLLexer` to tokenize SQL scripts accurately.
- **Structured Output**: Represents parsed SQL components as structured objects (`Table`, `Column`, `PrimaryKey`, `ForeignKey`, `Constraint`, etc.).
- **Extensible Architecture**: Built with a modular design using a base parser class (`ParserBase`) for easy extension and maintenance.

## Source Installation
To use the SQLParser library, ensure you have Python 3.8+ installed. Clone the repository and install dependencies:

```bash
git clone https://github.com/devsunny/python-pgsql-parser.git
cd sqlparser
pip install -r requirements.txt
```

## Pip installation
```bash
pip install python-pgsql-parser

```
## Usage
The `AdvancedSQLParser` class is the main entry point for parsing SQL scripts. Below is an example of how to use it:

```python
from sqlparser import AdvancedSQLParser

# Example SQL script
sql_script = """
CREATE TABLE users (
    id INT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100),
    FOREIGN KEY (email) REFERENCES accounts(email)
);
SELECT username, email FROM users;
"""

# Initialize parser and parse the script
parser = AdvancedSQLParser(sql_script)

# Access parsed tables
tables = parser.get_tables()
for table_name, table in tables.items():
    print(f"Table: {table.name}")
    for col_name, column in table.columns.items():
        print(f"  Column: {col_name}, Type: {column.col_type}, Nullable: {column.nullable}")
    if table.primary_key:
        print(f"  Primary Key: {table.primary_key.columns}")
    for fk in table.foreign_keys:
        print(f"  Foreign Key: {fk.columns} -> {fk.ref_table}({fk.ref_columns})")
```

### Output
For the above SQL script, the parser will output structured information about the `users` table, its columns, primary key, foreign key, and the `SELECT` query components.

## Project Structure
- **sqlparser/models.py**: Defines data models (`Token`, `TokenType`, `Table`, `Column`, `PrimaryKey`, `ForeignKey`, `Constraint`, etc.) for representing SQL components.
- **sqlparser/sql_lexer.py**: Implements `AdvancedSQLLexer` for tokenizing SQL scripts.
- **sqlparser/parser_base.py**: Provides the base `ParserBase` class with utility methods for token consumption and parsing.
- **sqlparser/advanced_statement_analyzer.py**: Analyzes SQL statements and handles nested subqueries.
- **sqlparser/column_def_parser.py**: Parses column definitions, including data types, constraints, and foreign key references.
- **sqlparser/advanced_ddl_statement_parser.py**: Parses DDL statements (`CREATE TABLE`, `ALTER TABLE`, `CREATE INDEX`).
- **sqlparser/sql_query_parser.py**: Parses `SELECT` queries, including CTEs and column expressions.
- **sqlparser/advanced_sql_parser.py**: Main parser class that orchestrates the parsing process and maintains the table registry.

## Code Example
Below is a snippet from `column_def_parser.py` that demonstrates how column definitions are parsed:

<xaiArtifactCode>
from typing import List
from .models import Token, TokenType, Column, PrimaryKey, ForeignKey, Constraint
from .parser_base import ParserBase

class ColumnDefParser(ParserBase):
    def __init__(self, col_def: List[Token]):
        super().__init__(col_def)
        self.col_name = None
        self.col_type = None
        self.nullable = True
        self.default_value = None
        self.is_primary = False
        self.fk_ref = None
        self.max_char_length = None
        self.precision = 0
        self.scale = 0
        self.primary_key = None
        self.foreign_key = None
        self.constraint = None
        self.foreign_key_ref = None
        self._parse()

    def _parse_column_def(self):
        while self.current_pos < self.num_of_tokens:
            tok = self._consume_one()
            if self.col_name is None:
                self.col_name = tok.value
            elif self.col_type is None:
                self.col_type = tok.value.upper()
            elif tok.token_type == TokenType.OPEN_PAREN:
                self._parse_precision_scale()
                self._consume_one()  # consume close_paren
            elif self._is_keyword(tok, "NOT") and self._is_keyword(self._peek(), "NULL"):
                self.nullable = False
                self._consume_one()  # consume null
            # ... (additional parsing logic)
</xaiArtifactCode>

## Dependencies
- Python 3.8+
- `typing` (standard library)
- `collections.OrderedDict` (standard library)


## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues and feature requests, please [open an issue](https://github.com/yourusername/python-pgsql-parser/issues).